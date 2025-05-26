import random
from lib.data_structures import Vehicle, Point


class GeneticAlgorithmVRP:
    """
    Genetic algorithm for solving the vehicle routing problem.

    Atributes:
    - points (list): List of Point objects representing the delivery points.
    - num_vehicles (int): Number of vehicles available.
    - warehouse (Point): Point object representing the warehouse.
    - population_size (int): Number of individuals in the population.
    - generations (int): Number of generations to run the algorithm.
    - mutation_rate (float): Probability of a mutation occurring.
    - tournament_size (int): Number of individuals in the tournament selection.

    Methods:
    - run(): Runs the genetic algorithm and returns the delivery plan.

    """

    def __init__(
        self,
        points: list,
        num_vehicles: int,
        warehouse: Point = None,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.2,
        tournament_size: int = 3,
    ) -> None:
        if warehouse is None:
            self.warehouse = points[0]
        else:
            self.warehouse = warehouse

        self.points = points
        self.num_vehicles = num_vehicles
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size

    def create_individual(self) -> list:
        """Creates a random individual."""
        return random.sample(self.points[1:], len(self.points[1:]))

    def calculate_delivery_plan(self, individual: list) -> list:
        """Calculates the delivery plan for the given individual."""
        for p in self.points[1:]:
            p.remaining_demand = p.total_demand

        vehicles = [Vehicle(1000, i + 1) for i in range(self.num_vehicles)]

        for vehicle in vehicles:
            vehicle.reset()
            vehicle.add_stop(self.warehouse, is_warehouse=True)
            vehicle.reload()

        for point in individual:
            while point.remaining_demand > 0:
                vehicle = self.select_vehicle(vehicles, point)

                if vehicle.current_load == 0:
                    vehicle.add_stop(self.warehouse, is_warehouse=True)
                    vehicle.reload()

                possible_delivery = min(vehicle.current_load, point.remaining_demand)

                vehicle.add_stop(point, delivery_amount=possible_delivery)
                point.deliver(possible_delivery)

        return vehicles

    def select_vehicle(self, vehicles: list, current_point: Point) -> Vehicle:
        """Selects the best vehicle for the delivery."""
        best_vehicle = None
        min_total_cost = float("inf")

        for vehicle in vehicles:
            current_position = (
                self.warehouse
                if vehicle.current_load == 0
                else vehicle.route[-1]["point"]
            )

            cost_to_point = current_position.distance_to(current_point)
            cost_to_warehouse = current_point.distance_to(self.warehouse)
            total_cost = cost_to_point + cost_to_warehouse

            possible_delivery = min(
                vehicle.current_load, current_point.remaining_demand
            )
            efficiency = possible_delivery / (
                total_cost + 1e-6
            )  # prevents division by zero

            if efficiency > 0 and total_cost < min_total_cost:
                min_total_cost = total_cost
                best_vehicle = vehicle

        if best_vehicle is None:
            best_vehicle = min(
                vehicles, key=lambda v: v.route[-1]["point"].distance_to(self.warehouse)
            )

        return best_vehicle

    def fitness(self, individual: list) -> float:
        """Calculates the total distance of the delivery plan."""
        if None in individual or len(individual) != len(self.points[1:]):
            return float("inf")

        try:
            vehicles = self.calculate_delivery_plan(individual)
            total_distance = 0

            for vehicle in vehicles:
                last_point = self.warehouse
                for stop in vehicle.route:
                    current_point = stop["point"]
                    total_distance += last_point.distance_to(current_point)
                    last_point = current_point

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
        reference_point = random.choice(self.points[1:])
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

        # I have no idea why adding the warehouse at the end is necessary but it is
        full_route = route + [self.warehouse]

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
        distance = 0
        last_point = self.warehouse
        for point in route:
            distance += last_point.distance_to(point)
            last_point = point
        return distance

    def run(self) -> list:
        """
        Runs the genetic algorithm.

        Returns a list of Vehicle objects representing the delivery routes.
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
        return self.calculate_delivery_plan(best_solution)
