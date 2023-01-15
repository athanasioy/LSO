from abc import ABC, abstractmethod
from typing import List, Tuple

from map_objects.node import Vehicle
from solver_objects.move import OptimizerMove, DistanceType
from solver_objects.solution import Solution


class Optimizer(ABC):
    beneficial_moves: List[OptimizerMove]
    solution: Solution
    run_again: bool
    distances: DistanceType

    @abstractmethod
    def generate_solution_space(self, distance: DistanceType):
        """Generate all possible moves"""
        pass

    @abstractmethod
    def move_cost(self, first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> float:
        """Return True if move gives lower cost"""
        pass

    @staticmethod
    @abstractmethod
    def capacity_check(first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        """Check capacity"""
        pass

    @abstractmethod
    def determine_distance_costs(self, a, swap_node1, c, d, swap_node2, f, vehicle1, vehicle2) -> Tuple[float, float]:
        """Determine the Cost of Move"""
        pass

    @abstractmethod
    def apply_move(self, first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle):
        """Apply Move"""
        pass

    @staticmethod
    def feasible_combination(first_pos: int, second_pos: int, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        """Check if all indices are inside the bounds of the route list"""
        smallest_route = min(len(vehicle1.vehicle_route.node_sequence), len(vehicle2.vehicle_route.node_sequence))

        if max(first_pos, second_pos) > smallest_route - 1:
            return False
        return True

    def handle_move(self, move: OptimizerMove):
        if move.move_cost < 0:
            self.add_move(move)
            self.run_again = True

    def add_move(self, move: OptimizerMove):
        self.beneficial_moves.append(move)

    def apply_best_move(self):
        self.beneficial_moves.sort(key=lambda move: move.move_cost)
        best_move = self.beneficial_moves[0]
        old_time = self.solution.solution_time
        est_time = self.solution.solution_time + best_move.time_cost
        self.apply_move(best_move.first_pos, best_move.second_pos, best_move.vehicle1, best_move.vehicle2)
        self.update_cache((best_move.vehicle1, best_move.vehicle1_new_time),
                          (best_move.vehicle2, best_move.vehicle2_new_time))
        new_time = self.solution.solution_time
        # if abs(est_time - new_time) > 0.01:
        #     print(best_move.vehicle1.vehicle_route.node_sequence)
        #     print(best_move.vehicle2.vehicle_route.node_sequence)
        #     print(f"estimated {est_time}, actual {new_time}")
        #     print(best_move)
        #     raise ValueError("Error On Cost Calculation")
        if old_time > new_time:
            print(F"OLD: {old_time}, NEW :{new_time}, {self.solution.compute_total_distance()}")
        self.beneficial_moves = []

    def update_cache(self, *args: tuple[Vehicle, float]):
        for arg in args:
            arg[0].update_cumul_time_cost()
            arg[0].vehicle_route.update_cumul_distance_cost()
        # self.solution.update_service_time_from_cache(*args)
        self.solution.compute_service_time()

    def iterator_controller(self):
        return self.run_again

    def determine_new_solution_time(self, *args: tuple[Vehicle, float], distance: DistanceType) -> float:
        """
        Compute on the fly new solution time by copying dictionaries of vehicle times
        Returns a float that represents new slowest route
        """
        if distance == DistanceType.PENALIZED:
            vehicle_times_copy = self.solution.penalized_vehicle_times.copy()
        else:
            vehicle_times_copy = self.solution.vehicle_times.copy()

        for vehicle, time in args:
            vehicle_times_copy.update({vehicle: time})
        slowest_vehicle = max(vehicle_times_copy, key=lambda x: vehicle_times_copy.get(x))
        return vehicle_times_copy.get(slowest_vehicle)

    def determine_time_matrix(self, vehicle1: Vehicle, vehicle2: Vehicle):
        if self.distances == DistanceType.PENALIZED:
            time_distances_vehicle1 = vehicle1.penalized_time_matrix
            time_distances_vehicle2 = vehicle2.penalized_time_matrix
        else:
            time_distances_vehicle1 = vehicle1.time_matrix
            time_distances_vehicle2 = vehicle2.time_matrix

        return time_distances_vehicle1, time_distances_vehicle2

    def determine_distance_matrix(self):
        if self.distances == DistanceType.PENALIZED:
            distances = self.solution.map.penalized_distance_matrix
        else:
            distances = self.solution.map.distance_matrix

        return distances

    def determine_cumuls_costs(self, vehicle1: Vehicle, vehicle2: Vehicle):
        if self.distances == DistanceType.PENALIZED:
            cumul_time1 = vehicle1.vehicle_route.penalized_cumul_time_cost
            cumul_time2 = vehicle2.vehicle_route.penalized_cumul_time_cost
        else:
            cumul_time1 = vehicle1.vehicle_route.cumul_time_cost
            cumul_time2 = vehicle2.vehicle_route.cumul_time_cost

        return cumul_time1, cumul_time2
