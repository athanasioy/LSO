import itertools
import random
from copy import deepcopy

from draw.ui import UI
from solver_objects.move import OptimizerMove, DistanceType
from solver_objects.optimizer import ReLocatorOptimizer, TwoOptOptimizer, SwapMoveOptimizer
from solver_objects.OptimizerABC import Optimizer
from solver_objects.solution import Solution
from typing import List


class VNDCombiner:
    def __init__(self):
        self.algos: List[Optimizer] = []

    def add_pipeline(self, algo: Optimizer):
        self.algos.append(algo)


class VND(VNDCombiner):
    def run(self):
        index = 0
        while index < len(self.algos):
            self.algos[index].generate_solution_space()
            if self.algos[index].beneficial_moves:
                self.algos[index].apply_best_move()
                index = 0
            else:
                index += 1


class VNDGLS(VNDCombiner):
    def __init__(self, random_seed: int, limit: int, solution: Solution):
        super().__init__()
        self.seed = random_seed
        self.limit = limit
        self.times_penalized = {}
        self.solution = solution
        self.initialize_times_penalized()

    def run(self):
        random.seed(self.seed)
        counter = 0
        while counter < self.limit:
            index = random.randint(0, len(self.algos) - 1)
            self.algos[index].generate_solution_space(DistanceType.PENALIZED)
            if self.algos[index].beneficial_moves:
                self.algos[index].apply_best_move()
            else:
                print('Penalized')
                self.penalize_arcs()
            counter += 1
            print(counter)

    def penalize_arcs(self):
        max_criterion = 0
        pen_1 = -1
        pen_2 = -1
        vehicle = None
        for vehicle in self.solution.map.vehicles:
            rt = vehicle
            for j in range(len(rt.vehicle_route.node_sequence) - 1):
                id1 = rt.vehicle_route.node_sequence[j]
                id2 = rt.vehicle_route.node_sequence[j + 1]
                criterion = self.solution.map.distance_matrix.get(id1).get(id2) / (1 + self.times_penalized[id1][id2])

                if criterion > max_criterion:
                    max_criterion = criterion
                    pen_1 = id1
                    pen_2 = id2
                    vehicle = rt

        self.times_penalized[pen_1][pen_2] += 1
        self.times_penalized[pen_2][pen_1] += 1

        pen_weight = 0.15

        self.solution.map.penalized_distance_matrix[pen_1][pen_2] = (1 + pen_weight * self.times_penalized[pen_1][
            pen_2]) * self.solution.map.distance_matrix[pen_1][pen_2]
        self.solution.map.penalized_distance_matrix[pen_2][pen_1] = (1 + pen_weight * self.times_penalized[pen_2][
            pen_1]) * self.solution.map.distance_matrix[pen_2][pen_1]

        vehicle.penalized_time_matrix[pen_1][pen_2] = (1 + pen_weight * self.times_penalized[pen_1][
            pen_2]) * vehicle.time_matrix[pen_1][pen_2]
        vehicle.penalized_time_matrix[pen_2][pen_1] = (1 + pen_weight * self.times_penalized[pen_2][
            pen_1]) * vehicle.time_matrix[pen_2][pen_1]

        self.penalized_n1_ID = pen_1
        self.penalized_n2_ID = pen_2

    def initialize_times_penalized(self):

        for node1, node2 in itertools.product(self.solution.map.nodes, repeat=2):

            if not self.times_penalized.get(node1):  # is None:
                self.times_penalized[node1] = {}

            self.times_penalized.get(node1).update({node2: 1})


class TabuOptimizer(Optimizer):
    def __init__(self, solution: Solution, limit: int, tabu_expander: int):
        super().__init__(solution)
        self.iterator_limit = limit
        self.counter = 0
        self.tabu_expander = tabu_expander
        self.best_solution = self.solution.solution_time

    def iterator_controller(self):
        return self.counter <= self.iterator_limit

    def handle_move(self, move: OptimizerMove):
        if not self.is_tabu(move) or self.solution.solution_time + move.time_cost < self.best_solution:
            self.add_move(move)

    def run(self):
        self.counter = 0
        while self.iterator_controller():
            self.generate_solution_space()
            if self.beneficial_moves:
                self.apply_best_move()
            self.counter += 1
            print(f"iteration  {self.counter}, {self.solution.solution_time}, {self.solution.compute_total_distance()}")

    def is_tabu(self, move: OptimizerMove) -> bool:
        node1 = move.vehicle1.vehicle_route.get_node_from_position(move.first_pos)
        node2 = move.vehicle2.vehicle_route.get_node_from_position(move.second_pos)

        return node1.tabu_iterator > self.counter or node2.tabu_iterator > self.counter

    def set_tabu(self, best_move: OptimizerMove):
        best_move.vehicle1.vehicle_route.get_node_from_position(
            best_move.first_pos).tabu_iterator = self.counter + self.tabu_expander
        best_move.vehicle2.vehicle_route.get_node_from_position(
            best_move.second_pos).tabu_iterator = self.counter + self.tabu_expander

    def apply_best_move(self):
        self.beneficial_moves.sort(key=lambda move: move.move_cost)
        best_move = self.beneficial_moves[0]
        self.apply_move(best_move.first_pos, best_move.second_pos, best_move.vehicle1, best_move.vehicle2)
        self.update_cache((best_move.vehicle1, best_move.vehicle1_new_time),
                          (best_move.vehicle2, best_move.vehicle2_new_time))
        if self.solution.solution_time < self.best_solution:
            self.best_solution = self.solution.solution_time
        self.set_tabu(best_move)
        self.beneficial_moves = []


class TabuOptimizerMemory(TabuOptimizer):
    def __init__(self, solution: Solution, limit: int, memory_limit):

        super().__init__(solution=solution, limit=limit, tabu_expander=0)
        self.tabu_memory: list[OptimizerMove] = []
        self.memory_limit = memory_limit

    def is_tabu(self, move: OptimizerMove) -> bool:
        return move in self.tabu_memory

    def set_tabu(self, best_move: OptimizerMove):
        self.tabu_memory.append(best_move)

    def manage_memory(self):
        if len(self.tabu_memory) > self.memory_limit:
            self.tabu_memory.pop(0)

    def apply_best_move(self):
        self.beneficial_moves.sort(key=lambda move: move.move_cost)
        best_move = self.beneficial_moves[0]
        self.apply_move(best_move.first_pos, best_move.second_pos, best_move.vehicle1, best_move.vehicle2)
        self.update_cache((best_move.vehicle1, best_move.vehicle1_new_time),
                          (best_move.vehicle2, best_move.vehicle2_new_time))
        if self.solution.solution_time < self.best_solution:
            self.best_solution = self.solution.solution_time
        self.set_tabu(best_move)
        self.manage_memory()
        self.beneficial_moves = []


class TwoOptTabuSearch(TabuOptimizer, TwoOptOptimizer):
    """Implementation of TwoOptTabu"""


class RelocTabuSearch(TabuOptimizer, ReLocatorOptimizer):
    """Implementation of Relocation Tabu Search"""


class SwapTabuSearch(TabuOptimizer, SwapMoveOptimizer):
    """Implementation of SwapMove Tabu Search"""


class TwoOptTabuSearchWithMemory(TabuOptimizerMemory, TwoOptOptimizer):
    """Implementation of TwoOptTabu"""


class ReLocTabuSearchWithMemory(TabuOptimizerMemory, ReLocatorOptimizer):
    """Implementation of TwoOptTabu"""
