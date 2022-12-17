import math
from typing import List

from mapmanager import MapManager
from node import Node, Vehicle


def compute_node_distance(node1: Node, node2: Node) -> float:
    return math.sqrt((node1.x_cord - node2.x_cord) ** 2 + (node1.y_cord - node2.y_cord) ** 2)


class Solution:

    def __init__(self, Map: MapManager):
        self.map = Map
        self.solution_time: float
        self.solution_time, self.slowest_vehicle = self.compute_service_time()

    def compute_service_time(self):
        max_time = 0
        slowest_vehicle = None
        for vehicle in self.map.vehicles:
            time = self.compute_route_time(vehicle)
            if time > max_time:
                max_time = time
                slowest_vehicle = vehicle

        return max_time, slowest_vehicle

    def check_solution(self):
        return self.check_capacity()

    def compute_route_time(self, vehicle: Vehicle):
        time_to_travel: float = 0
        for i in range(len(vehicle.vehicle_route.node_sequence) - 1):
            starting_node = vehicle.vehicle_route.node_sequence[i]
            destination_node = vehicle.vehicle_route.node_sequence[i + 1]

            dist = self.map.distance_matrix[(starting_node, destination_node)]

            time_to_travel += (dist / vehicle.vehicle_speed) * 60  # Convert to Minutes
            time_to_travel += vehicle.unloading_time

        return time_to_travel

    def check_capacity(self):
        return all(vehicle.vehicle_route.get_total_route_demand() <= 3000 for vehicle in self.map.vehicles)

    def duplicate_nodes(self):
        """
        Check if inside the route there are nodes that are visited two times
        :return:
        """
        for vehicle in self.map.vehicles:
            if len(vehicle.vehicle_route.node_sequence) != len(set(vehicle.vehicle_route.node_sequence)):
                print("PROBLEM WITH DUPLICATED NODES")
                return False
        print("ALL GOOD WITH DUPLICATE NODES")
        return True

    def check_multiple_visits(self):
        route_sets = [set(vehicle.vehicle_route.node_sequence) for vehicle in self.map.vehicles]
        intersections_between_routes = set().intersection(*route_sets)
        if len(intersections_between_routes) != 0:
            print("PROBLEM WITH MULTIPLE VISITS")
            print(route_sets)
            return False
        print("ALL GOOD WITH MULTIPLE VISITS")
        return True

