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
        self.run_again = True
        while self.run_again:
            self.run_again = False
            self.generate_solution_space()
            c += 1
            print(f"iteration {c}")
        return c  # Used in VHS

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
                    self.solution.run_checks()

    @staticmethod
    def swap_nodes(node_sequence: List[Node], node_sequence1: List[Node], first_pos: int, second_pos: int):
        print('swaping')
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

        cost_removed = self.solution.map.distance_matrix.get(a).get(swap_node1) + \
                       self.solution.map.distance_matrix.get(swap_node1).get(c)

        cost_removed += self.solution.map.distance_matrix.get(d).get(swap_node2) + \
                        self.solution.map.distance_matrix.get(swap_node2).get(f)

        cost_added = self.solution.map.distance_matrix.get(a).get(swap_node2) + \
                     self.solution.map.distance_matrix.get(swap_node2).get(c)

        cost_added += self.solution.map.distance_matrix.get(d).get(swap_node1) + \
                      self.solution.map.distance_matrix.get(swap_node1).get(f)
        return cost_removed, cost_added

    @staticmethod
    def feasible_swap(first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        node1 = vehicle1.vehicle_route.get_node_from_position(first_pos)
        node2 = vehicle2.vehicle_route.get_node_from_position(second_pos)

        net_demand = +node2.demand - node1.demand

        return vehicle1.has_enough_capacity(net_demand) and vehicle2.has_enough_capacity(-net_demand)

    @staticmethod
    def feasible_combination(first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        # print("**"*40)
        smallest_route = min(len(vehicle1.vehicle_route.node_sequence), len(vehicle2.vehicle_route.node_sequence))
        # print(f"smallest_route is {smallest_route}")
        # print(f"max is {max(first_pos, second_pos)}")
        if max(first_pos, second_pos) > smallest_route - 1:
            return False
        return True


class ReLocatorOptimizer(Optimizer):
    def __init__(self, solution: Solution):
        self.solution = solution

        self.run_again = True

    def run(self):
        c = 0
        self.run_again = True
        while self.run_again:
            self.run_again = False
            self.generate_solution_space()
            c += 1
            print(f"iteration {c}")
        return c

    def generate_solution_space(self):
        max_route_length = max(len(vehicle.vehicle_route.node_sequence) for vehicle in self.solution.map.vehicles)
        # for vehicle1 in self.solution.map.vehicles:
        #     for first_pos in range(max_route_length):
        #         for vehicle2 in self.solution.map.vehicles:
        #             for second_pos in range(max_route_length):
        for vehicle1, vehicle2 in itertools.product(self.solution.map.vehicles, repeat=2):
            for first_pos, second_pos in itertools.combinations(range(1, max_route_length), 2):

                if not self.feasible_combination(first_pos=first_pos,
                                                 second_pos=second_pos,
                                                 vehicle1=vehicle1,
                                                 vehicle2=vehicle2):
                    continue

                if not self.feasible_relocation(first_pos=first_pos,
                                                second_pos=second_pos,
                                                vehicle1=vehicle1,
                                                vehicle2=vehicle2):
                    continue

                beneficial_relocation: bool = self.is_beneficial_relocation(first_pos=first_pos,
                                                                            second_pos=second_pos,
                                                                            vehicle1=vehicle1,
                                                                            vehicle2=vehicle2)

                beneficial_time_impact: bool = self.determine_time_impact(first_pos=first_pos,
                                                                            second_pos=second_pos,
                                                                            vehicle1=vehicle1,
                                                                            vehicle2=vehicle2)

                if beneficial_relocation and beneficial_time_impact:
                    self.relocate(first_pos, second_pos, vehicle1, vehicle2)
                    self.run_again = True
                    self.solution.compute_service_time()

    @staticmethod
    def feasible_combination(first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        # print("**"*40)
        smallest_route = min(len(vehicle1.vehicle_route.node_sequence), len(vehicle2.vehicle_route.node_sequence))
        # print(f"smallest_route is {smallest_route}")
        # print(f"max is {max(first_pos, second_pos)}")
        if max(first_pos, second_pos) > smallest_route - 1:
            return False
        return True

    def is_beneficial_relocation(self, first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        cost_removed, cost_added = self.determine_distance_costs(a, swap_node1, c, d, swap_node2, f)
        if cost_removed > cost_added:  # Do not relocate to slowest Vehicle
            return True
        return False

    @staticmethod
    def feasible_relocation(first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        node1 = vehicle1.vehicle_route.get_node_from_position(first_pos)


        return vehicle2.has_enough_capacity(node1.demand)

    def determine_distance_costs(self, a, swap_node1, c, d, swap_node2, f) -> Tuple[float, float]:

        # we lose a-swap_node1, swap_node1-c, swap_node2-f
        # we gain a-c, swap_node1-swap_node2, swap_node1-f
        cost_removed = self.solution.map.distance_matrix.get(a).get(swap_node1) + \
                       self.solution.map.distance_matrix.get(swap_node1).get(c) + \
                       self.solution.map.distance_matrix.get(swap_node2).get(f)

        cost_added = self.solution.map.distance_matrix.get(a).get(c) + \
                     self.solution.map.distance_matrix.get(swap_node1).get(swap_node2) + \
                     self.solution.map.distance_matrix.get(swap_node1).get(f)

        return cost_removed, cost_added


    def determine_time_impact(self, first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle):
        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        time_added_vehicle2 , time_removed_vehicle1 = self.determine_time_costs(a,swap_node1,c,d,swap_node2,f,vehicle1,vehicle2)

        if time_added_vehicle2 + vehicle2.get_route_service_time() > self.solution.solution_time:
            return False
        return True



    def determine_time_costs(self, a, swap_node1, c, d, swap_node2, f, vehicle1:Vehicle, vehicle2:Vehicle):

        time_added_vehicle2 = vehicle2.time_matrix.get(swap_node2).get(swap_node1) + \
                              vehicle2.time_matrix.get(swap_node2).get(c) - \
                              vehicle2.time_matrix.get(swap_node1).get(c)

        time_removed_vehicle1 = vehicle1.time_matrix.get(d).get(swap_node2) + \
                                vehicle1.time_matrix.get(swap_node2).get(f) - \
                                vehicle1.time_matrix.get(a).get(f)

        return time_added_vehicle2, time_removed_vehicle1


    def relocate(self, first_pos, second_pos, vehicle1, vehicle2):
        print('relocating')
        print(vehicle1, vehicle1.vehicle_route)
        print(vehicle2, vehicle2.vehicle_route)

        vehicle2.vehicle_route.node_sequence.insert(second_pos+1, vehicle1.vehicle_route.node_sequence[first_pos])
        if vehicle1 == vehicle2 and first_pos > second_pos:
            # in case of intra-route relocations, when we relocate behind, we have to delete the index +1
            del vehicle1.vehicle_route.node_sequence[first_pos+1]
        else:
            del vehicle1.vehicle_route.node_sequence[first_pos]
        self.solution.run_checks()

class TwoOptOptimizer(Optimizer):
    def __init__(self, solution: Solution):
        self.solution = solution
        self.run_again = True

    def run(self):
        c = 0
        self.run_again = True
        self.solution.map.update_cumul_costs()

        while self.run_again:
            self.run_again = False
            self.generate_solution_space()
            c += 1
            print(f"iteration {c}")

        return c

    def generate_solution_space(self):
        max_route_length = max(len(vehicle.vehicle_route.node_sequence) for vehicle in self.solution.map.vehicles)
        for vehicle1, vehicle2 in itertools.combinations(self.solution.map.vehicles, r=2):
            for first_pos, second_pos in itertools.combinations(range(1, max_route_length), 2):
                if not self.feasible_combination(first_pos=first_pos,
                                                 second_pos=second_pos,
                                                 vehicle1=vehicle1,
                                                 vehicle2=vehicle2):
                    continue

                if not self.feasible_two_opt_move(first_pos=first_pos,
                                                second_pos=second_pos,
                                                vehicle1=vehicle1,
                                                vehicle2=vehicle2):
                    continue

                beneficial_two_opt: bool = self.is_beneficial_twoOpt(first_pos=first_pos,
                                                                        second_pos=second_pos,
                                                                        vehicle1=vehicle1,
                                                                        vehicle2=vehicle2)

                beneficial_time_impact: bool = self.determine_time_impact(first_pos=first_pos,
                                                                      second_pos=second_pos,
                                                                      vehicle1=vehicle1,
                                                                      vehicle2=vehicle2)

                if beneficial_two_opt and beneficial_time_impact:
                    self.doTwoOpt(first_pos=first_pos,
                                  second_pos=second_pos,
                                  vehicle1=vehicle1,
                                  vehicle2=vehicle2)
                    # self.solution.run_checks()

                    self.update_cache(vehicle1,vehicle2)

    @staticmethod
    def feasible_combination(first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        # print("**"*40)
        smallest_route = min(len(vehicle1.vehicle_route.node_sequence), len(vehicle2.vehicle_route.node_sequence))
        # print(f"smallest_route is {smallest_route}")
        # print(f"max is {max(first_pos, second_pos)}")
        if max(first_pos, second_pos) > smallest_route - 1:
            return False
        return True

    def feasible_two_opt_move(self, first_pos: int, second_pos:int , vehicle1: Vehicle, vehicle2: Vehicle):

        new_route_cost1 = vehicle1.vehicle_route.cumul_cost[first_pos] + \
                          vehicle2.vehicle_route.cumul_cost[-1] - vehicle2.vehicle_route.cumul_cost[second_pos-1]

        new_route_cost2 = vehicle2.vehicle_route.cumul_cost[second_pos-1] +\
                          vehicle1.vehicle_route.cumul_cost[-1]- \
                          vehicle1.vehicle_route.cumul_cost[first_pos]

        return new_route_cost1 <= vehicle1.vehicle_capacity and new_route_cost2 <= vehicle2.vehicle_capacity

    def is_beneficial_twoOpt(self, first_pos, second_pos, vehicle1, vehicle2):
        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        cost_removed, cost_added = self.determine_distance_costs(a, swap_node1, c, d, swap_node2, f)
        if cost_removed > cost_added:
            return True
        return False

    def determine_distance_costs(self, a, swap_node1, c, d, swap_node2, f):

        # we lose swap_node1-c, d-swap_node2
        # we gain d-c swap_node1-swap_node2
        cost_removed = self.solution.map.distance_matrix.get(swap_node1).get(c) + \
                       self.solution.map.distance_matrix.get(d).get(swap_node2)

        cost_added = self.solution.map.distance_matrix.get(d).get(c) + \
                     self.solution.map.distance_matrix.get(swap_node1).get(swap_node2)

        return cost_removed, cost_added

    def determine_time_impact(self, first_pos, second_pos, vehicle1:Vehicle, vehicle2: Vehicle):
        """ Make sure we are not making the solution worse"""

        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        vehicle1_new_time = vehicle1.vehicle_route.cumul_time_cost[:first_pos] +\
                            [vehicle1.time_matrix.get(swap_node1).get(swap_node2)]+ \
                            vehicle2.vehicle_route.cumul_time_cost[second_pos+1:]
        vehicle2_new_time = vehicle2.vehicle_route.cumul_time_cost[:second_pos-1] +\
                            [vehicle2.time_matrix.get(d).get(c)]+ \
                            vehicle1.vehicle_route.cumul_time_cost[second_pos+1:]


        if max(vehicle1_new_time[-1], vehicle2_new_time[-1]) > self.solution.solution_time:
            return False
        return True

    def doTwoOpt(self, first_pos, second_pos, vehicle1:Vehicle, vehicle2:Vehicle):
        # print('twoOpt')
        temp = vehicle1.vehicle_route.node_sequence.copy() # Keep this because swapping elements changes list
        # print(f"first pos:{first_pos}, second pos {second_pos}, vehicle1 {vehicle1}, vehicle2 {vehicle2}")
        # print(vehicle1.vehicle_route, end=',')
        # print(vehicle2.vehicle_route)

        vehicle1.vehicle_route.node_sequence = vehicle1.vehicle_route.node_sequence[:first_pos+1] + \
                                               vehicle2.vehicle_route.node_sequence[second_pos:]

        vehicle2.vehicle_route.node_sequence = vehicle2.vehicle_route.node_sequence[:second_pos] +\
                                               temp[first_pos+1:]


        # print('twoOpt Result')
        # print(vehicle1.vehicle_route, end=',')
        # print(vehicle2.vehicle_route)

        del temp #

    def update_cache(self, vehicle1:Vehicle, vehicle2:Vehicle):
        vehicle1.update_cumul_time_cost()
        vehicle1.vehicle_route.update_cumul_distance_cost()
        vehicle2.update_cumul_time_cost()
        vehicle2.vehicle_route.update_cumul_distance_cost()


class VND:
    def __init__(self):
        self.algos = []

    def add_pipeline(self, algo:Optimizer):
        self.algos.append(algo)

    def run(self):
        index = 0
        while index < len(self.algos):
            print(index)
            counter = self.algos[index].run()
            if counter == 1:
                index += 1
            else:
                index = 0  # Reset the index
