import math
from typing import Tuple
from map_objects.mapmanager import MapManager
from map_objects.node import Node, Vehicle


def compute_node_distance(node1: Node, node2: Node) -> float:
    return math.sqrt((node1.x_cord - node2.x_cord) ** 2 + (node1.y_cord - node2.y_cord) ** 2)


class Solution:

    def __init__(self, Map: MapManager):
        self.map = Map
        self.solution_time: float
        self.solution_time,self.slowest_vehicle = self.compute_service_time() # update self.solution_time and slowest_vehicle

    def compute_service_time(self) -> Tuple[float, Vehicle]:
        max_time = 0
        slowest_vehicle = None
        for vehicle in self.map.vehicles:
            time = self.compute_route_time(vehicle)

            if slowest_vehicle is None:
                slowest_vehicle = vehicle
                max_time = time

            if time > max_time:
                max_time = time
                slowest_vehicle = vehicle

        self.slowest_vehicle = slowest_vehicle
        self.solution_time = max_time
        return max_time, slowest_vehicle

    def compute_route_time(self, vehicle: Vehicle):
        time_to_travel: float = 0
        for i in range(len(vehicle.vehicle_route.node_sequence) - 1):
            starting_node = vehicle.vehicle_route.node_sequence[i]
            destination_node = vehicle.vehicle_route.node_sequence[i + 1]

            time_to_travel += vehicle.time_matrix.get(starting_node).get(destination_node)

        return time_to_travel

    def compute_total_distance(self):
        tot_distance = 0.0
        for vehicle in self.map.vehicles:
            for i in range(len(vehicle.vehicle_route.node_sequence) - 1):
                starting_node = vehicle.vehicle_route.node_sequence[i]
                destination_node = vehicle.vehicle_route.node_sequence[i + 1]
                tot_distance += self.map.distance_matrix.get(starting_node).get(destination_node)
        return tot_distance
    def check_capacity(self):
        return all(vehicle.vehicle_route.get_total_route_demand() <= 3000 for vehicle in self.map.vehicles)

    def duplicate_nodes(self):
        """
        Check if inside the route there are nodes that are visited two times
        :return:
        """
        for vehicle in self.map.vehicles:
            if len(vehicle.vehicle_route.node_sequence) != len(set(vehicle.vehicle_route.node_sequence)):
                print(vehicle)
                print(vehicle.vehicle_route)
                raise ValueError("Problem with duplicated nodes")
                return False
        print("ALL GOOD WITH DUPLICATE NODES")
        return True

    def check_multiple_visits(self):
        route_sets = [set(vehicle.vehicle_route.node_sequence[1:]) for vehicle in self.map.vehicles]
        intersections_between_routes = set.intersection(*route_sets)
        if len(intersections_between_routes) != 0:
            print(intersections_between_routes)
            print(route_sets)
            raise ValueError("Mutlpile Visits on routes")
        print("ALL GOOD WITH MULTIPLE VISITS")
        return True

    def run_checks(self):
        self.duplicate_nodes()
        self.check_multiple_visits()
        self.check_capacity()
        self.all_routes_start_from_depot()

    def all_routes_start_from_depot(self):
        for vehicle in self.map.vehicles:
            if vehicle.vehicle_route.node_sequence[0].id != 0:
                raise ValueError(f'vehicle {vehicle} does not start from depot! {vehicle.vehicle_route}')
