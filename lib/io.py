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
                operation = stop.get("operation_type", "unknown")
                amounts_at_stop = stop.get("amounts", {})
                vehicle_load_after_op = stop.get("vehicle_load_after_op", {})

                amounts_str_parts = []
                for good, amt in amounts_at_stop.items():
                    if amt != 0:
                        amounts_str_parts.append(f"{amt}kg {good}")
                amounts_display = (
                    ", ".join(amounts_str_parts) if amounts_str_parts else "(no goods)"
                )

                load_str_parts = []
                for good, load_val in vehicle_load_after_op.items():
                    if load_val > 0:  # Only show goods currently in load
                        load_str_parts.append(f"{load_val}kg {good}")
                load_display = ", ".join(load_str_parts) if load_str_parts else "empty"
                total_load_display = sum(vehicle_load_after_op.values())

                f.write(f"Stop {j+1}: {point.label} | Operation: {operation.upper()}\n")
                if amounts_at_stop and any(v != 0 for v in amounts_at_stop.values()):
                    f.write(f"  Action: {amounts_display}\n")

                if not point.is_warehouse:
                    remaining_demands_at_point = stop.get(
                        "remaining_demand_at_point", {}
                    )
                    demands_str_parts = []
                    for good, dem_val in remaining_demands_at_point.items():
                        if dem_val != 0:
                            dem_type = "to deliver" if dem_val > 0 else "to pickup"
                            demands_str_parts.append(
                                f"{abs(dem_val)}kg {good} {dem_type}"
                            )
                    demands_display = (
                        ", ".join(demands_str_parts)
                        if demands_str_parts
                        else "(all demands met)"
                    )
                    f.write(f"  Point Demands: {demands_display}\n")

                f.write(
                    f"  Vehicle Load After: {load_display} (Total: {total_load_display}kg)\n"
                )

            f.write(
                f"\nVehicle {vehicle.id} Total Distance: {vehicle_distance:.2f} km\n"
            )
            total_sum += vehicle_distance

        f.write(f"\n{'='*60}\n")
        f.write(f"GRAND TOTAL DISTANCE: {total_sum:.2f} km\n")
        f.write(f"{'='*60}\n")
