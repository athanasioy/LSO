import itertools
import math
from typing import List, Dict, Tuple

from node import Node, Vehicle

Node_Pair = Tuple[Node, Node]


class MapManager:
    def __init__(self, nodes: List[Node], vehicles: List[Vehicle]):
        self.nodes = nodes
        self.vehicles = vehicles

        self.distance_matrix: Dict[Node_Pair, float] = {}
        self.compute_distance_matrix()

    def add_vehicle_route(self, vehicle: Vehicle, node: Node):
        vehicle_index = self.vehicles.index(vehicle)
        self.vehicles[vehicle_index].vehicle_route.update_route(node)

    def update_vehicle_position(self, vehicle):
        vehicle_index = self.vehicles.index(vehicle)
        self.vehicles[vehicle_index].update_position()

    def update_node(self, node: Node):
        node_index = self.nodes.index(node)
        self.nodes[node_index].has_been_visited = True

    @staticmethod
    def compute_node_distance(node1: Node, node2: Node) -> float:
        return math.sqrt((node1.x_cord - node2.x_cord) ** 2 + (node1.y_cord - node2.y_cord) ** 2)

    def compute_distance_matrix(self):

        for node1, node2 in itertools.product(self.nodes, repeat=2):
            dist = self.compute_node_distance(node1, node2)

            self.distance_matrix.update({(node1, node2): dist})

    # def compute_time_matrix(self):
    #     for first_index in range(len(self.nodes)):
    #         for second_index in range(len(self.nodes)):
    #             distance = self.distance_matrix[first_index][second_index]
    #             self.time_matrix[first_index][second_index] = distance/40 * 60
    #
