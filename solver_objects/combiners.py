from draw.ui import UI
from solver_objects.move import OptimizerMove
from solver_objects.optimizer import ReLocatorOptimizer, TwoOptOptimizer, SwapMoveOptimizer
from solver_objects.OptimizerABC import Optimizer
from solver_objects.solution import Solution
from typing import List


class VND:
    def __init__(self, ui: UI):
        self.algos: List[Optimizer] = []
        self.ui = ui

    def add_pipeline(self, algo: Optimizer):
        self.algos.append(algo)

    def run(self):
        index = 0
        while index < len(self.algos):
            self.algos[index].generate_solution_space()
            if self.algos[index].beneficial_moves:
                print(index)
                old_time = self.algos[index].solution.solution_time
                self.algos[index].apply_best_move()
                new_time = self.algos[index].solution.solution_time
                # if self.ui and new_time<old_time:
                #     self.ui.save_plot(dir=r'C:\Users\aneme\PycharmProjects\LGO\images', name=f"{new_time}.png")
                index = 0
            else:
                index += 1

class TabuOptimizer(Optimizer):
    def __init__(self, solution: Solution, limit:int, tabu_expander:int):
        super().__init__(solution)
        self.iterator_limit = limit
        self.tabu_memory: list[OptimizerMove] = []
        self.counter = 0
        self.tabu_expander = tabu_expander
        self.best_solution = self.solution.solution_time

    def iterator_controller(self):
        return self.counter <= self.iterator_limit

    def handle_move(self, move: OptimizerMove):
        if not self.is_tabu(move) or move.time_cost < 0:
            self.add_move(move)

    def run(self):
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

    def set_tabu(self, best_move:OptimizerMove):
        best_move.vehicle1.vehicle_route.get_node_from_position(best_move.first_pos).tabu_iterator = self.counter + self.tabu_expander
        best_move.vehicle2.vehicle_route.get_node_from_position(best_move.second_pos).tabu_iterator = self.counter + self.tabu_expander

    def apply_best_move(self):
        self.beneficial_moves.sort(key=lambda move: move.move_cost)
        best_move = self.beneficial_moves[0]
        self.apply_move(best_move.first_pos, best_move.second_pos, best_move.vehicle1, best_move.vehicle2)
        self.update_cache(best_move.vehicle1, best_move.vehicle2)

        self.set_tabu(best_move)
        self.beneficial_moves = []


class TabuReloc(ReLocatorOptimizer):

    def __init__(self, solution: Solution, limit:int, tabu_expander:int):
        super().__init__(solution)
        self.iterator_limit = limit
        self.tabu_memory: list[OptimizerMove] = []
        self.counter = 0
        self.tabu_expander = tabu_expander

    def iterator_controller(self):
        return self.counter <= self.iterator_limit

    def handle_move(self, move: OptimizerMove):
        if not self.is_tabu(move) or move.move_cost < 0:
            self.add_move(move)

    def run(self):
        while self.iterator_controller():
            self.generate_solution_space()
            if self.beneficial_moves:
                self.apply_best_move()
            self.counter += 1
            print(f"iteration {self.counter}, {self.solution.solution_time}, {self.solution.compute_total_distance()}")

    def is_tabu(self, move: OptimizerMove) -> bool:
        node1 = move.vehicle1.vehicle_route.get_node_from_position(move.first_pos)
        node2 = move.vehicle2.vehicle_route.get_node_from_position(move.second_pos)

        return node1.tabu_iterator <= self.counter or node2.tabu_iterator <= self.counter

    def set_tabu(self, best_move:OptimizerMove):
        best_move.vehicle1.vehicle_route.get_node_from_position(best_move.first_pos).tabu_iterator = self.counter + self.tabu_expander
        best_move.vehicle2.vehicle_route.get_node_from_position(best_move.second_pos).tabu_iterator = self.counter + self.tabu_expander

    def apply_best_move(self):
        self.beneficial_moves.sort(key=lambda move: move.move_cost)
        best_move = self.beneficial_moves[0]
        self.apply_move(best_move.first_pos, best_move.second_pos, best_move.vehicle1, best_move.vehicle2)
        self.update_cache(best_move.vehicle1, best_move.vehicle2)
        self.set_tabu(best_move)
        self.beneficial_moves = []


class TwoOptTabuSearch(TabuOptimizer, TwoOptOptimizer):
    """Implementation of TwoOptTabu"""


class RelocTabuSearch(TabuOptimizer, ReLocatorOptimizer):
    """Implementation of Relocation Tabu Search"""


class SwapTabuSearch(TabuOptimizer, SwapMoveOptimizer):
    """Implementation of SwapMove Tabu Search"""
