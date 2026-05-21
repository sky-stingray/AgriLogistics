import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from geopy.distance import geodesic
import datetime

from app_utils import INDIAN_CITIES, DEFAULT_DESTINATIONS, get_available_destinations, get_default_destinations

st.set_page_config(page_title="AgriLogistics VRPTW", layout="wide")

def calculate_distance_matrix(locations):
    """Calculates geodesic distance matrix in kilometers."""
    n = len(locations)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = geodesic(locations[i], locations[j]).kilometers
    return matrix

def calculate_time_matrix(distance_matrix, speed_kmh=60):
    """Calculates time matrix in minutes."""
    return (distance_matrix / speed_kmh) * 60

def solve_vrptw(data):
    """Solves the VRPTW problem."""
    manager = pywrapcp.RoutingIndexManager(
        len(data['time_matrix']), data['num_vehicles'], data['depot']
    )
    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(data['time_matrix'][from_node][to_node])

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    time = 'Time'
    routing.AddDimension(
        transit_callback_index,
        60 * 24,  # allow waiting time (1 day in minutes)
        60 * 24 * 7,  # maximum time per vehicle (7 days)
        False, 
        time)
    time_dimension = routing.GetDimensionOrDie(time)

    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == data['depot']:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(int(time_window[0]), int(time_window[1]))

    penalty = 1000000 
    for node in range(1, len(data['time_matrix'])):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.time_limit.seconds = 5 # Prevent UI freezing

    solution = routing.SolveWithParameters(search_parameters)
    return manager, routing, solution

# --- Streamlit UI ---
st.title("🌾 AgriLogistics: Perishable Routing Optimizer")
st.markdown("Optimize fleet routes across India while respecting crop perishability time windows.")

# --- Sidebar Controls ---
st.sidebar.header("1. Fleet & Speeds")
num_vehicles = st.sidebar.slider("Number of Vehicles", 1, 10, 3)
speed_kmh = st.sidebar.slider("Average Speed (km/h)", 30, 100, 60)

st.sidebar.header("2. Product Perishability")
st.sidebar.markdown("*Maximum transit time allowed in hours.*")
tomato_life = st.sidebar.number_input("Tomato (Fast)", 1, 48, 12)
potato_life = st.sidebar.number_input("Potato (Medium)", 12, 168, 72)
wheat_life = st.sidebar.number_input("Wheat (Slow)", 24, 720, 168)

crop_profiles = {
    "Tomato": tomato_life * 60, # convert to minutes
    "Potato": potato_life * 60,
    "Wheat": wheat_life * 60
}

# --- Location Selection ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("3. Select Locations")
    depot_city = st.selectbox("Select Source (Depot)", list(INDIAN_CITIES.keys()), index=0)
    
    available_destinations = get_available_destinations(depot_city)
    destinations = st.multiselect(
        "Select Destinations", 
        available_destinations,
        default=get_default_destinations(depot_city)
    )
    
    st.subheader("4. Assign Crops to Destinations")
    destination_crops = {}
    for dest in destinations:
        destination_crops[dest] = st.selectbox(f"Crop for {dest}", ["Tomato", "Potato", "Wheat"], key=dest)

with col2:
    if not destinations:
        st.warning("Please select at least one destination.")
        st.stop()
        
    # --- Data Preparation ---
    all_nodes = [depot_city] + destinations
    coordinates = [INDIAN_CITIES[node] for node in all_nodes]
    
    dist_matrix = calculate_distance_matrix(coordinates)
    time_matrix = calculate_time_matrix(dist_matrix, speed_kmh)
    
    # Define time windows (in minutes)
    # Depot has [0, max_time]
    time_windows = [(0, 60 * 24 * 7)] 
    for dest in destinations:
        crop_type = destination_crops[dest]
        max_time_allowed = crop_profiles[crop_type]
        time_windows.append((0, max_time_allowed))
        
    data = {
        'time_matrix': time_matrix,
        'time_windows': time_windows,
        'num_vehicles': num_vehicles,
        'depot': 0
    }
    
    # --- Solve ---
    with st.spinner("Optimizing routes..."):
        manager, routing, solution = solve_vrptw(data)
        
    if not solution:
        st.error("No solution found at all. The parameters are fundamentally impossible.")
    else:
        # Extract Routes and Dropped Nodes
        routes = []
        dropped_nodes = []
        
        # Check dropped nodes
        for node in range(routing.Size()):
            if routing.IsStart(node) or routing.IsEnd(node):
                continue
            if solution.Value(routing.NextVar(node)) == node:
                dropped_nodes.append(manager.IndexToNode(node))
                
        time_dimension = routing.GetDimensionOrDie('Time')
        
        # Extract vehicle routes
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                time_var = time_dimension.CumulVar(index)
                node_idx = manager.IndexToNode(index)
                route.append({
                    "location": all_nodes[node_idx],
                    "arrival_time_min": solution.Min(time_var)
                })
                index = solution.Value(routing.NextVar(index))
            node_idx = manager.IndexToNode(index)
            time_var = time_dimension.CumulVar(index)
            route.append({
                "location": all_nodes[node_idx],
                "arrival_time_min": solution.Min(time_var)
            })
            if len(route) > 2: # Only save active routes
                routes.append(route)
                
        # --- UI Feedback ---
        if dropped_nodes:
            st.error("🚨 Infeasible Route Detected!")
            st.write("Some locations could not be reached before the crops perished. Dropped deliveries:")
            for node_idx in dropped_nodes:
                failed_city = all_nodes[node_idx]
                failed_crop = destination_crops[failed_city]
                req_time = crop_profiles[failed_crop] / 60
                st.write(f"- **{failed_city}** ({failed_crop} expires in {req_time}h)")
                
            st.info("""
            **How to fix this (Minimum Changes Needed):**
            1. **Increase Fleet Size:** Add more vehicles from the sidebar to distribute the load.
            2. **Increase Speed:** Faster trucks mean wider geographic reach.
            3. **Adjust Perishability:** Increase the shelf life of the failed crops if possible.
            """)
        else:
            st.success("✅ All locations routed successfully within perishability constraints!")

        # --- Mapping ---
        m = folium.Map(location=[22.0, 79.0], zoom_start=5)
        
        # Depot marker
        folium.Marker(
            INDIAN_CITIES[depot_city], 
            popup=f"Source: {depot_city}", 
            icon=folium.Icon(color='black', icon='home')
        ).add_to(m)
        
        colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue']
        
        for idx, route in enumerate(routes):
            route_coords = [INDIAN_CITIES[stop['location']] for stop in route]
            color = colors[idx % len(colors)]
            
            # Draw Route Line
            folium.PolyLine(route_coords, color=color, weight=3, opacity=0.8).add_to(m)
            
            # Draw Destination Markers
            for stop in route[1:-1]: # Skip depot
                city = stop['location']
                crop = destination_crops[city]
                arrival_h = round(stop['arrival_time_min'] / 60, 1)
                folium.Marker(
                    INDIAN_CITIES[city],
                    popup=f"{city}<br>Crop: {crop}<br>Arrival: {arrival_h} hrs",
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(m)
                
        for node_idx in dropped_nodes:
            city = all_nodes[node_idx]
            folium.Marker(
                INDIAN_CITIES[city],
                popup=f"FAILED: {city}",
                icon=folium.Icon(color='red', icon='remove-circle')
            ).add_to(m)
            
        st_folium(m, width=800, height=500)
        
        # --- Route Itineraries ---
        if routes:
            st.subheader("Route Itineraries")
            for idx, route in enumerate(routes):
                with st.expander(f"Truck {idx + 1}"):
                    for step in route:
                        hours = round(step['arrival_time_min'] / 60, 2)
                        st.write(f"→ **{step['location']}** (Arrival: {hours} hours)")