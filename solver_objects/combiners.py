from solver_objects.move import OptimizerMove
from solver_objects.optimizer import ReLocatorOptimizer
from solver_objects.OptimizerABC import Optimizer
from solver_objects.solution import Solution
from typing import List


class VND:
    def __init__(self):
        self.algos: List[Optimizer] = []

    def add_pipeline(self, algo: Optimizer):
        self.algos.append(algo)

    def run(self):
        index = 0
        while index < len(self.algos):
            print(index)
            self.algos[index].generate_solution_space()
            if self.algos[index].beneficial_moves:
                self.algos[index].apply_best_move()
                index = 0
            else:
                index += 1


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
            print(f"iteration reloc {self.counter}, {self.solution.solution_time}")

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



