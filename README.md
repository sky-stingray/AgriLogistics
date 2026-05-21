# 🌾 AgriLogistics: VRPTW Perishable Routing Optimizer

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-FF4B4B.svg)](https://streamlit.io/)
[![Google OR-Tools](https://img.shields.io/badge/OR--Tools-9.8.3296-1A73E8.svg)](https://developers.google.com/optimization)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)



By defining the "perishable rate" of different crops (like Tomatoes, Potatoes, and Wheat) as hard time-window constraints, this tool helps logistics managers optimize fleet routes across India ensuring produce reaches its destination before spoiling.

## ✨ Key Features

*   **Constraint-Based Optimization:** Leverages Google OR-Tools to solve complex routing problems with strict time windows.
*   **Perishability Profiling:** Dynamically assign shelf-life constraints based on crop type (e.g., fast-perishing tomatoes vs. slow-perishing wheat).
*   **Interactive Geographic Mapping:** Visualize routes, depots, and delivery nodes on an interactive map of India.
*   **Feasibility Detection:** Automatically detects when a route is geographically impossible given fleet size, speed, and crop perishability, offering actionable suggestions to fix the logistics breakdown.
*   **Reactive UI:** Built entirely in Python using Streamlit for an intuitive, fast, and accessible user experience.

## 🛠️ Tech Stack

*   **Frontend / UI:** [Streamlit](https://streamlit.io/)
*   **Routing Engine:** [Google OR-Tools](https://developers.google.com/optimization/routing/vrptw)
*   **Mapping:** [Folium](https://python-visualization.github.io/folium/) & `streamlit-folium`
*   **Geospatial Computation:** [Geopy](https://geopy.readthedocs.io/en/stable/) (Haversine/Geodesic distance calculation)
*   **Data Processing:** `pandas`, `numpy`

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need Python 3.8 or higher installed on your system.

### Installation

1. **Clone the repository**
  ```bash
  git clone [https://github.com/yourusername/agrilogistics-vrptw.git](https://github.com/yourusername/agrilogistics-vrptw.git)
  cd agrilogistics-vrptw
  ```

2. **Create a virtual environment (Recommended)**
  ```bash
  python -m venv venv

  # On macOS/Linux:
  source venv/bin/activate
  # On Windows:
  venv\Scripts\activate
  ```

3. **Install dependencies**
  ```bash
   pip install -r requirements.txt
  ```

### Running the App

Start the Streamlit server locally:

```bash
streamlit run app.py

```

The application will automatically open in your default web browser at `http://localhost:8501`.

## 📖 How to Use

1. **Configure Fleet:** Use the left sidebar to set the number of available trucks and their average speed.
2. **Set Perishability:** Adjust the maximum transit hours allowed for each crop type based on your current climate or refrigeration capabilities.
3. **Select Routing Nodes:** Choose a source city (Depot) and multiple destination cities.
4. **Assign Cargo:** Specify which crop needs to be delivered to which destination.
5. **Optimize:** The engine will automatically compute the optimal routes and draw them on the map. If a delivery cannot be made in time, check the error logs for minimum required changes.

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

To contribute:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

*Please ensure your code adheres to standard Python PEP 8 guidelines and include comments where necessary, especially when modifying the OR-Tools solver constraints.*

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

```