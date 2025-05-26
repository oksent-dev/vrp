def save_routes(vehicles: list, filename: str = "output/routes.txt") -> None:
    """Saves the delivery routes to a text file."""
    total_sum = 0.0
    with open(filename, "w") as f:
        for vehicle in vehicles:
            f.write(f"\nVehicle {vehicle.id} route:\n")
            vehicle_distance = 0.0

            for i in range(len(vehicle.route) - 1):
                from_point = vehicle.route[i]["point"]
                to_point = vehicle.route[i + 1]["point"]
                vehicle_distance += from_point.distance_to(to_point)

            for stop in vehicle.route:
                point = stop["point"]
                if stop["is_warehouse"]:
                    f.write(
                        f"Warehouse | Load: {vehicle.capacity}/{vehicle.capacity}\n"
                    )
                else:
                    f.write(
                        f"[Delivery] {point.label} | Delivered: {stop['delivery']}kg | "
                        f"Remaining demand: {stop['remaining_demand'] - stop['delivery']}kg | "
                        f"Vehicle load: {stop['remaining_load'] - stop['delivery']}kg\n"
                    )

            f.write(f"\nTotal distance: {vehicle_distance:.2f} km\n")
            total_sum += vehicle_distance

        f.write(f"\n\nGRAND TOTAL DISTANCE: {total_sum:.2f} km")
