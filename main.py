from lib.data_structures import Point
from lib.solver import GeneticAlgorithmVRP
from lib.io import save_routes
from lib.plot import plot_routes
import random

GOOD_TYPES = ["oranges", "uranium", "tuna"]


def generate_demands_for_point(is_pickup: bool) -> dict:
    """Generates a dictionary of demands for multiple goods for a single point."""
    demands = {good: 0 for good in GOOD_TYPES}
    total_quantity = random.randint(100, 200)

    num_goods_for_point = random.randint(1, len(GOOD_TYPES))
    selected_goods = random.sample(GOOD_TYPES, num_goods_for_point)

    remaining_quantity = total_quantity
    for i, good in enumerate(selected_goods):
        if i == num_goods_for_point - 1:
            quantity = remaining_quantity
        else:
            max_possible_for_this_good = remaining_quantity - (
                num_goods_for_point - 1 - i
            )
            quantity = (
                random.randint(1, max_possible_for_this_good)
                if max_possible_for_this_good > 0
                else 0
            )

        demands[good] = -quantity if is_pickup else quantity
        remaining_quantity -= quantity
        if remaining_quantity <= 0 and i < num_goods_for_point - 1:
            break

    current_total_abs_demand = sum(abs(d) for d in demands.values())
    if current_total_abs_demand < total_quantity and selected_goods:
        diff = total_quantity - current_total_abs_demand
        last_good = selected_goods[-1]
        demands[last_good] += -diff if is_pickup else diff
    elif current_total_abs_demand > total_quantity and selected_goods:
        pass

    return demands


def generate_delivery_points(num_points: int) -> list:
    """
    Generates a list of delivery points with random coordinates and demands for multiple goods.
    """
    points = []
    for i in range(num_points):
        x = random.randint(10, 90)
        y = random.randint(10, 90)
        point_demands = generate_demands_for_point(is_pickup=False)
        points.append(
            Point(
                x,
                y,
                demands=point_demands,
                label=f"Delivery ({x},{y})",
                point_type="delivery",
            )
        )
    return points


def generate_pickup_points(num_points: int) -> list:
    """
    Generates a list of pickup points with random coordinates and pickup amounts for multiple goods.
    """
    points = []
    for i in range(num_points):
        x = random.randint(10, 90)
        y = random.randint(10, 90)
        point_demands = generate_demands_for_point(is_pickup=True)
        points.append(
            Point(
                x,
                y,
                demands=point_demands,
                label=f"Pickup ({x},{y})",
                point_type="pickup",
            )
        )
    return points


def generate_warehouses(warehouse_positions: list) -> list:
    """
    Generates a list of warehouse points at different locations.
    Warehouses have no initial demand for specific goods, they are sources/sinks.
    """
    warehouses = []

    for i in range(len(warehouse_positions)):
        x, y = warehouse_positions[i]
        warehouses.append(
            Point(
                x,
                y,
                demands=None,
                label=f"Warehouse {i+1} ({x},{y})",
                is_warehouse=True,
            )  # demands=None will default to 0 for all goods
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
