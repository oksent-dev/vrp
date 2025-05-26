from lib.data_structures import Point
from lib.solver import GeneticAlgorithmVRP
from lib.io import save_routes
from lib.plot import plot_routes
import random


def generate_delivery_points(num_points: int) -> list:
    """
    Generates a list of delivery points with random coordinates and demands.
    """
    points = []
    for i in range(num_points):
        x = random.randint(10, 90)
        y = random.randint(10, 90)
        demand = random.randint(100, 200)
        points.append(
            Point(
                x, y, demand=demand, label=f"Delivery ({x},{y})", point_type="delivery"
            )
        )
    return points


def generate_pickup_points(num_points: int) -> list:
    """
    Generates a list of pickup points with random coordinates and pickup amounts.
    """
    points = []
    for i in range(num_points):
        x = random.randint(10, 90)
        y = random.randint(10, 90)
        pickup_amount = random.randint(100, 200)
        points.append(
            Point(
                x,
                y,
                demand=-pickup_amount,
                label=f"Pickup ({x},{y})",
                point_type="pickup",
            )
        )
    return points


def generate_warehouses(warehouse_positions: list) -> list:
    """
    Generates a list of warehouse points at different locations.
    """
    warehouses = []
    warehouse_positions = [(10, 10), (90, 10), (10, 90), (90, 90), (50, 50)]

    for i in range(len(warehouse_positions)):
        x, y = warehouse_positions[i]
        warehouses.append(
            Point(x, y, demand=0, label=f"Warehouse {i+1} ({x},{y})", is_warehouse=True)
        )
    return warehouses


def main():
    random.seed(1)
    warehouse_positions = [(10, 10), (90, 10), (10, 90), (90, 90), (50, 50)]
    warehouses = generate_warehouses(warehouse_positions)
    print(f"Created {len(warehouses)} warehouses:")
    for warehouse in warehouses:
        print(f"  - {warehouse.label}")

    delivery_points = generate_delivery_points(20)
    pickup_points = generate_pickup_points(10)

    print(
        f"\nGenerated {len(delivery_points)} delivery points and {len(pickup_points)} pickup points"
    )

    all_service_points = delivery_points + pickup_points
    all_points = warehouses + all_service_points

    vehicles_capacities = [1000, 1500, 2000, 2000]

    print(
        f"\nUsing {len(vehicles_capacities)} vehicles with capacities: {vehicles_capacities}"
    )
    print("Optimizing routes for pickup and delivery operations...")

    ga = GeneticAlgorithmVRP(
        points=all_points,
        vehicles_capacities=vehicles_capacities,
        warehouses=warehouses,
    )
    vehicles = ga.run()

    save_routes(vehicles, "output/routes_pickup_delivery.txt")
    plot_routes(vehicles, all_points)

    print(f"\nResults saved to: output/routes_pickup_delivery.txt")


if __name__ == "__main__":
    main()
