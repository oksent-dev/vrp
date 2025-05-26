class Point:
    """
    Class representing a delivery point.

    Attributes:
    - x (int): x-coordinate of the point.
    - y (int): y-coordinate of the point.
    - total_demand (int): total demand of the point.
    - remaining_demand (int): remaining demand of the point.
    - label (str): label of the point
    """

    def __init__(self, x: int, y: int, demand: int = 0, label: str = None) -> None:
        self.x = x
        self.y = y
        self.total_demand = demand
        self.remaining_demand = demand
        self.label = label

    def deliver(self, amount: int) -> int:
        """Delivers a certain amount of goods to the point."""
        self.remaining_demand -= amount
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
    - route (list): list of stops the vehicle makes.
    """

    def __init__(self, capacity: int, vehicle_id: int) -> None:
        self.id = vehicle_id
        self.capacity = capacity
        self.current_load = 0
        self.route = []

    def reset(self) -> None:
        """Resets load and route of the vehicle."""
        self.current_load = 0
        self.route = []

    def reload(self) -> int:
        """Reloads the vehicle to full capacity."""
        self.current_load = self.capacity
        return self.current_load

    def add_stop(
        self, point: Point, delivery_amount: int = 0, is_warehouse: bool = False
    ) -> None:
        """Adds a stop to the vehicle's route."""
        stop_info = {
            "point": point,
            "delivery": delivery_amount,
            "remaining_load": self.current_load,
            "remaining_demand": point.remaining_demand if not is_warehouse else None,
            "is_warehouse": is_warehouse,
        }
        self.route.append(stop_info)

        if not is_warehouse:
            self.current_load -= delivery_amount
