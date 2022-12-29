from solver_objects.OptimizerMove import Move
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
        self.tabu_expander = tabu_expander
        self.tabu_memory = set()
    def iterator_controller(self):
        return self.c <= self.iterator_limit

    def handle_move(self, first_pos, second_pos, vehicle1, vehicle2, cost, time_impact):
        if not self.isTabu(Move(first_pos=first_pos, second_pos=second_pos, vehicle1=vehicle1, vehicle2=vehicle2,
                 distance_cost=cost, time_cost=time_impact)
        ):
            self.add_move(
                Move(first_pos=first_pos, second_pos=second_pos, vehicle1=vehicle1, vehicle2=vehicle2,
                     distance_cost=cost, time_cost=time_impact)
            )

    def run(self):
        self.c = 0
        while self.iterator_controller():
            self.generate_solution_space()
            self.best_sol_time = 100000
            if self.beneficial_moves:
                self.beneficial_moves.sort(key=lambda move: move.move_cost())

                best_move = self.beneficial_moves[0]
                self.apply_move(best_move.first_pos, best_move.second_pos, best_move.vehicle1, best_move.vehicle2)
                self.add_move_to_memory(best_move)
                self.set_tabu(best_move)
                self.beneficial_moves = []  # clear moves
                new_service_time, _ = self.solution.compute_service_time()
                if new_service_time<self.best_sol_time:
                    self.best_sol_time = new_service_time
            self.c += 1
            print(f"iteration reloc {self.c}, {self.solution.solution_time}, {self.solution.compute_total_distance()}")
        return self.c

    def set_tabu(self, best_move):
        best_move.vehicle1.vehicle_route.node_sequence[best_move.first_pos].tabu_iterator += self.tabu_expander
        best_move.vehicle2.vehicle_route.node_sequence[best_move.second_pos].tabu_iterator += self.tabu_expander

    def isTabu(self, move: Move) -> bool:

        return move in self.tabu_memory

    def add_move_to_memory(self, best_move:Move):
        self.tabu_memory.add(best_move)


