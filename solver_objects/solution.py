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
        self.vehicle_times: dict[Vehicle, float] = {}
        self.solution_time, self.slowest_vehicle = self.compute_service_time()  # update self.solution_time and slowest_vehicle

    def compute_service_time(self) -> Tuple[float, Vehicle]:
        max_time = 0
        slowest_vehicle = None
        for vehicle in self.map.vehicles:
            time = self.compute_route_time(vehicle)
            self.vehicle_times.update({vehicle: time})

        slowest_vehicle = max(self.vehicle_times, key=lambda x: self.vehicle_times.get(x))

        self.slowest_vehicle = slowest_vehicle
        self.solution_time = self.vehicle_times.get(slowest_vehicle)
        return max_time, slowest_vehicle

    @staticmethod
    def compute_route_time(vehicle: Vehicle) -> float:
        time_to_travel: float = 0
        for i in range(len(vehicle.vehicle_route.node_sequence) - 1):
            starting_node = vehicle.vehicle_route.node_sequence[i]
            destination_node = vehicle.vehicle_route.node_sequence[i + 1]

            time_to_travel += vehicle.time_matrix.get(starting_node).get(destination_node)

        return time_to_travel

    def compute_total_distance(self) -> float:
        tot_distance = 0.0
        for vehicle in self.map.vehicles:
            for i in range(len(vehicle.vehicle_route.node_sequence) - 1):
                starting_node = vehicle.vehicle_route.node_sequence[i]
                destination_node = vehicle.vehicle_route.node_sequence[i + 1]
                tot_distance += self.map.distance_matrix.get(starting_node).get(destination_node)
        return tot_distance

    def check_capacity(self) -> None:
        """check all routes capacity"""
        if all(vehicle.vehicle_route.get_total_route_demand() <= vehicle.vehicle_capacity for vehicle in self.map.vehicles):
            print('all good with capacity')
            return

        for vehicle in self.map.vehicles:
            if vehicle.vehicle_route.get_total_route_demand() > vehicle.vehicle_capacity:
                raise ValueError(f"Vehicle {vehicle} exceeds total capacity {vehicle.vehicle_capacity} with {vehicle.vehicle_route.get_total_route_demand()}  ")

    def duplicate_nodes(self) -> None:
        """Check if inside the route there are nodes that are visited two times"""
        for vehicle in self.map.vehicles:
            if len(vehicle.vehicle_route.node_sequence) != len(set(vehicle.vehicle_route.node_sequence)):
                print(vehicle)
                print(vehicle.vehicle_route)
                raise ValueError("Problem with duplicated nodes")
        print("ALL GOOD WITH DUPLICATE NODES")

    def check_multiple_visits(self) -> None:
        """Check if node is visited multiple times"""
        route_sets = [set(vehicle.vehicle_route.node_sequence[1:]) for vehicle in self.map.vehicles]
        intersections_between_routes = set.intersection(*route_sets)
        if len(intersections_between_routes) != 0:
            print(intersections_between_routes)
            print(route_sets)
            raise ValueError("Mutlpile Visits on routes")
        print("ALL GOOD WITH MULTIPLE VISITS")

    def all_routes_start_from_depot(self) -> None:
        for vehicle in self.map.vehicles:
            if vehicle.vehicle_route.node_sequence[0] != self.map.depot:
                raise ValueError(f'vehicle {vehicle} does not start from depot! {vehicle.vehicle_route}')
        print('all nodes start from depot')

    def run_checks(self) -> None:
        self.duplicate_nodes()
        self.check_multiple_visits()
        self.check_capacity()
        self.all_routes_start_from_depot()


