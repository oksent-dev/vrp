import random
from lib.data_structures import Vehicle, Point


class GeneticAlgorithmVRP:
    """
    Genetic algorithm for solving the vehicle routing problem with multiple warehouses,
    supporting both pickup and delivery operations.
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

    def _calculate_initial_load(self, vehicle: Vehicle, individual: list) -> int:
        """Calculate optimal initial load based on route analysis."""
        total_deliveries = sum(p.total_demand for p in self.delivery_points)
        total_pickups = sum(abs(p.total_demand) for p in self.pickup_points)

        if total_pickups > total_deliveries:
            return min(vehicle.capacity // 4, total_deliveries)
        else:
            return min(vehicle.capacity, total_deliveries)

    def calculate_service_plan(self, individual: list) -> list:
        """Calculates the service plan for pickup and delivery operations."""
        for p in self.service_points:
            p.remaining_demand = p.total_demand

        vehicles = []
        for i, capacity in enumerate(self.vehicles_capacities):
            assigned_warehouse = random.choice(self.warehouses)
            vehicle = Vehicle(capacity, i + 1, assigned_warehouse)
            vehicles.append(vehicle)

        for vehicle in vehicles:
            vehicle.reset()
            initial_load = self._calculate_initial_load(vehicle, individual)
            vehicle.partial_load(initial_load)
            vehicle.add_stop(
                vehicle.assigned_warehouse,
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
        """Handles delivery operations for a specific point."""
        while point.remaining_demand > 0:
            vehicle = self._select_vehicle_for_delivery(vehicles, point)

            if vehicle.current_load == 0:
                nearest_warehouse = vehicle.find_nearest_warehouse(self.warehouses)
                if vehicle.route[-1]["point"] != nearest_warehouse:
                    vehicle.add_stop(
                        nearest_warehouse, is_warehouse=True, operation_type="reload"
                    )
                vehicle.reload()

            possible_delivery = min(vehicle.current_load, point.remaining_demand)

            vehicle.add_stop(point, amount=possible_delivery, operation_type="delivery")
            point.deliver(possible_delivery)

    def _handle_pickup(self, vehicles: list, point: Point) -> None:
        """Handles pickup operations for a specific point."""
        while point.remaining_demand < 0:
            pickup_amount = abs(point.remaining_demand)
            vehicle = self._select_vehicle_for_pickup(vehicles, point, pickup_amount)

            possible_pickup = min(
                vehicle.capacity - vehicle.current_load, pickup_amount
            )

            vehicle.add_stop(point, amount=possible_pickup, operation_type="pickup")
            point.pickup(possible_pickup)

            if vehicle.current_load >= vehicle.capacity * 0.8:
                nearest_warehouse = vehicle.find_nearest_warehouse(self.warehouses)
                vehicle.add_stop(
                    nearest_warehouse, is_warehouse=True, operation_type="unload"
                )
                vehicle.current_load = 0

    def _select_vehicle_for_delivery(self, vehicles: list, point: Point) -> Vehicle:
        """Selects the best vehicle for delivery operations."""
        best_vehicle = None
        min_cost = float("inf")

        for vehicle in vehicles:
            if vehicle.current_load == 0:
                continue

            current_position = (
                vehicle.route[-1]["point"]
                if vehicle.route
                else vehicle.assigned_warehouse
            )
            cost_to_point = current_position.distance_to(point)

            possible_delivery = min(vehicle.current_load, point.remaining_demand)
            efficiency = possible_delivery / (cost_to_point + 1e-6)

            if efficiency > 0 and cost_to_point < min_cost:
                min_cost = cost_to_point
                best_vehicle = vehicle

        if best_vehicle is None:
            best_vehicle = min(
                vehicles,
                key=lambda v: (
                    v.route[-1]["point"] if v.route else v.assigned_warehouse
                ).distance_to(point),
            )

        return best_vehicle

    def _select_vehicle_for_pickup(
        self, vehicles: list, point: Point, pickup_amount: int
    ) -> Vehicle:
        """Selects the best vehicle for pickup operations."""
        best_vehicle = None
        min_cost = float("inf")

        for vehicle in vehicles:
            if not vehicle.can_pickup(pickup_amount):
                continue

            current_position = (
                vehicle.route[-1]["point"]
                if vehicle.route
                else vehicle.assigned_warehouse
            )
            cost_to_point = current_position.distance_to(point)

            available_capacity = vehicle.capacity - vehicle.current_load
            efficiency = min(available_capacity, pickup_amount) / (cost_to_point + 1e-6)

            if efficiency > 0 and cost_to_point < min_cost:
                min_cost = cost_to_point
                best_vehicle = vehicle

        if best_vehicle is None:
            best_vehicle = max(vehicles, key=lambda v: v.capacity - v.current_load)

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

                # Add return to warehouse cost
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
