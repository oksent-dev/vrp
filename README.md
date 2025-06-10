# Vehicle Routing Problem (VRP) with Multiple Warehouses, Pickups, and Goods Types

This project is a university assignment implementing a complex Vehicle Routing Problem (VRP) using a genetic algorithm. The solution supports multiple warehouses, heterogeneous vehicles, delivery and pickup points, and multiple goods categories.

## Features

- **Map Representation:** Points (warehouses, deliveries, pickups) are scattered on a 2D map with coordinates in the range (0, 100).
- **Distance Calculation:** All distances are calculated using Euclidean distance (in kilometers).
- **Warehouses:** Five warehouses are placed on the map. Each has unlimited capacity for storing goods.
- **Vehicles:** Three types of vehicles:
  - Custom capacity
  - Each vehicle starts at a randomly assigned warehouse.
- **Service Points:**
  - Some points require goods to be delivered, others require goods to be picked up.
  - Each point's demand (or pickup) is randomly generated between 100 kg and 200 kg.
  - Goods picked up can be delivered to other points or returned to a warehouse.
- **Goods Types:** There are three categories of goods: oranges, uranium, and tuna. Each point's demand is split among these categories, but the total per point is always between 100 kg and 200 kg.
- **Optimization Goal:** Find the shortest (or nearly shortest) set of routes that allows all deliveries and pickups to be completed, respecting vehicle capacities and goods types.

## How It Works

1. **Initialization:**

   - Five warehouses are generated at fixed positions.
   - Delivery and pickup points are generated with random coordinates and demands (split among oranges, uranium, and tuna).
   - Vehicles are initialized with different capacities and assigned to warehouses.

2. **Genetic Algorithm:**

   - The algorithm searches for an optimal or near-optimal set of routes for all vehicles, ensuring all demands and pickups are satisfied and vehicle capacities are not exceeded.

3. **Output:**
   - The resulting routes are saved to a text file (`output/routes.txt`).
   - A visualization of the routes is saved as an image (`output/routes.png`).

## Usage

1. **Requirements:**

   - Python 3.10+
   - `matplotlib` for plotting (install with `pip install matplotlib` if not present)

2. **Run the Project:**

   ```powershell
   python main.py
   ```

3. **Output Files:**
   - `output/routes.txt`: Textual description of the routes.
   - `output/routes.png`: Visualization of the routes on the map.

## Grading Requirements Coverage

- **Satisfactory:** Single warehouse, random delivery points, vehicle capacities, Euclidean distances, all vehicles start at warehouse, random demands.
- **Good:** Five warehouses, random vehicle starting locations, both deliveries and pickups, goods can be returned to warehouses, three vehicle types.
- **Very Good:** Three goods categories (oranges, uranium, tuna), per-point demand split among goods, all other requirements above.

# License

This project is for educational purposes.
