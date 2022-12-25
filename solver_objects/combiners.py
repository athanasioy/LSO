from solver_objects.optimizer import Optimizer


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
            elif counter > 150:
                break
            else:
                index = 0  # Reset the index


