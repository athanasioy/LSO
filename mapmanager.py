import itertools
import math
from typing import List, Dict, Tuple

from node import Node, Vehicle



class MapManager:
    def __init__(self, nodes: List[Node], vehicles: List[Vehicle]):
        self.nodes = nodes
        self.vehicles = vehicles

        self.distance_matrix: Dict[Node, Dict[Node, float]] = {}
        self.compute_distance_matrix()
        for vehicle in self.vehicles:
            vehicle.compute_time_matrix(distance_matrix=self.distance_matrix)

    def add_vehicle_route(self, vehicle: Vehicle, node: Node):
        vehicle_index = self.vehicles.index(vehicle)
        self.vehicles[vehicle_index].vehicle_route.update_route(node)

    def update_vehicle_position(self, vehicle):
        vehicle_index = self.vehicles.index(vehicle)
        self.vehicles[vehicle_index].update_position()

    def update_node(self, node: Node):
        node_index = self.nodes.index(node)
        self.nodes[node_index].has_been_visited = True

    def update_cumul_costs(self):
        for vehicle in self.vehicles:
            vehicle.vehicle_route.update_cumul_distance_cost()
            vehicle.update_cumul_time_cost()

    @staticmethod
    def compute_node_distance(node1: Node, node2: Node) -> float:
        return math.sqrt((node1.x_cord - node2.x_cord) ** 2 + (node1.y_cord - node2.y_cord) ** 2)

    def compute_distance_matrix(self):

        for node1, node2 in itertools.product(self.nodes, repeat=2):
            dist = self.compute_node_distance(node1, node2)

            if not self.distance_matrix.get(node1): # is None:
                self.distance_matrix[node1] = {}

            self.distance_matrix.get(node1).update({node2:dist})

    #
