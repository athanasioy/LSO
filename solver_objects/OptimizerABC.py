from abc import ABC, abstractmethod
from typing import List, Tuple

from map_objects.node import Vehicle
from solver_objects.move import OptimizerMove
from solver_objects.solution import Solution


class Optimizer(ABC):
    beneficial_moves: List[OptimizerMove]
    solution: Solution
    run_again: bool

    @abstractmethod
    def generate_solution_space(self):
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
    def determine_distance_costs(self, a, swap_node1, c, d, swap_node2, f) -> Tuple[float, float]:
        """Determine the Cost of Move"""
        pass

    @abstractmethod
    def apply_move(self,first_pos:int, second_pos:int, vehicle1:Vehicle, vehicle2:Vehicle):
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
        self.apply_move(best_move.first_pos, best_move.second_pos, best_move.vehicle1, best_move.vehicle2)
        self.update_cache(best_move.vehicle1, best_move.vehicle2)
        self.beneficial_moves = []

    def update_cache(self, *args):
        for vehicle in args:
            vehicle.update_cumul_time_cost()
            vehicle.vehicle_route.update_cumul_distance_cost()
        self.solution.compute_service_time()

    def iterator_controller(self):
        return self.run_again

    def determine_new_solution_time(self, *args: tuple[Vehicle, float]) -> float:
        vehicle_times_copy = self.solution.vehicle_times.copy()
        for vehicle, time in args:
            vehicle_times_copy.update({vehicle: time})
        slowest_vehicle = max(vehicle_times_copy, key=lambda x: vehicle_times_copy.get(x))
        return vehicle_times_copy.get(slowest_vehicle)
