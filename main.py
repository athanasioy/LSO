import random
import configparser
from typing import List

from map_objects.printer import Printer
from solver_objects.algorithm import BaseAlgo2, BetterAlgo, MinimumInsertions
from map_objects.mapmanager import MapManager
from map_objects.node import Node, Vehicle
from solver_objects.optimizer import SwapMoveOptimizer, ReLocatorOptimizer, TwoOptOptimizer, RemoveCrissCross
import solver_objects.combiners
from solver_objects.solution import Solution

from draw.ui import UI

config = configparser.ConfigParser()
config.read('config.ini')


def initialize_nodes(home_depot: Node) -> List[Node]:
    nodes_number = config.getint('OPTIONS', 'nodes')
    nodes = [home_depot]
    for i in range(nodes_number):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        dem = 100 * (1 + random.randint(1, 4))  # demand in kg

        n = Node(_id=i + 1,
                 x_cord=x,
                 y_cord=y,
                 demand=dem,
                 unloading_time=config.getint('OPTIONS', 'unloading_time'))
        nodes.append(n)
    return nodes


def initialize_vehicles(home_depot: Node) -> List[Vehicle]:
    vehicle_speed = config.getint('OPTIONS', 'vehicle_speed')
    num_of_vehicles = config.getint('OPTIONS', 'number_of_vehicles')
    vehicle_capacity = config.getint('OPTIONS', 'vehicle_capacity')
    unloading_time = config.getint('OPTIONS', 'unloading_time')
    vehicles = [Vehicle(_id=i, vehicle_speed=vehicle_speed,
                        vehicle_capacity=vehicle_capacity,
                        home_depot=home_depot,
                        unloading_time=unloading_time
                        ) for i in range(1, num_of_vehicles + 1)]

    return vehicles


def main(random_seed: int) -> None:
    random.seed(random_seed)
    home_depot = Node(_id=0, x_cord=50, y_cord=50, demand=0, unloading_time=15)
    home_depot.has_been_visited = True
    nodes = initialize_nodes(home_depot)
    vehicles = initialize_vehicles(home_depot)

    node_map = MapManager(nodes=nodes, vehicles=vehicles)
    solution = Solution(node_map)

    greedy_algo = MinimumInsertions(_map=node_map, solution=solution)
    # greedy_algo = BaseAlgo2(_map=node_map)
    # greedy_algo = BetterAlgo(_map = node_map)
    greedy_algo.run()

    solution.run_checks()
    solution.compute_service_time()
    #
    printer = Printer(solution)
    printer.print_solution()
    #
    sw = SwapMoveOptimizer(solution)
    rl = ReLocatorOptimizer(solution)
    twoOpt = TwoOptOptimizer(solution)
    cc = RemoveCrissCross(solution)
    ui2 = UI(home_depot=home_depot, customer_nodes=nodes, vehicles=node_map.vehicles)
    #
    vnd = solver_objects.combiners.VND()
    vnd.add_pipeline(sw)  # sw -> rl -> TwoOpt 259
    vnd.add_pipeline(rl)  # rl -> sw -> twoOpt 241 sw -> rl -> twoOpt 237
    vnd.add_pipeline(twoOpt)
    # TSTwoOpt = solver_objects.combiners.TwoOptTabuSearchWithMemory(solution, memory_limit=15, limit=500)
    # TSTwoOpt.run()
    vnd.run()
    # cc.run()
    #
    GLS = solver_objects.combiners.VNDGLS(random_seed=1, limit=2000, solution=solution)
    GLS.add_pipeline(sw)
    GLS.add_pipeline(rl)
    GLS.add_pipeline(twoOpt)
    # GLS.run()
    solution.compute_service_time()
    solution.run_checks()
    printer.print_solution()
    printer.print_vehicle_time()
    print(f"Solution time {solution.solution_time}")
    ui2.plot_routes()


if __name__ == "__main__":
    random_seed = config.getint('OPTIONS', 'RANDOM_SEED')
    main(random_seed)
