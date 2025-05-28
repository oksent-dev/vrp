import random
from lib.data_structures import Vehicle, Point


class GeneticAlgorithmVRP:
    """
    Genetic algorithm for solving the vehicle routing problem with multiple warehouses,
    supporting both pickup and delivery operations.

    attributes:
        points (list): List of all points including warehouses and service points.
        vehicles_capacities (list): List of capacities for each vehicle.
        warehouses (list): List of warehouse points.
        population_size (int): Size of the population for the genetic algorithm.
        generations (int): Number of generations to run the algorithm.
        mutation_rate (float): Probability of mutation in the genetic algorithm.
        tournament_size (int): Size of the tournament for selection in the genetic algorithm.

    """

    def __init__(
        self,
        points: list,
        vehicles_capacities: list,
        warehouses: list = None,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.2,
        tournament_size: int = 3,
    ) -> None:
        if warehouses is None:
            self.warehouses = [points[0]]
            self.service_points = points[1:]
        else:
            self.warehouses = warehouses
            warehouse_set = set(warehouses)
            self.service_points = [p for p in points if p not in warehouse_set]

        self.delivery_points = [
            p for p in self.service_points if p.point_type == "delivery"
        ]
        self.pickup_points = [
            p for p in self.service_points if p.point_type == "pickup"
        ]

        self.vehicles_capacities = vehicles_capacities
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size

    def create_individual(self) -> list:
        """Creates a random individual representing the order of service points."""
        return random.sample(self.service_points, len(self.service_points))

    def _calculate_initial_load(self, vehicle: Vehicle, individual: list) -> dict:
        """Calculate optimal initial load for each good based on route analysis."""

        initial_loads = {good: 0 for good in Vehicle.GOOD_TYPES}
        capacity_per_good_type = (
            (vehicle.capacity // 4) // len(Vehicle.GOOD_TYPES)
            if len(Vehicle.GOOD_TYPES) > 0
            else 0
        )
        if capacity_per_good_type == 0:
            return initial_loads

        for good in Vehicle.GOOD_TYPES:
            initial_loads[good] = capacity_per_good_type

        current_total = sum(initial_loads.values())

        return initial_loads

    def calculate_service_plan(self, individual: list) -> list:
        """Calculates the service plan for pickup and delivery operations for multiple goods."""
        for p in self.service_points:
            p.remaining_demands = p.demands.copy()

        vehicles = []
        for i, capacity in enumerate(self.vehicles_capacities):
            assigned_warehouse = random.choice(self.warehouses)
            vehicle = Vehicle(capacity, i + 1, assigned_warehouse)
            vehicles.append(vehicle)

        for vehicle in vehicles:
            vehicle.reset()
            initial_load_amounts = self._calculate_initial_load(vehicle, individual)
            vehicle.partial_load(initial_load_amounts)
            vehicle.add_stop(
                vehicle.assigned_warehouse,
                amounts=initial_load_amounts,
                is_warehouse=True,
                operation_type="initial_load",
            )

        for point in individual:
            if point.point_type == "delivery":
                self._handle_delivery(vehicles, point)
            elif point.point_type == "pickup":
                self._handle_pickup(vehicles, point)

        return vehicles

    def _handle_delivery(self, vehicles: list, point: Point) -> None:
        """Handles delivery operations for a specific point with multiple goods."""
        for good_type, demand_amount in point.remaining_demands.items():
            if demand_amount <= 0:
                continue

            needed_amount_for_good = demand_amount
            while needed_amount_for_good > 0:
                vehicle = self._select_vehicle_for_delivery(
                    vehicles, point, good_type, needed_amount_for_good
                )
                if not vehicle:
                    break

                if vehicle.current_loads.get(good_type, 0) == 0:
                    nearest_warehouse = vehicle.find_nearest_warehouse(self.warehouses)
                    if vehicle.route[-1]["point"] != nearest_warehouse:
                        vehicle.add_stop(
                            nearest_warehouse,
                            is_warehouse=True,
                            operation_type="travel_to_reload",
                        )
                    amount_to_reload = {
                        good_type: min(
                            needed_amount_for_good,
                            vehicle.capacity
                            - vehicle.current_total_load
                            + vehicle.current_loads.get(good_type, 0),
                        )
                    }
                    vehicle.reload(amount_to_reload)
                    vehicle.add_stop(
                        nearest_warehouse,
                        amounts=amount_to_reload,
                        is_warehouse=True,
                        operation_type="reload_specific_good",
                    )

                can_deliver_for_good = min(
                    vehicle.current_loads.get(good_type, 0), needed_amount_for_good
                )

                if can_deliver_for_good > 0:
                    delivery_amounts = {good_type: can_deliver_for_good}
                    vehicle.add_stop(
                        point, amounts=delivery_amounts, operation_type="delivery"
                    )
                    point.deliver(delivery_amounts)
                    needed_amount_for_good -= can_deliver_for_good
                else:
                    break

    def _handle_pickup(self, vehicles: list, point: Point) -> None:
        """Handles pickup operations for a specific point with multiple goods."""
        for good_type, demand_amount in point.remaining_demands.items():
            if demand_amount >= 0:
                continue

            needed_pickup_for_good = abs(demand_amount)
            while needed_pickup_for_good > 0:
                vehicle = self._select_vehicle_for_pickup(
                    vehicles, point, good_type, needed_pickup_for_good
                )
                if not vehicle:
                    break

                available_capacity_for_good = (
                    vehicle.capacity - vehicle.current_total_load
                )
                can_pickup_for_good = min(
                    available_capacity_for_good, needed_pickup_for_good
                )

                if can_pickup_for_good > 0:
                    pickup_amounts = {good_type: can_pickup_for_good}
                    vehicle.add_stop(
                        point, amounts=pickup_amounts, operation_type="pickup"
                    )
                    point.pickup(pickup_amounts)
                    needed_pickup_for_good -= can_pickup_for_good

                    if vehicle.current_total_load >= vehicle.capacity * 0.8:
                        nearest_warehouse = vehicle.find_nearest_warehouse(
                            self.warehouses
                        )
                        vehicle.add_stop(
                            nearest_warehouse,
                            is_warehouse=True,
                            operation_type="unload_if_full",
                        )
                        vehicle.current_loads = {g: 0 for g in Vehicle.GOOD_TYPES}
                else:
                    break

    def _select_vehicle_for_delivery(
        self, vehicles: list, point: Point, good_type: str, amount_needed: int
    ) -> Vehicle:
        best_vehicle = None
        min_cost = float("inf")

        for vehicle in vehicles:
            current_position = (
                vehicle.route[-1]["point"]
                if vehicle.route
                else vehicle.assigned_warehouse
            )

            current_load_of_good = vehicle.current_loads.get(good_type, 0)

            if current_load_of_good > 0:
                cost = current_position.distance_to(point)
                if cost < min_cost:
                    min_cost = cost
                    best_vehicle = vehicle

                elif cost == min_cost and best_vehicle is not None:
                    if (
                        current_load_of_good >= amount_needed
                        and best_vehicle.current_loads.get(good_type, 0) < amount_needed
                    ):
                        best_vehicle = vehicle
                    elif (
                        current_load_of_good
                        > best_vehicle.current_loads.get(good_type, 0)
                        and best_vehicle.current_loads.get(good_type, 0) < amount_needed
                    ):
                        best_vehicle = vehicle
            load_of_other_goods = vehicle.current_total_load - current_load_of_good
            if vehicle.capacity - load_of_other_goods >= amount_needed:
                nearest_warehouse = vehicle.find_nearest_warehouse(self.warehouses)
                if not nearest_warehouse:
                    continue

                cost_reload_trip = current_position.distance_to(
                    nearest_warehouse
                ) + nearest_warehouse.distance_to(point)

                if cost_reload_trip < min_cost:
                    min_cost = cost_reload_trip
                    best_vehicle = vehicle

        return best_vehicle

    def _select_vehicle_for_pickup(
        self, vehicles: list, point: Point, good_type: str, amount_to_pickup: int
    ) -> Vehicle:
        """Selects the best vehicle for picking up a specific good."""
        best_vehicle = None
        min_cost = float("inf")

        for vehicle in vehicles:
            if not vehicle.can_pickup({good_type: amount_to_pickup}):
                continue

            current_position = (
                vehicle.route[-1]["point"]
                if vehicle.route
                else vehicle.assigned_warehouse
            )
            cost_to_point = current_position.distance_to(point)

            if cost_to_point < min_cost:
                min_cost = cost_to_point
                best_vehicle = vehicle

        if best_vehicle is None:
            available_vehicles = [
                v for v in vehicles if (v.capacity - v.current_total_load) > 0
            ]
            if not available_vehicles:
                return None
            best_vehicle = min(
                available_vehicles,
                key=lambda v: (
                    v.route[-1]["point"] if v.route else v.assigned_warehouse
                ).distance_to(point),
            )

            if not vehicle.can_pickup({good_type: 1}):
                return None

        return best_vehicle

    def fitness(self, individual: list) -> float:
        """Calculates the total distance of the service plan."""
        if None in individual or len(individual) != len(self.service_points):
            return float("inf")

        try:
            vehicles = self.calculate_service_plan(individual)
            total_distance = 0

            for vehicle in vehicles:
                if not vehicle.route:
                    continue

                last_point = vehicle.assigned_warehouse
                for stop in vehicle.route:
                    current_point = stop["point"]
                    total_distance += last_point.distance_to(current_point)
                    last_point = current_point

                if vehicle.route:
                    final_warehouse = vehicle.find_nearest_warehouse(self.warehouses)
                    total_distance += last_point.distance_to(final_warehouse)

            return total_distance

        except Exception as e:
            return float("inf")

    def tournament_selection(self, population: list) -> list:
        """Selects individuals using tournament selection."""
        selected = []
        for _ in range(self.population_size):
            candidates = random.sample(population, self.tournament_size)
            winner = min(candidates, key=lambda x: self.fitness(x))
            selected.append(winner.copy())
        return selected

    def ordered_crossover(self, parent1: list, parent2: list) -> list:
        """Crossover operator that preserves the order of genes."""
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))

        child = [None] * size
        child[start : end + 1] = parent1[start : end + 1]

        segment_genes = set(child[start : end + 1])
        ptr_parent2 = 0

        for i in range(size):
            if child[i] is None:
                while ptr_parent2 < size and parent2[ptr_parent2] in segment_genes:
                    ptr_parent2 += 1
                if ptr_parent2 < size:
                    child[i] = parent2[ptr_parent2]
                    ptr_parent2 += 1

        return child

    def spatial_crossover(self, parent1: list, parent2: list) -> list:
        """Crossover operator that uses spatial information."""
        reference_point = random.choice(self.service_points)
        parent1_sorted = sorted(parent1, key=lambda p: p.distance_to(reference_point))
        parent2_sorted = sorted(parent2, key=lambda p: p.distance_to(reference_point))

        child = []
        used = set()

        i = j = 0
        while len(child) < len(parent1):
            while i < len(parent1_sorted) and parent1_sorted[i] in used:
                i += 1
            if i < len(parent1_sorted):
                child.append(parent1_sorted[i])
                used.add(parent1_sorted[i])
                i += 1

            while j < len(parent2_sorted) and parent2_sorted[j] in used:
                j += 1
            if j < len(parent2_sorted) and len(child) < len(parent1):
                child.append(parent2_sorted[j])
                used.add(parent2_sorted[j])
                j += 1

        return child

    def mutate(self, individual: list) -> list:
        """Mutates the individual by swapping two random genes."""
        if random.random() < self.mutation_rate:
            i, j = random.sample(range(len(individual)), 2)
            individual[i], individual[j] = individual[j], individual[i]
        return individual

    def optimize_route(self, route: list) -> list:
        """Optimizes the route using 2-opt algorithm."""
        if not route:
            return route

        nearest_warehouse = min(self.warehouses, key=lambda w: route[0].distance_to(w))
        full_route = route + [nearest_warehouse]

        improved = True
        while improved:
            improved = False
            best_distance = self.calculate_route_distance(full_route)

            for i in range(1, len(full_route) - 2):
                for j in range(i + 1, len(full_route) - 1):
                    new_route = (
                        full_route[:i]
                        + full_route[i : j + 1][::-1]
                        + full_route[j + 1 :]
                    )
                    new_distance = self.calculate_route_distance(new_route)

                    if new_distance < best_distance:
                        full_route = new_route
                        improved = True
                        best_distance = new_distance

        return full_route[:-1]

    def calculate_route_distance(self, route: list) -> float:
        """Calculates the total distance of the route."""
        if not route:
            return 0

        distance = 0
        nearest_warehouse = min(self.warehouses, key=lambda w: route[0].distance_to(w))
        last_point = nearest_warehouse

        for point in route:
            distance += last_point.distance_to(point)
            last_point = point
        return distance

    def run(self) -> list:
        """
        Runs the genetic algorithm.

        Returns a list of Vehicle objects representing the service routes.
        """
        population = [self.create_individual() for _ in range(self.population_size)]

        # Add random individuals every 5 generations for diversity
        for generation in range(self.generations):
            if generation % 5 == 0:
                population = population[:-10] + [
                    self.create_individual() for _ in range(10)
                ]

        for _ in range(self.generations):
            population = sorted(population, key=lambda x: self.fitness(x))
            elites = population[:2]

            selected = self.tournament_selection(population)
            next_generation = elites.copy()

            while len(next_generation) < self.population_size:
                parent1, parent2 = random.choices(selected, k=2)

                if random.random() < 0.7:
                    child = self.ordered_crossover(parent1, parent2)
                else:
                    child = self.spatial_crossover(parent1, parent2)

                child = self.mutate(child)

                # Local optimization for 20% of the population
                if random.random() < 0.2:
                    child = self.optimize_route(child)

                next_generation.append(child)

            population = next_generation[: self.population_size]

        best_solution = min(population, key=lambda x: self.fitness(x))
        return self.calculate_service_plan(best_solution)
