class Point:
    """
    Class representing a delivery or pickup point.

    Attributes:
    - x (int): x-coordinate of the point.
    - y (int): y-coordinate of the point.
    - demands (dict): demands for each good type (e.g., {'oranges': 50, 'uranium': -30}).
                      Positive for delivery, negative for pickup.
    - remaining_demands (dict): remaining demands for each good type.
    - label (str): label of the point
    - is_warehouse (bool): indicates if this point is a warehouse
    - point_type (str): 'delivery', 'pickup', or 'warehouse'
    """

    GOOD_TYPES = ["oranges", "uranium", "tuna"]

    def __init__(
        self,
        x: int,
        y: int,
        demands: dict = None,  # Changed from demand: int
        label: str = None,
        is_warehouse: bool = False,
        point_type: str = None,
    ) -> None:
        self.x = x
        self.y = y
        # Ensure demands is a dict, defaulting to zero for all good types if None
        self.demands = (
            demands if demands is not None else {good: 0 for good in Point.GOOD_TYPES}
        )
        self.remaining_demands = self.demands.copy()
        self.label = label
        self.is_warehouse = is_warehouse

        if is_warehouse:
            self.point_type = "warehouse"
        elif point_type:
            self.point_type = point_type
        else:
            # Determine point_type based on the sum of demands
            total_demand_value = sum(self.demands.values())
            if total_demand_value > 0:
                self.point_type = "delivery"
            elif total_demand_value < 0:
                self.point_type = "pickup"
            else:  # Could be a transit point or uninitialized, default to delivery for safety
                self.point_type = "delivery"

    @property
    def total_demand(self) -> int:
        """Returns the sum of absolute values of initial demands for all goods."""
        return sum(abs(d) for d in self.demands.values())

    @property
    def total_remaining_demand_value(self) -> int:
        """Returns the sum of current remaining demands (can be negative for pickups)."""
        return sum(self.remaining_demands.values())

    def deliver(self, amounts: dict) -> dict:
        """Delivers specified amounts of goods to the point."""
        for good, amount in amounts.items():
            if good in self.remaining_demands:
                self.remaining_demands[good] -= amount
        return self.remaining_demands

    def pickup(self, amounts: dict) -> dict:
        """Picks up specified amounts of goods from the point.
        Internal remaining_demands for pickups are negative, so we add positive pickup amount.
        """
        for good, amount in amounts.items():
            if good in self.remaining_demands:
                # E.g., remaining_demand = -10 (need to pick up 10). Pickup 5. New remaining = -5.
                self.remaining_demands[good] += amount
        return self.remaining_demands

    def process_amount(self, amounts: dict) -> dict:
        """Processes delivery or pickup based on point type and amounts.
        Amounts should be positive for what is being transferred.
        """
        if self.point_type == "delivery":
            return self.deliver(amounts)
        elif self.point_type == "pickup":
            # For pickup, the 'amounts' represent what the vehicle takes.
            # These are positive values.
            return self.pickup(amounts)
        return self.remaining_demands

    def distance_to(self, other: "Point") -> float:
        """Calculates the Euclidean distance to another point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class Vehicle:
    """
    Class representing a vehicle.

    Attributes:
    - id (int): vehicle ID.
    - capacity (int): maximum total weight capacity of the vehicle.
    - current_loads (dict): current loads of each good type (e.g., {'oranges': 100}).
    - route (list): list of stops the vehicle makes.
    - assigned_warehouse (Point): The warehouse this vehicle starts from.
    """

    GOOD_TYPES = ["oranges", "uranium", "tuna"]

    def __init__(
        self, capacity: int, vehicle_id: int, assigned_warehouse: Point = None
    ) -> None:
        self.id = vehicle_id
        self.capacity = capacity
        self.current_loads = {good: 0 for good in Vehicle.GOOD_TYPES}  # Changed
        self.route = []
        self.assigned_warehouse = assigned_warehouse

    @property
    def current_total_load(self) -> int:
        """Calculates the current total load of the vehicle."""
        return sum(self.current_loads.values())

    def reset(self) -> None:
        """Resets load and route of the vehicle."""
        self.current_loads = {good: 0 for good in Vehicle.GOOD_TYPES}
        self.route = []

    def reload(self, specific_goods: dict = None) -> dict:
        """Reloads the vehicle.
        If specific_goods is provided, attempts to load them up to capacity.
        Otherwise, this method might need more sophisticated logic based on strategy,
        for now, it's a placeholder or clears and then loads specific goods.
        A full generic reload to capacity with mixed goods is complex without knowing
        what to prioritize.
        For now, let's assume reload means it can take specific goods from a warehouse.
        If specific_goods is None, it implies it unloads everything and then loads
        what's specified, or simply sets load if it's an initial load.
        """
        # This method is tricky. A simple "fill to capacity" is not well-defined with multiple goods.
        # Let's assume for now that reload is called when specific goods are to be loaded.
        # Or, if called from a warehouse stop, it might mean "prepare for next deliveries".
        # The solver will likely manage specific loading amounts.
        # For a simple interpretation, let's say it can load specific goods up to capacity.
        if specific_goods:
            for good, amount in specific_goods.items():
                if self.current_total_load + amount <= self.capacity:
                    self.current_loads[good] += amount
                else:
                    # Ran out of capacity, load partially or stop
                    can_add = self.capacity - self.current_total_load
                    self.current_loads[good] += can_add
                    break  # No more capacity
        # If no specific goods, what does reload mean?
        # For now, let's assume it's used by the solver which will specify amounts.
        return self.current_loads

    def add_stop(
        self,
        point: Point,
        amounts: dict = None,  # Changed from amount: int
        is_warehouse: bool = False,
        operation_type: str = "delivery",  # e.g., "delivery", "pickup", "initial_load", "reload", "unload"
    ) -> None:
        """Adds a stop to the vehicle's route."""
        if amounts is None:
            amounts = {good: 0 for good in Vehicle.GOOD_TYPES}

        stop_info = {
            "point": point,
            "amounts": amounts.copy(),  # Store the actual amounts transferred for this stop
            "operation_type": operation_type,
            "vehicle_load_after_op": self.current_loads.copy(),  # Load before this op for consistency
            "remaining_demand_at_point": (
                point.remaining_demands.copy() if not is_warehouse else None
            ),
            "is_warehouse": is_warehouse,
        }

        # Update vehicle load based on operation.
        # For "initial_load" and "reload", current_loads has already been updated
        # by vehicle.partial_load() or vehicle.reload() respectively,
        # which are called by the solver *before* add_stop.
        # Thus, no further modification to self.current_loads is needed here for those types.

        if not is_warehouse:  # Operations at customer points
            if operation_type == "delivery":
                for good, amount in amounts.items():
                    self.current_loads[good] -= amount
            elif operation_type == "pickup":
                for good, amount in amounts.items():
                    self.current_loads[good] += amount
        # For warehouse operations:
        elif operation_type == "unload":  # e.g., unloading everything at a warehouse
            # This assumes "unload" means emptying the vehicle at a warehouse.
            self.current_loads = {good: 0 for good in Vehicle.GOOD_TYPES}
        # No 'elif' for "initial_load" or "reload" here, as self.current_loads is already correct.
        # The previous block causing double counting was:
        # elif operation_type == "initial_load" or operation_type == "reload":
        #     for good, amount in amounts.items():
        #         self.current_loads[good] += amount

        # Update stop_info to reflect vehicle load *after* any operation at this stop.
        # For "initial_load" / "reload", this will be the load set by partial_load() / reload().
        # For "delivery" / "pickup", this will be the load after delivering/picking up items.
        # For "unload", this will be the zeroed-out load.
        stop_info["vehicle_load_after_op"] = self.current_loads.copy()
        self.route.append(stop_info)

    def can_pickup(self, amounts_to_pickup: dict) -> bool:
        """Checks if vehicle can pickup the specified amounts of goods."""
        total_pickup_weight = sum(amounts_to_pickup.values())
        return self.current_total_load + total_pickup_weight <= self.capacity

    def can_deliver(self, amounts_to_deliver: dict) -> bool:
        """Checks if vehicle can deliver the specified amounts of goods."""
        for good, amount in amounts_to_deliver.items():
            if self.current_loads.get(good, 0) < amount:
                return False
        return True  # If all goods are available in sufficient quantity

    def partial_load(self, amounts_to_load: dict) -> dict:
        """Loads specific amounts of goods, respecting capacity.
        Returns the amounts actually loaded.
        """
        actually_loaded = {good: 0 for good in Vehicle.GOOD_TYPES}
        for good, amount in amounts_to_load.items():
            available_capacity = self.capacity - self.current_total_load
            load_this_good = min(amount, available_capacity)

            if load_this_good <= 0:  # No capacity left or no amount to load
                break

            self.current_loads[good] += load_this_good
            actually_loaded[good] = load_this_good

            if self.current_total_load >= self.capacity:  # Exactly full
                break
        return actually_loaded

    def find_nearest_warehouse(self, warehouses: list["Point"]) -> "Point":
        """Finds the nearest warehouse to the vehicle's current location."""
        if not warehouses:
            return None  # Or raise an error

        current_position = (
            self.route[-1]["point"] if self.route else self.assigned_warehouse
        )
        if (
            not current_position
        ):  # Should not happen if assigned_warehouse is guaranteed
            return None

        nearest_warehouse = min(
            warehouses, key=lambda w: current_position.distance_to(w)
        )
        return nearest_warehouse
