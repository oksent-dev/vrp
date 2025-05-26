def save_routes(vehicles: list, filename: str = "output/routes.txt") -> None:
    """Saves the delivery routes to a text file."""
    total_sum = 0.0
    with open(filename, "w") as f:
        f.write("=== VEHICLE ROUTING PROBLEM  ===\n")
        f.write(f"Number of vehicles: {len(vehicles)}\n")

        for vehicle in vehicles:
            f.write(f"\n{'='*60}\n")
            f.write(f"Vehicle {vehicle.id} (Capacity: {vehicle.capacity}kg)\n")
            if hasattr(vehicle, "assigned_warehouse") and vehicle.assigned_warehouse:
                f.write(f"Assigned Warehouse: {vehicle.assigned_warehouse.label}\n")
            f.write(f"{'='*60}\n")

            vehicle_distance = 0.0

            for i in range(len(vehicle.route) - 1):
                from_point = vehicle.route[i]["point"]
                to_point = vehicle.route[i + 1]["point"]
                vehicle_distance += from_point.distance_to(to_point)

            for j, stop in enumerate(vehicle.route):
                point = stop["point"]
                if stop["is_warehouse"]:
                    operation = stop.get("operation_type", "warehouse")
                    remaining_load = stop.get("remaining_load", 0)

                    if operation == "initial_load":
                        f.write(
                            f"Stop {j+1}: {point.label} | Initial load: {remaining_load}kg\n"
                        )
                    elif operation == "reload":
                        f.write(
                            f"Stop {j+1}: {point.label} | Reloaded to: {vehicle.capacity}kg\n"
                        )
                    elif operation == "unload":
                        f.write(f"Stop {j+1}: {point.label} | Unloaded to: 0kg\n")
                    else:
                        f.write(
                            f"Stop {j+1}: {point.label} | Load: {remaining_load}kg\n"
                        )
                else:
                    operation = stop.get("operation_type", "delivery")
                    amount = stop.get("amount", 0)
                    remaining_demand = stop.get("remaining_demand", 0)
                    remaining_load = stop.get("remaining_load", 0)

                    if operation == "delivery":
                        remaining_demand -= amount
                        remaining_load -= amount
                        f.write(
                            f"Stop {j+1}: [Delivery] {point.label} | "
                            f"Delivered: {amount}kg | "
                            f"Remaining demand: {remaining_demand}kg | "
                            f"Vehicle load after delivery: {remaining_load}kg\n"
                        )
                    elif operation == "pickup":
                        remaining_demand += amount
                        remaining_load += amount
                        f.write(
                            f"Stop {j+1}: [Pickup] {point.label} | "
                            f"Picked up: {amount}kg | "
                            f"Remaining pickup: {abs(remaining_demand)}kg | "
                            f"Vehicle load after pickup: {remaining_load}kg\n"
                        )
                    else:
                        f.write(
                            f"Stop {j+1}: {point.label} | "
                            f"Amount: {amount}kg | "
                            f"Vehicle load: {remaining_load}kg\n"
                        )

            f.write(
                f"\nVehicle {vehicle.id} Total Distance: {vehicle_distance:.2f} km\n"
            )
            total_sum += vehicle_distance

        f.write(f"\n{'='*60}\n")
        f.write(f"GRAND TOTAL DISTANCE: {total_sum:.2f} km\n")
        f.write(f"{'='*60}\n")
