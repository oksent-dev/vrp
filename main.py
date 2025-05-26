from lib.data_structures import Point
from lib.solver import GeneticAlgorithmVRP
from lib.io import save_routes
from lib.plot import plot_routes
import random


def generate_points(num_points):
    """
    Generates a list of points with random coordinates and demands.
    """
    points = [Point(50, 50, label="Warehouse")]
    for _ in range(1, num_points + 1):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        points.append(
            Point(
                x,
                y,
                demand=random.randint(100, 200),
                label=f"Point ({x},{y})",
            )
        )
    return points


def main():
    random.seed(1)
    points = generate_points(30)
    ga = GeneticAlgorithmVRP(points, num_vehicles=4)
    vehicles = ga.run()
    save_routes(vehicles)
    plot_routes(vehicles, points)


if __name__ == "__main__":
    main()
