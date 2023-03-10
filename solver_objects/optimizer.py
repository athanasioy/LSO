import itertools
from typing import Tuple, List

from map_objects.node import Vehicle
from solver_objects.OptimizerABC import Optimizer
from solver_objects.move import OptimizerMove, DistanceType
from solver_objects.solution import Solution


class SwapMoveOptimizer(Optimizer):
    def __init__(self, solution: Solution):
        self.solution = solution
        self.run_again = True
        self.beneficial_moves: List[OptimizerMove] = []
        self.solution.map.update_cumul_costs()
        self.distances = None

    def run(self):
        c = 0
        self.run_again = True

        while self.iterator_controller():
            self.run_again = False
            self.generate_solution_space()
            if self.beneficial_moves:  # if Optimizer finds any beneficial moves
                self.apply_best_move()

            c += 1
            print(f"iteration Swap {c}")

        return c  # Used in VHS

    def generate_solution_space(self, distances: DistanceType = DistanceType.NORMAL):
        self.distances = distances  # Set Distances
        max_route_length = max(len(vehicle.vehicle_route.node_sequence) for vehicle in self.solution.map.vehicles)

        for first_pos, second_pos in itertools.combinations_with_replacement(range(1, max_route_length + 1), r=2):  # Every possible swap
            # For every possible 2 vehicles
            for vehicle1, vehicle2 in itertools.product(self.solution.map.vehicles, repeat=2):
                if vehicle1 == vehicle2 and abs(first_pos - second_pos) <= 1:
                    continue

                # check if index position exits in said routes
                if not self.feasible_combination(first_pos=first_pos,
                                                 second_pos=second_pos,
                                                 vehicle1=vehicle1,
                                                 vehicle2=vehicle2):
                    continue

                # check if capacity can
                if not self.capacity_check(first_pos=first_pos,
                                           second_pos=second_pos,
                                           vehicle1=vehicle1,
                                           vehicle2=vehicle2):
                    continue

                distance_cost = self.move_cost(first_pos, second_pos, vehicle1, vehicle2)

                time_cost, v1_time, v2_time = self.determine_time_impact(first_pos, second_pos, vehicle1, vehicle2)
                # time_cost = 0

                self.handle_move(
                    OptimizerMove(first_pos=first_pos,
                                  second_pos=second_pos,
                                  vehicle1=vehicle1,
                                  vehicle2=vehicle2,
                                  distance_cost=distance_cost,
                                  time_cost=time_cost,
                                  vehicle1_new_time=v1_time,
                                  vehicle2_new_time=v2_time))

    def apply_move(self, first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle):
        """Apply Swap Move"""
        vehicle1.vehicle_route.node_sequence[first_pos], vehicle2.vehicle_route.node_sequence[second_pos] = \
            vehicle2.vehicle_route.node_sequence[second_pos], vehicle1.vehicle_route.node_sequence[first_pos]

    def move_cost(self,
                  first_pos: int,
                  second_pos: int,
                  vehicle1: Vehicle,
                  vehicle2: Vehicle) -> float:

        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        cost_removed, cost_added = self.determine_distance_costs(a, swap_node1, c, d, swap_node2, f, vehicle1, vehicle2)

        return cost_added - cost_removed

    def determine_distance_costs(self, a, swap_node1, c, d, swap_node2, f, vehicle1, vehicle2) -> Tuple[float, float]:
        distances = self.determine_distance_matrix()

        cost_removed = distances.get(a).get(swap_node1) + \
                       distances.get(swap_node1).get(c)

        cost_removed += distances.get(d).get(swap_node2) + \
                        distances.get(swap_node2).get(f)

        cost_added = distances.get(a).get(swap_node2) + \
                     distances.get(swap_node2).get(c)

        cost_added += distances.get(d).get(swap_node1) + \
                      distances.get(swap_node1).get(f)

        if swap_node2 == f:  # if swap_node2 is last node on route:
            cost_added -= distances.get(swap_node1).get(f)  # Cancel this

        if swap_node1 == c:  # if swap_node1 is last node on route:
            cost_added -= distances.get(swap_node2).get(c)

        if vehicle1 == vehicle2 and d == swap_node1 and c == swap_node2:  # in case of intra-route and swap nodes are next to each other
            # correct for double counting of arcs
            cost_removed -= distances.get(swap_node1).get(c)
            cost_removed -= distances.get(swap_node2).get(f)

        return cost_removed, cost_added

    @staticmethod
    def capacity_check(first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        node1 = vehicle1.vehicle_route.get_node_from_position(first_pos)
        node2 = vehicle2.vehicle_route.get_node_from_position(second_pos)

        net_demand = +node2.demand - node1.demand

        return vehicle1.has_enough_capacity(net_demand) and vehicle2.has_enough_capacity(-net_demand)

    def determine_time_impact(self, first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle):
        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        vehicle1_net_effect, vehicle2_net_effect = self.determine_time_costs(a, swap_node1, c, d, swap_node2, f,
                                                                             vehicle1, vehicle2)

        vehicle1_new_time = vehicle1.vehicle_route.cumul_time_cost[-1] + vehicle1_net_effect
        vehicle2_new_time = vehicle2.vehicle_route.cumul_time_cost[-1] + vehicle2_net_effect

        new_solution_time = self.determine_new_solution_time((vehicle1, vehicle1_new_time),
                                                             (vehicle2, vehicle2_new_time), distance=self.distances)

        return new_solution_time - self.solution.solution_time, vehicle1_new_time, vehicle2_new_time

    def determine_time_costs(self, a, swap_node1, c, d, swap_node2, f, vehicle1: Vehicle, vehicle2: Vehicle):
        time_distances_vehicle1, time_distances_vehicle2 = self.determine_time_matrix(vehicle1, vehicle2)

        if vehicle1 == vehicle2:
            vehicle1_net_effect = time_distances_vehicle1.get(a).get(swap_node2)
            vehicle1_net_effect += time_distances_vehicle1.get(swap_node2).get(c)
            vehicle1_net_effect -= time_distances_vehicle1.get(a).get(swap_node1)
            vehicle1_net_effect -= time_distances_vehicle1.get(swap_node1).get(c)

            vehicle1_net_effect += time_distances_vehicle1.get(d).get(swap_node1)
            vehicle1_net_effect += time_distances_vehicle1.get(swap_node1).get(f)
            vehicle1_net_effect -= time_distances_vehicle1.get(d).get(swap_node2)
            vehicle1_net_effect -= time_distances_vehicle1.get(swap_node2).get(f)

            if swap_node2 == f:  # if swap_node2 is last node on route:
                vehicle1_net_effect -= time_distances_vehicle2.get(swap_node1).get(f)  # Cancel this

            if swap_node1 == c:  # if swap_node1 is last node on route:
                vehicle1_net_effect -= time_distances_vehicle1.get(swap_node2).get(c)

            if vehicle1 == vehicle2 and d == swap_node1 and c == swap_node2:  # in case of intra-route and swap nodes are next to each other
                # correct for double counting of arcs
                vehicle1_net_effect -= time_distances_vehicle1.get(swap_node1).get(c)
                vehicle1_net_effect -= time_distances_vehicle1.get(swap_node2).get(f)

            vehicle2_net_effect = vehicle1_net_effect

        else:
            vehicle2_net_effect = time_distances_vehicle2.get(d).get(swap_node1)
            vehicle2_net_effect += time_distances_vehicle2.get(swap_node1).get(f)
            vehicle2_net_effect -= time_distances_vehicle2.get(d).get(swap_node2)
            vehicle2_net_effect -= time_distances_vehicle2.get(swap_node2).get(f)

            vehicle1_net_effect = time_distances_vehicle1.get(a).get(swap_node2)
            vehicle1_net_effect += time_distances_vehicle1.get(swap_node2).get(c)
            vehicle1_net_effect -= time_distances_vehicle1.get(a).get(swap_node1)
            vehicle1_net_effect -= time_distances_vehicle1.get(swap_node1).get(c)

            if swap_node2 == f:  # if swap_node2 is last node on route:
                vehicle2_net_effect -= time_distances_vehicle2.get(swap_node1).get(f)  # Cancel this

            if swap_node1 == c:  # if swap_node1 is last node on route:
                vehicle1_net_effect -= time_distances_vehicle1.get(swap_node2).get(c)

        return vehicle1_net_effect, vehicle2_net_effect


    def __repr__(self):
        return "Swap Move"


class ReLocatorOptimizer(Optimizer):
    def __init__(self, solution: Solution):
        self.solution = solution
        self.run_again = True
        self.beneficial_moves: List[OptimizerMove] = []
        self.distances = None

    def run(self):
        self.c = 0
        self.run_again = True
        while self.iterator_controller():
            self.run_again = False
            self.generate_solution_space()
            if self.beneficial_moves:
                self.apply_best_move()
            self.c += 1
            print(f"iteration reloc {self.c}")
        return self.c

    def generate_solution_space(self, distances: DistanceType = DistanceType.NORMAL):
        self.distances = distances  # Set Distances
        max_route_length = max(len(vehicle.vehicle_route.node_sequence) for vehicle in self.solution.map.vehicles)

        # for every single intra-route and inter-route combination
        for vehicle1, vehicle2 in itertools.product(self.solution.map.vehicles, repeat=2):
            # check combinations
            for first_pos, second_pos in itertools.combinations(range(1, max_route_length + 1), 2):
                if not self.feasible_combination(first_pos=first_pos,
                                                 second_pos=second_pos,
                                                 vehicle1=vehicle1,
                                                 vehicle2=vehicle2):
                    continue

                if not self.capacity_check(first_pos=first_pos,
                                           second_pos=second_pos,
                                           vehicle1=vehicle1,
                                           vehicle2=vehicle2):
                    continue

                cost: float = self.move_cost(first_pos=first_pos,
                                             second_pos=second_pos,
                                             vehicle1=vehicle1,
                                             vehicle2=vehicle2)

                time_impact, v1_time, v2_time = self.determine_time_impact(first_pos=first_pos,
                                                                           second_pos=second_pos,
                                                                           vehicle1=vehicle1,
                                                                           vehicle2=vehicle2)

                self.handle_move(
                    OptimizerMove(first_pos=first_pos,
                                  second_pos=second_pos,
                                  vehicle1=vehicle1,
                                  vehicle2=vehicle2,
                                  distance_cost=cost,
                                  time_cost=time_impact,
                                  vehicle1_new_time=v1_time,
                                  vehicle2_new_time=v2_time)
                )

    def move_cost(self, first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> float:
        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        cost_removed, cost_added = self.determine_distance_costs(a, swap_node1, c, d, swap_node2, f)
        return cost_added - cost_removed

    @staticmethod
    def capacity_check(first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        node1 = vehicle1.vehicle_route.get_node_from_position(first_pos)

        return vehicle2.has_enough_capacity(node1.demand)

    def determine_distance_costs(self, a, swap_node1, c, d, swap_node2, f) -> Tuple[float, float]:
        distances = self.determine_distance_matrix()

        # we lose a-swap_node1, swap_node1-c, swap_node2-f
        # we gain a-c, swap_node1-swap_node2, swap_node1-f

        cost_removed = distances.get(a).get(swap_node1)
        cost_removed += distances.get(swap_node1).get(c)
        cost_removed += distances.get(swap_node2).get(f)

        cost_added = distances.get(a).get(c)
        cost_added += distances.get(swap_node1).get(swap_node2)
        cost_added += distances.get(swap_node1).get(f)

        if swap_node2 == f:  # if swap_node2 is at end of route:
            cost_added -= distances.get(swap_node2).get(swap_node1)
        if swap_node1 == c:  # if swap_node1 is at end of route:
            cost_added -= distances.get(a).get(c)

        return cost_removed, cost_added

    def determine_time_impact(self, first_pos: int,
                              second_pos: int,
                              vehicle1: Vehicle,
                              vehicle2: Vehicle) -> Tuple[float, float, float]:

        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        time_added_vehicle2, time_added_vehicle1 = self.determine_time_costs(a, swap_node1, c, d, swap_node2, f,
                                                                             vehicle1, vehicle2)

        if vehicle1 == vehicle2:
            vehicle1_new_time = vehicle1.vehicle_route.cumul_time_cost[-1] + time_added_vehicle1 + time_added_vehicle2
            vehicle2_new_time = vehicle1_new_time
            new_solution_time = self.determine_new_solution_time((vehicle1, vehicle1_new_time), distance=self.distances)
        else:
            vehicle1_new_time = + vehicle1.vehicle_route.cumul_time_cost[-1] + time_added_vehicle1
            vehicle2_new_time = vehicle2.vehicle_route.cumul_time_cost[-1] + time_added_vehicle2

            new_solution_time = self.determine_new_solution_time((vehicle1, vehicle1_new_time),
                                                                 (vehicle2, vehicle2_new_time), distance=self.distances)

        return new_solution_time - self.solution.solution_time, vehicle1_new_time, vehicle2_new_time

    def determine_time_costs(self, a, swap_node1, c, d, swap_node2, f, vehicle1: Vehicle, vehicle2: Vehicle):
        """relocate swap node1 in front of swap node 2"""
        time_distances_vehicle1, time_distances_vehicle2 = self.determine_time_matrix(vehicle1, vehicle2)

        time_added_vehicle2 = time_distances_vehicle2.get(swap_node2).get(swap_node1)
        time_added_vehicle2 += time_distances_vehicle2.get(swap_node1).get(f)
        time_added_vehicle2 -= time_distances_vehicle2.get(swap_node2).get(f)

        time_added_vehicle1 = time_distances_vehicle1.get(a).get(c)
        time_added_vehicle1 -= time_distances_vehicle1.get(a).get(swap_node1)
        time_added_vehicle1 -= time_distances_vehicle1.get(swap_node1).get(c)

        if swap_node2 == f:  # if swap_node2 is at end of route:
            time_added_vehicle2 -= time_distances_vehicle2.get(swap_node2).get(swap_node1)

        if swap_node1 == c:  # if swap_node1 is at end of route:
            time_added_vehicle1 -= time_distances_vehicle1.get(a).get(c)

        return time_added_vehicle2, time_added_vehicle1

    def apply_move(self, first_pos, second_pos, vehicle1, vehicle2):
        """Apply Relocation Move"""
        vehicle2.vehicle_route.node_sequence.insert(second_pos + 1, vehicle1.vehicle_route.node_sequence[first_pos])
        if vehicle1 == vehicle2 and first_pos > second_pos:
            # in case of intra-route relocations, when we relocate behind, we have to delete the index +1
            del vehicle1.vehicle_route.node_sequence[first_pos + 1]
        else:
            del vehicle1.vehicle_route.node_sequence[first_pos]

    def __repr__(self):
        return "Relocation Move"


class TwoOptOptimizer(Optimizer):
    def __init__(self, solution: Solution):
        self.solution = solution
        self.run_again = True
        self.beneficial_moves: List[OptimizerMove] = []

    def run(self):
        c = 0
        self.run_again = True
        self.solution.map.update_cumul_costs()

        while self.iterator_controller():
            self.run_again = False
            self.generate_solution_space()
            if self.beneficial_moves:
                self.apply_best_move()

            c += 1
            print(f"iteration twoOpt {c}")

        return c

    def generate_solution_space(self, distances: DistanceType = DistanceType.NORMAL):
        self.distances = distances  # Set Distances

        max_route_length = max(len(vehicle.vehicle_route.node_sequence) for vehicle in self.solution.map.vehicles)
        for vehicle1, vehicle2 in itertools.combinations_with_replacement(self.solution.map.vehicles, r=2):
            for first_pos, second_pos in itertools.product(range(1, max_route_length + 1), repeat=2):

                if not self.feasible_combination(first_pos=first_pos,
                                                 second_pos=second_pos,
                                                 vehicle1=vehicle1,
                                                 vehicle2=vehicle2):
                    continue

                if first_pos == len(vehicle1.vehicle_route.node_sequence) - 1 and vehicle2 != vehicle1:
                    continue  # Can't Do Two Opt for end of route

                if vehicle1 == vehicle2 and second_pos - first_pos < 2:
                    continue

                if not self.capacity_check(first_pos=first_pos,
                                           second_pos=second_pos,
                                           vehicle1=vehicle1,
                                           vehicle2=vehicle2):
                    continue

                cost: float = self.move_cost(first_pos=first_pos,
                                             second_pos=second_pos,
                                             vehicle1=vehicle1,
                                             vehicle2=vehicle2)

                time_impact, v1_time, v2_time = self.determine_time_impact(first_pos=first_pos,
                                                                           second_pos=second_pos,
                                                                           vehicle1=vehicle1,
                                                                           vehicle2=vehicle2)
                self.handle_move(
                    OptimizerMove(first_pos=first_pos,
                                  second_pos=second_pos,
                                  vehicle1=vehicle1,
                                  vehicle2=vehicle2,
                                  distance_cost=cost,
                                  time_cost=time_impact,
                                  vehicle1_new_time=v1_time,
                                  vehicle2_new_time=v2_time)
                )

    def capacity_check(self, first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle):

        if vehicle1 == vehicle2:
            return True

        new_route_cost1 = vehicle1.vehicle_route.cumul_demand[first_pos] + \
                          vehicle2.vehicle_route.cumul_demand[-1] - vehicle2.vehicle_route.cumul_demand[second_pos - 1]

        new_route_cost2 = vehicle2.vehicle_route.cumul_demand[second_pos - 1] + \
                          vehicle1.vehicle_route.cumul_demand[-1] - \
                          vehicle1.vehicle_route.cumul_demand[first_pos]

        return new_route_cost1 <= vehicle1.vehicle_capacity and new_route_cost2 <= vehicle2.vehicle_capacity

    def move_cost(self, first_pos, second_pos, vehicle1, vehicle2) -> float:
        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        cost_removed, cost_added = self.determine_distance_costs(a, swap_node1, c, d, swap_node2, f, vehicle1, vehicle2)
        return cost_added - cost_removed

    def determine_distance_costs(self, a, swap_node1, c, d, swap_node2, f, vehicle1, vehicle2):
        distances = self.determine_distance_matrix()
        # we lose swap_node1-c, d-swap_node2
        # we gain d-c swap_node1-swap_node2

        if vehicle1 == vehicle2:
            cost_added = distances.get(swap_node1).get(swap_node2)
            cost_added += distances.get(c).get(f)

            cost_removed = distances.get(swap_node1).get(c)
            cost_removed += distances.get(swap_node2).get(f)

            if swap_node2 == f:
                cost_added -= distances.get(c).get(f)

        else:
            cost_removed = distances.get(swap_node1).get(c)
            cost_removed += distances.get(d).get(swap_node2)

            cost_added = distances.get(d).get(c)
            cost_added += distances.get(swap_node1).get(swap_node2)

        return cost_removed, cost_added

    def determine_time_impact(self, first_pos,
                              second_pos,
                              vehicle1: Vehicle,
                              vehicle2: Vehicle) -> Tuple[float, float, float]:
        """ Make sure we are not making the solution worse"""
        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        time_distances_vehicle1, time_distances_vehicle2 = self.determine_time_matrix(vehicle1, vehicle2)
        cumul1, cumul2 = self.determine_cumuls_costs(vehicle1, vehicle2)

        if vehicle1 == vehicle2:
            time_added_vehicle1 = time_distances_vehicle1.get(swap_node1).get(swap_node2)
            time_added_vehicle1 += time_distances_vehicle1.get(c).get(f)

            time_removed_vehicle1 = time_distances_vehicle1.get(swap_node1).get(c)
            time_removed_vehicle1 += time_distances_vehicle1.get(swap_node2).get(f)

            if swap_node2 == f:
                time_added_vehicle1 -= time_distances_vehicle1.get(c).get(f)

            vehicle1_new_time = cumul1[-1] + time_added_vehicle1 - time_removed_vehicle1
            vehicle2_new_time = vehicle1_new_time

            new_solution_time = self.determine_new_solution_time((vehicle1, vehicle1_new_time),
                                                                 (vehicle2, vehicle2_new_time), distance=self.distances)

        else:
            vehicle1_new_time = cumul1[first_pos]
            vehicle1_new_time += time_distances_vehicle1.get(swap_node1).get(swap_node2)
            vehicle1_new_time += cumul2[-1] - cumul2[second_pos]

            vehicle2_new_time = cumul2[second_pos - 1]
            vehicle2_new_time += time_distances_vehicle2.get(d).get(c)
            vehicle2_new_time += cumul1[-1] - cumul1[first_pos + 1]

            new_solution_time = self.determine_new_solution_time((vehicle1, vehicle1_new_time),
                                                                 (vehicle2, vehicle2_new_time), distance=self.distances)

        return new_solution_time - self.solution.solution_time, vehicle1_new_time, vehicle2_new_time

    def apply_move(self, first_pos, second_pos, vehicle1: Vehicle, vehicle2: Vehicle):
        """Apply TwoOpt Move"""

        if vehicle1 == vehicle2:
            reversed_segment = reversed(vehicle1.vehicle_route.node_sequence[first_pos + 1:second_pos + 1])

            vehicle1.vehicle_route.node_sequence[first_pos + 1: second_pos + 1] = reversed_segment
        else:

            temp = vehicle1.vehicle_route.node_sequence.copy()  # Keep this because swapping elements changes list
            # print(f"first pos:{first_pos}, second pos {second_pos}, vehicle1 {vehicle1}, vehicle2 {vehicle2}")
            # print(vehicle1.vehicle_route, end=',')
            # print(vehicle2.vehicle_route)

            vehicle1.vehicle_route.node_sequence = vehicle1.vehicle_route.node_sequence[:first_pos + 1] + \
                                                   vehicle2.vehicle_route.node_sequence[second_pos:]

            vehicle2.vehicle_route.node_sequence = vehicle2.vehicle_route.node_sequence[:second_pos] + \
                                                   temp[first_pos + 1:]

            # print('twoOpt Result')
            # print(vehicle1.vehicle_route, end=',')
            # print(vehicle2.vehicle_route)

            del temp  # Clean up


    def __repr__(self):
        return "TwoOpt Move"
