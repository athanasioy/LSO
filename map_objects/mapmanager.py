import itertools
import math
from copy import deepcopy
from typing import List, Dict

from map_objects.node import Node, Vehicle


class MapManager:
    def __init__(self, nodes: List[Node], vehicles: List[Vehicle]):
        self.nodes = nodes
        self.vehicles = vehicles
        self.depot = vehicles[0].vehicle_route.node_sequence[0]  # save depot on mapManager
        self.distance_matrix: Dict[Node, Dict[Node, float]] = {}
        self.penalized_distance_matrix: Dict[Node, Dict[Node, float]] = {}
        self.compute_distance_matrix()
        for vehicle in self.vehicles:
            vehicle.compute_time_matrix(distance_matrix=self.distance_matrix)
            vehicle.penalized_time_matrix = vehicle.time_matrix.copy()

    @staticmethod
    def add_vehicle_route(vehicle: Vehicle, node: Node):
        vehicle.vehicle_route.update_route(node)

    @staticmethod
    def insert_vehicle_route(vehicle: Vehicle, node: Node, idx: int):
        vehicle.vehicle_route.node_sequence.insert(idx, node)

    @staticmethod
    def update_vehicle_position(vehicle):
        vehicle.update_position()

    @staticmethod
    def update_node(node: Node):
        node.has_been_visited = True

    def update_cumul_costs(self):
        """Update cached distance and time costs"""
        for vehicle in self.vehicles:
            vehicle.vehicle_route.update_cumul_distance_cost()
            vehicle.update_cumul_time_cost()

    @staticmethod
    def compute_node_distance(node1: Node, node2: Node) -> float:
        return math.sqrt((node1.x_cord - node2.x_cord) ** 2 + (node1.y_cord - node2.y_cord) ** 2)

    def compute_distance_matrix(self):

        for node1, node2 in itertools.product(self.nodes, repeat=2):
            dist = self.compute_node_distance(node1, node2)

            if not self.distance_matrix.get(node1):  # is None:
                self.distance_matrix[node1] = {}

            if not self.penalized_distance_matrix.get(node1):
                self.penalized_distance_matrix[node1] = {}

            self.distance_matrix.get(node1).update({node2: dist})
            self.penalized_distance_matrix.get(node1).update({node2: dist})

