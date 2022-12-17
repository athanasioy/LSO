import itertools
from abc import ABC
from typing import Tuple, List

from node import Vehicle, Node
from solution import Solution


class Optimizer(ABC):
    def generate_solution_space(self):
        pass


class SwapMoveOptimizer(Optimizer):
    def __init__(self, solution: Solution):
        self.solution = solution

        self.run_again = True

    def run(self):
        c = 0
        while self.run_again:
            print(f"iteration {c}")
            self.run_again = False
            self.generate_solution_space()
            c += 1

    def generate_solution_space(self):

        max_route_length = max(len(vehicle.vehicle_route.node_sequence) for vehicle in self.solution.map.vehicles)

        for first_pos, second_pos in itertools.combinations(range(1, max_route_length), 2):  # Every possible swap
            # For every possible 2 vehicles
            for vehicle1, vehicle2 in itertools.combinations(self.solution.map.vehicles, 2):

                # check if index position exits in said routes
                if not self.feasible_combination(first_pos=first_pos,
                                                 second_pos=second_pos,
                                                 vehicle1=vehicle1,
                                                 vehicle2=vehicle2):
                    continue

                # check if capacity can
                if not self.feasible_swap(first_pos=first_pos,
                                          second_pos=second_pos,
                                          vehicle1=vehicle1,
                                          vehicle2=vehicle2):
                    continue

                beneficial_swap: bool = self.determine_cost_savings(first_pos, second_pos, vehicle1, vehicle2)

                if beneficial_swap:
                    self.swap_nodes(vehicle1.vehicle_route.node_sequence,
                                    vehicle2.vehicle_route.node_sequence,
                                    first_pos,
                                    second_pos)
                    self.run_again = True

    @staticmethod
    def swap_nodes(node_sequence: List[Node], node_sequence1: List[Node], first_pos: int, second_pos: int):

        node_sequence[first_pos], node_sequence1[second_pos] = node_sequence1[second_pos], node_sequence[first_pos]

    def determine_cost_savings(self,
                               first_pos: int,
                               second_pos: int,
                               vehicle1: Vehicle,
                               vehicle2: Vehicle) -> bool:

       # vehicle1: Vehicle = self.solution.map.vehicles[vehicle1_pos]
       # vehicle2: Vehicle = self.solution.map.vehicles[vehicle2_pos]

        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        cost_removed, cost_added = self.determine_costs(a, swap_node1, c, d, swap_node2, f)

        if cost_removed > cost_added:
            return True
        return False

    def determine_costs(self, a, swap_node1, c, d, swap_node2, f) -> Tuple[float, float]:

        cost_removed = self.solution.map.distance_matrix[(a, swap_node1)] + \
                       self.solution.map.distance_matrix[(swap_node1, c)]

        cost_removed += self.solution.map.distance_matrix[(d, swap_node2)] + \
                        self.solution.map.distance_matrix[(swap_node2, f)]

        cost_added = self.solution.map.distance_matrix[(a, swap_node2)] + \
                     self.solution.map.distance_matrix[(swap_node2, c)]

        cost_added += self.solution.map.distance_matrix[(d, swap_node1)] + \
                      self.solution.map.distance_matrix[(swap_node1, f)]
        return cost_removed, cost_added

    @staticmethod
    def feasible_swap(first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        node1 = vehicle1.vehicle_route.get_node_from_position(first_pos)
        node2 = vehicle2.vehicle_route.get_node_from_position(second_pos)

        net_demand = +node2.demand - node1.demand

        return vehicle1.has_enough_capacity(net_demand) and vehicle2.has_enough_capacity(-net_demand)

    @staticmethod
    def feasible_combination(first_pos: int, second_pos:int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        # print("**"*40)
        smallest_route = min(len(vehicle1.vehicle_route.node_sequence), len(vehicle2.vehicle_route.node_sequence))
        # print(f"smallest_route is {smallest_route}")
        # print(f"max is {max(first_pos, second_pos)}")
        if max(first_pos, second_pos) > smallest_route - 1:
            return False
        return True


class ReOrderingOptimizer(Optimizer):
    def __init__(self, solution: Solution):
        self.solution = solution

        self.run_again = True

    def run(self):
        c = 0
        while self.run_again:
            print(f"iteration {c}")
            self.run_again = False
            self.generate_solution_space()
            c += 1

    def generate_solution_space(self):
        max_route_length = max(len(vehicle.vehicle_route.node_sequence) for vehicle in self.solution.map.vehicles)
        # for vehicle1 in self.solution.map.vehicles:
        #     for first_pos in range(max_route_length):
        #         for vehicle2 in self.solution.map.vehicles:
        #             for second_pos in range(max_route_length):
        for vehicle1, vehicle2 in itertools.combinations_with_replacement(self.solution.map.vehicles, 2):
            for first_pos, second_pos in itertools.combinations(range(1, max_route_length),2):
                if not self.feasible_combination(first_pos=first_pos,
                                                 second_pos=second_pos,
                                                 vehicle1=vehicle1,
                                                 vehicle2=vehicle2):
                    continue
                befenicial_reordeing: bool = self.beneficial_relocation(first_pos=first_pos,
                                                                        second_pos=second_pos,
                                                                        vehicle1=vehicle1,
                                                                        vehicle2=vehicle2)

    @staticmethod
    def feasible_combination(first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        # print("**"*40)
        smallest_route = min(len(vehicle1.vehicle_route.node_sequence), len(vehicle2.vehicle_route.node_sequence))
        # print(f"smallest_route is {smallest_route}")
        # print(f"max is {max(first_pos, second_pos)}")
        if max(first_pos, second_pos) > smallest_route - 1:
            return False
        return True

    def beneficial_relocation(self, first_pos:int, second_pos:int, vehicle1:Vehicle, vehicle2:Vehicle):
        return False



