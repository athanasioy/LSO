import itertools
from typing import Tuple, List

from map_objects.node import Vehicle
from solver_objects.OptimizerABC import Optimizer
from solver_objects.OptimizerMove import Move
from solver_objects.solution import Solution


class SwapMoveOptimizer(Optimizer):
    def __init__(self, solution: Solution):
        self.solution = solution
        self.run_again = True
        self.beneficial_moves: List[Move] = []

    def run(self):
        c = 0
        self.run_again = True

        self.solution.map.update_cumul_costs()

        while self.iterator_controller():
            self.run_again = False
            self.generate_solution_space()
            if self.beneficial_moves:  # if Optimizer finds any beneficial moves
                self.apply_best_move()

            c += 1
            print(f"iteration Swap {c}")

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
                if not self.capacity_check(first_pos=first_pos,
                                          second_pos=second_pos,
                                          vehicle1=vehicle1,
                                          vehicle2=vehicle2):
                    continue

                distance_cost = self.move_cost(first_pos, second_pos, vehicle1, vehicle2)

                time_cost = self.determine_time_impact(first_pos, second_pos, vehicle1, vehicle2)
                # time_cost = 0

                self.handle_move(
                    Move(first_pos=first_pos, second_pos=second_pos, vehicle1=vehicle1, vehicle2=vehicle2,
                             distance_cost=distance_cost, time_cost=time_cost))

    def apply_move(self,first_pos:int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle):
        """Apply Swap Move"""
        vehicle1.vehicle_route.node_sequence[first_pos], vehicle2.vehicle_route.node_sequence[second_pos] = vehicle2.vehicle_route.node_sequence[second_pos], vehicle1.vehicle_route.node_sequence[first_pos]

    def move_cost(self,
                  first_pos: int,
                  second_pos: int,
                  vehicle1: Vehicle,
                  vehicle2: Vehicle) -> float:

        # vehicle1: Vehicle = self.solution.map.vehicles[vehicle1_pos]
        # vehicle2: Vehicle = self.solution.map.vehicles[vehicle2_pos]

        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        cost_removed, cost_added = self.determine_distance_costs(a, swap_node1, c, d, swap_node2, f)


        return cost_added - cost_removed

    def determine_distance_costs(self, a, swap_node1, c, d, swap_node2, f) -> Tuple[float, float]:

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
    def capacity_check(first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        node1 = vehicle1.vehicle_route.get_node_from_position(first_pos)
        node2 = vehicle2.vehicle_route.get_node_from_position(second_pos)

        net_demand = +node2.demand - node1.demand

        return vehicle1.has_enough_capacity(net_demand) and vehicle2.has_enough_capacity(-net_demand)


    def determine_time_impact(self, first_pos:int , second_pos:int , vehicle1:Vehicle, vehicle2:Vehicle):
        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        vehicle1_net_effect, vehicle2_net_effect = self.determine_time_costs(a, swap_node1, c, d, swap_node2, f, vehicle1,vehicle2)

        vehicle1_new_time = vehicle1.vehicle_route.cumul_time_cost[-1] + vehicle1_net_effect
        vehicle2_new_time = vehicle2.vehicle_route.cumul_time_cost[-1] + vehicle2_net_effect

        new_solution_time = max(vehicle1_new_time, vehicle2_new_time)

        if self.solution.slowest_vehicle not in (vehicle1, vehicle2):
            # if solution doesn't affect slowest vehicle, solution time can only go up
            return max(new_solution_time - self.solution.solution_time, 0)
        else:
            # if solution affects slowest vehicle, return net difference of new solution time minus old solution time
            return new_solution_time - self.solution.solution_time


    def determine_time_costs(self, a, swap_node1, c, d, swap_node2, f,vehicle1:Vehicle, vehicle2:Vehicle):

        vehicle2_net_effect = vehicle2.time_matrix.get(d).get(swap_node1)+ vehicle2.time_matrix.get(swap_node1).get(f)- \
                            vehicle2.time_matrix.get(d).get(swap_node2) - vehicle2.time_matrix.get(swap_node2).get(f)

        vehicle1_net_effect = vehicle1.time_matrix.get(a).get(swap_node2) + vehicle1.time_matrix.get(swap_node2).get(c)\
                              - \
                              vehicle1.time_matrix.get(a).get(swap_node1) - vehicle1.time_matrix.get(swap_node1).get(c)

        return vehicle1_net_effect , vehicle2_net_effect

class ReLocatorOptimizer(Optimizer):
    def __init__(self, solution: Solution):
        self.solution = solution
        self.run_again = True
        self.beneficial_moves: List[Move] = []

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

                if not self.capacity_check(first_pos=first_pos,
                                           second_pos=second_pos,
                                           vehicle1=vehicle1,
                                           vehicle2=vehicle2):
                    continue

                cost: float = self.move_cost(first_pos=first_pos,
                                                             second_pos=second_pos,
                                                             vehicle1=vehicle1,
                                                             vehicle2=vehicle2)

                time_impact = self.determine_time_impact(first_pos=first_pos,
                                                         second_pos=second_pos,
                                                         vehicle1=vehicle1,
                                                         vehicle2=vehicle2)

                self.handle_move(
                    Move(first_pos=first_pos, second_pos=second_pos, vehicle1=vehicle1, vehicle2=vehicle2, distance_cost=cost, time_cost=time_impact)
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

        # we lose a-swap_node1, swap_node1-c, swap_node2-f
        # we gain a-c, swap_node1-swap_node2, swap_node1-f
        cost_removed = self.solution.map.distance_matrix.get(a).get(swap_node1) + \
                       self.solution.map.distance_matrix.get(swap_node1).get(c) + \
                       self.solution.map.distance_matrix.get(swap_node2).get(f)

        cost_added = self.solution.map.distance_matrix.get(a).get(c) + \
                     self.solution.map.distance_matrix.get(swap_node1).get(swap_node2) + \
                     self.solution.map.distance_matrix.get(swap_node1).get(f)

        return cost_removed, cost_added


    def determine_time_impact(self, first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle)-> float:
        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        time_added_vehicle2 , time_removed_vehicle1 = self.determine_time_costs(a,swap_node1,c,d,swap_node2,f,vehicle1,vehicle2)

        new_vehicle_time2 = time_added_vehicle2 + vehicle2.get_route_service_time()

        # case when we are changing routes that do not concern slowest vehicle
        if self.solution.slowest_vehicle not in (vehicle1,vehicle2):
            # check if we got any slower from the slowest vehicle
            return max(new_vehicle_time2 - self.solution.solution_time,0)
        else:
            return new_vehicle_time2 - self.solution.solution_time


    def determine_time_costs(self, a, swap_node1, c, d, swap_node2, f, vehicle1:Vehicle, vehicle2:Vehicle):

        time_added_vehicle2 = vehicle2.time_matrix.get(swap_node2).get(swap_node1) + \
                              vehicle2.time_matrix.get(swap_node1).get(f) - \
                              vehicle2.time_matrix.get(swap_node2).get(f)

        time_added_vehicle1 = vehicle1.time_matrix.get(a).get(c) - \
                                vehicle1.time_matrix.get(a).get(swap_node1) - \
                                vehicle1.time_matrix.get(swap_node1).get(c)

        return time_added_vehicle2, time_added_vehicle1


    def apply_move(self, first_pos, second_pos, vehicle1, vehicle2):
        """Apply Relocation Move"""

        vehicle2.vehicle_route.node_sequence.insert(second_pos+1, vehicle1.vehicle_route.node_sequence[first_pos])
        if vehicle1 == vehicle2 and first_pos > second_pos:
            # in case of intra-route relocations, when we relocate behind, we have to delete the index +1
            del vehicle1.vehicle_route.node_sequence[first_pos+1]
        else:
            del vehicle1.vehicle_route.node_sequence[first_pos]


class TwoOptOptimizer(Optimizer):
    def __init__(self, solution: Solution):
        self.solution = solution
        self.run_again = True
        self.beneficial_moves: List[Move] = []

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

    def generate_solution_space(self):
        max_route_length = max(len(vehicle.vehicle_route.node_sequence) for vehicle in self.solution.map.vehicles)
        for vehicle1, vehicle2 in itertools.combinations(self.solution.map.vehicles, r=2):
            for first_pos, second_pos in itertools.combinations(range(1, max_route_length), 2):
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

                time_impact = self.determine_time_impact(first_pos=first_pos,
                                                         second_pos=second_pos,
                                                         vehicle1=vehicle1,
                                                         vehicle2=vehicle2)
                self.handle_move(
                    Move(first_pos=first_pos, second_pos=second_pos, vehicle1=vehicle1, vehicle2=vehicle2,
                             distance_cost=cost,time_cost=time_impact)
                )

    def capacity_check(self, first_pos: int, second_pos:int, vehicle1: Vehicle, vehicle2: Vehicle):

        new_route_cost1 = vehicle1.vehicle_route.cumul_cost[first_pos] + \
                          vehicle2.vehicle_route.cumul_cost[-1] - vehicle2.vehicle_route.cumul_cost[second_pos-1]

        new_route_cost2 = vehicle2.vehicle_route.cumul_cost[second_pos-1] +\
                          vehicle1.vehicle_route.cumul_cost[-1]- \
                          vehicle1.vehicle_route.cumul_cost[first_pos]

        return new_route_cost1 <= vehicle1.vehicle_capacity and new_route_cost2 <= vehicle2.vehicle_capacity

    def move_cost(self, first_pos, second_pos, vehicle1, vehicle2) -> float:
        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        cost_removed, cost_added = self.determine_distance_costs(a, swap_node1, c, d, swap_node2, f)
        return cost_added-cost_removed

    def determine_distance_costs(self, a, swap_node1, c, d, swap_node2, f):

        # we lose swap_node1-c, d-swap_node2
        # we gain d-c swap_node1-swap_node2
        cost_removed = self.solution.map.distance_matrix.get(swap_node1).get(c) + \
                       self.solution.map.distance_matrix.get(d).get(swap_node2)

        cost_added = self.solution.map.distance_matrix.get(d).get(c) + \
                     self.solution.map.distance_matrix.get(swap_node1).get(swap_node2)

        return cost_removed, cost_added

    def determine_time_impact(self, first_pos, second_pos, vehicle1:Vehicle, vehicle2: Vehicle) -> float:
        """ Make sure we are not making the solution worse"""

        a, swap_node1, c = vehicle1.vehicle_route.get_adjacent_nodes(first_pos)
        d, swap_node2, f = vehicle2.vehicle_route.get_adjacent_nodes(second_pos)

        vehicle1_new_time = vehicle1.vehicle_route.cumul_time_cost[first_pos] +\
                            vehicle1.time_matrix.get(swap_node1).get(swap_node2)+ \
                            vehicle2.vehicle_route.cumul_time_cost[-1] - vehicle2.vehicle_route.cumul_time_cost[second_pos]

        vehicle2_new_time = vehicle2.vehicle_route.cumul_time_cost[second_pos-1] +\
                            vehicle2.time_matrix.get(d).get(c)+ \
                            vehicle1.vehicle_route.cumul_time_cost[-1] -vehicle1.vehicle_route.cumul_time_cost[first_pos+1]

        new_solution_time = max(vehicle1_new_time, vehicle2_new_time)

        if self.solution.slowest_vehicle not in (vehicle1,vehicle2):
            # if solution doesn't affect slowest vehicle, solution time can only go up
            return max(new_solution_time - self.solution.solution_time,0)
        else:
            # if solution affects slowest vehicle, return net difference of new solution time minus old solution time
            return new_solution_time - self.solution.solution_time

    def apply_move(self, first_pos, second_pos, vehicle1:Vehicle, vehicle2:Vehicle):
        """Apply TwoOpt Move"""
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

        del temp  # Clean up



