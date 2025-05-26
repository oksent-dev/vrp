import matplotlib.pyplot as plt


def plot_routes(vehicles: list, points: list) -> None:
    """Visualizes vehicle routes on a map."""
    for i, vehicle in enumerate(vehicles):
        x_coords = [stop["point"].x for stop in vehicle.route]
        y_coords = [stop["point"].y for stop in vehicle.route]
        plt.plot(x_coords, y_coords, marker="o", label=f"Vehicle {i+1}")

    plt.scatter(
        [p.x for p in points], [p.y for p in points], c="k", marker="x", label="Points"
    )
    plt.gca().add_artist(
        plt.Circle((points[0].x, points[0].y), 2, color="r", fill=False)
    )
    plt.scatter(points[0].x, points[0].y, c="r", marker="s", label="Warehouse")
    plt.legend()
    plt.show()
