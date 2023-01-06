import random
import configparser
import time
from typing import List

from solver_objects.algorithm import BaseAlgo2, BetterAlgo, MinimumInsertions
from map_objects.mapmanager import MapManager
from map_objects.node import Node, Vehicle
from solver_objects.optimizer import SwapMoveOptimizer, ReLocatorOptimizer, TwoOptOptimizer
from solver_objects.combiners import VND, TabuReloc
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


def main() -> None:
    random.seed(5)
    home_depot = Node(_id=0, x_cord=50, y_cord=50, demand=0, unloading_time=0)
    home_depot.has_been_visited = True
    nodes = initialize_nodes(home_depot)
    vehicles = initialize_vehicles(home_depot)

    node_map = MapManager(nodes=nodes, vehicles=vehicles)
    # base_algo = BaseAlgo2(_map=node_map)
    minins = MinimumInsertions(_map= node_map)
    start_time = time.time()
    minins.run()
    end_time = time.time()
    for vehicle in node_map.vehicles:
        print(vehicle, vehicle.vehicle_route.get_total_route_demand())

    solution = Solution(node_map)
    solution.run_checks()

    service_time, slowest_vehicle = solution.compute_service_time()

    print(f"Algorithm finished in {end_time - start_time} seconds")
    print(f"Solution Time {service_time}, total distance {solution.compute_total_distance()}")
    print(f"Slowest Vehicle was {slowest_vehicle} with route {slowest_vehicle.vehicle_route}")
    print(f"Slowest Route total demand {slowest_vehicle.vehicle_route.get_total_route_demand()}")
    print(f"Slowest Route Total Distance {slowest_vehicle.vehicle_route.get_total_distance()}")


    sw = SwapMoveOptimizer(solution)
    rl = ReLocatorOptimizer(solution)

    twoOpt = TwoOptOptimizer(solution)
    vnd = VND()
    vnd.add_pipeline(sw) # sw -> rl -> TwoOpt 259
    vnd.add_pipeline(rl) # rl -> sw -> twoOpt 241 sw -> rl -> twoOpt 237
    vnd.add_pipeline(twoOpt)
    #
    vnd.run()

    end_time = time.time()
    service_time, slowest_vehicle = solution.compute_service_time()
    solution.run_checks()
    print(f"Algorithm and Optimizer finished in {end_time - start_time} seconds")
    print(f"Solution Time {service_time}, total distance {solution.compute_total_distance()}")
    print(f"Slowest Vehicle was {slowest_vehicle} with route {slowest_vehicle.vehicle_route}")
    print(f"Slowest Route total demand {slowest_vehicle.vehicle_route.get_total_route_demand()}")
    print(f"Slowest Route Total Distance {slowest_vehicle.vehicle_route.get_total_distance()}")
    # for vehicle in solution.map.vehicles:
    #     print(f"{vehicle},{vehicle.vehicle_route}")


    ui2 = UI(home_depot=home_depot, customer_nodes=nodes, vehicles=solution.map.vehicles)
    ui2.plot_routes()


if __name__ == "__main__":
    main()
