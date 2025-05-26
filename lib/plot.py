import matplotlib.pyplot as plt


def plot_routes(
    vehicles: list, points: list, output_file: str = "output/routes.png"
) -> None:
    """Visualizes vehicle routes on a map."""
    plt.figure(figsize=(12, 8))

    colors = ["blue", "green", "red", "orange", "purple", "brown", "pink", "gray"]
    for i, vehicle in enumerate(vehicles):
        if vehicle.route:
            x_coords = [stop["point"].x for stop in vehicle.route]
            y_coords = [stop["point"].y for stop in vehicle.route]
            color = colors[i % len(colors)]
            plt.plot(
                x_coords,
                y_coords,
                marker="o",
                color=color,
                label=f"Vehicle {vehicle.id} (Cap: {vehicle.capacity}kg)",
            )

    warehouses = [p for p in points if getattr(p, "is_warehouse", False)]
    delivery_points = [p for p in points if not getattr(p, "is_warehouse", False)]

    if delivery_points:
        plt.scatter(
            [p.x for p in delivery_points],
            [p.y for p in delivery_points],
            c="black",
            marker="x",
            s=50,
            label="Delivery Points",
            alpha=0.7,
        )

    if warehouses:
        plt.scatter(
            [w.x for w in warehouses],
            [w.y for w in warehouses],
            c="red",
            marker="s",
            s=100,
            label="Warehouses",
            alpha=0.8,
        )

        for warehouse in warehouses:
            plt.gca().add_artist(
                plt.Circle(
                    (warehouse.x, warehouse.y), 3, color="red", fill=False, alpha=0.5
                )
            )

    plt.title("Vehicle Routing Problem")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.show()
