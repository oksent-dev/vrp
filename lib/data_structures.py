class Point:
    """
    Class representing a delivery or pickup point.

    Attributes:
    - x (int): x-coordinate of the point.
    - y (int): y-coordinate of the point.
    - total_demand (int): total demand of the point (positive for delivery, negative for pickup).
    - remaining_demand (int): remaining demand of the point.
    - label (str): label of the point
    - is_warehouse (bool): indicates if this point is a warehouse
    - point_type (str): 'delivery', 'pickup', or 'warehouse'
    """

    def __init__(
        self,
        x: int,
        y: int,
        demand: int = 0,
        label: str = None,
        is_warehouse: bool = False,
        point_type: str = None,
    ) -> None:
        self.x = x
        self.y = y
        self.total_demand = demand
        self.remaining_demand = demand
        self.label = label
        self.is_warehouse = is_warehouse

        if is_warehouse:
            self.point_type = "warehouse"
        elif point_type:
            self.point_type = point_type
        elif demand > 0:
            self.point_type = "delivery"
        elif demand < 0:
            self.point_type = "pickup"

    def deliver(self, amount: int) -> int:
        """Delivers a certain amount of goods to the point."""
        self.remaining_demand -= amount
        return self.remaining_demand

    def pickup(self, amount: int) -> int:
        """Picks up a certain amount of goods from the point."""
        self.remaining_demand += amount
        return self.remaining_demand

    def process_amount(self, amount: int) -> int:
        """Processes delivery or pickup based on point type."""
        if self.point_type == "delivery":
            return self.deliver(amount)
        elif self.point_type == "pickup":
            return self.pickup(amount)
        return self.remaining_demand

    def distance_to(self, other: "Point") -> float:
        """Calculates the Euclidean distance to another point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class Vehicle:
    """
    Class representing a vehicle.

    Attributes:
    - id (int): vehicle ID.
    - capacity (int): maximum load capacity of the vehicle.
    - current_load (int): current load of the vehicle.
    - route (list): list of stops the vehicle makes."""

    def __init__(
        self, capacity: int, vehicle_id: int, assigned_warehouse: Point = None
    ) -> None:
        self.id = vehicle_id
        self.capacity = capacity
        self.current_load = 0
        self.route = []
        self.assigned_warehouse = assigned_warehouse

    def reset(self) -> None:
        """Resets load and route of the vehicle."""
        self.current_load = 0
        self.route = []

    def reload(self) -> int:
        """Reloads the vehicle to full capacity."""
        self.current_load = self.capacity
        return self.current_load

    def add_stop(
        self,
        point: Point,
        amount: int = 0,
        is_warehouse: bool = False,
        operation_type: str = "delivery",
    ) -> None:
        """Adds a stop to the vehicle's route."""
        stop_info = {
            "point": point,
            "amount": amount,
            "operation_type": operation_type,
            "remaining_load": self.current_load,
            "remaining_demand": point.remaining_demand if not is_warehouse else None,
            "is_warehouse": is_warehouse,
        }
        self.route.append(stop_info)

        if not is_warehouse:
            if operation_type == "delivery":
                self.current_load -= amount
            elif operation_type == "pickup":
                self.current_load += amount

    def can_pickup(self, amount: int) -> bool:
        """Checks if vehicle can pickup the specified amount."""
        return self.current_load + amount <= self.capacity

    def can_deliver(self, amount: int) -> bool:
        """Checks if vehicle can deliver the specified amount."""
        return self.current_load >= amount

    def partial_load(self, amount: int) -> int:
        """Loads a specific amount instead of full capacity."""
        if amount > self.capacity:
            amount = self.capacity
        self.current_load = amount
        return self.current_load

    def find_nearest_warehouse(self, warehouses: list) -> "Point":
        """Finds the nearest warehouse to the vehicle's current position."""
        if not self.route:
            return self.assigned_warehouse if self.assigned_warehouse else warehouses[0]

        current_position = self.route[-1]["point"]
        nearest_warehouse = min(
            warehouses, key=lambda w: current_position.distance_to(w)
        )
        return nearest_warehouse
