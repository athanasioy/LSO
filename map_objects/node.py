import itertools
import math
from typing import List, Tuple, Dict


class Node:

    def __init__(self, _id: int, x_cord: int, y_cord: int, demand: int, unloading_time: int):
        self.id = _id
        self.x_cord = x_cord
        self.y_cord = y_cord
        self.demand = demand
        self.unloading_time = unloading_time
        self.has_been_visited = False
        self.do_not_consider = False

    def __repr__(self):
        return f"id: {self.id}"


class Route:
    def __init__(self, depot: Node):
        self.node_sequence: List[Node] = [depot]
        self.total_time = 0.0
        self.total_distance = 0.0
        self.cumul_cost = []
        self.cumul_time_cost = []

    def get_total_route_demand(self):
        return sum((node.demand for node in self.node_sequence))

    def update_cumul_distance_cost(self):
        self.cumul_cost = list(itertools.accumulate([node.demand for node in self.node_sequence]))

    def update_route(self, node: Node):
        self.node_sequence.append(node)

    def get_last_node(self) -> Node:
        return self.node_sequence[-1]

    def get_node_from_position(self, index: int) -> Node:
        return self.node_sequence[index]

    def _get_previous_node_from_position(self, index: int) -> Node:
        return self.node_sequence[index - 1]

    def _get_next_node_from_position(self, index: int) -> Node:
        # print(f"index is {index}")
        # print(f"index +1 is {index+1}")
        # print(f"len of route is {len(self.node_sequence)}")
        # print(index, len(self.node_sequence))
        if index >= (len(self.node_sequence)-1):
            return self.node_sequence[index]
        return self.node_sequence[index + 1]

    def get_adjacent_nodes(self, index: int) -> Tuple[Node, Node, Node]:
        return self._get_previous_node_from_position(index),\
               self.get_node_from_position(index),\
               self._get_next_node_from_position(index)

    def get_total_distance(self):

        def compute_node_distance(node1: Node, node2: Node) -> float:
            return math.sqrt((node1.x_cord - node2.x_cord) ** 2 + (node1.y_cord - node2.y_cord) ** 2)

        total_distance = 0
        for i in range(len(self.node_sequence) - 1):
            starting_node = self.node_sequence[i]
            destination_node = self.node_sequence[i + 1]

            total_distance += compute_node_distance(starting_node, destination_node)

        return total_distance

    def __repr__(self):
        string = ""
        for node in self.node_sequence:
            string += str(node.id)
            string += "-->"
        string += "END"
        return string


class Vehicle:
    def __init__(self, _id: int, vehicle_speed: int, vehicle_capacity: int, home_depot: Node, unloading_time: int):
        self.id = _id
        self.vehicle_speed = vehicle_speed
        self.vehicle_position: Node = home_depot  # Every vehicle starts at home depot
        self.vehicle_route = Route(home_depot)
        self.vehicle_capacity = vehicle_capacity
        self.unloading_time = unloading_time
        self.time_matrix: Dict[Node, Dict[Node, float]] = {}

    def update_position(self):
        self.vehicle_position = self.vehicle_route.get_last_node()

    def update_cumul_time_cost(self):
        self.vehicle_route.cumul_time_cost = []
        time = 0
        self.vehicle_route.cumul_time_cost.append(time)

        for i in range(len(self.vehicle_route.node_sequence) - 1):
            starting_node = self.vehicle_route.node_sequence[i]
            destination_node = self.vehicle_route.node_sequence[i + 1]

            time += self.time_matrix.get(starting_node).get(destination_node)
            self.vehicle_route.cumul_time_cost.append(time)



    def has_enough_capacity(self, node_demand: int) -> bool:
        """
        Method that checks if we can service the node.
        Returns true if the node to be added can be serviced by the vehicle
        :param node_demand: demand to be added
        :return: bool
        """
        return node_demand + self.vehicle_route.get_total_route_demand() <= self.vehicle_capacity

    def in_radius_of(self, node: Node) -> bool:
        """
        checks if node is inside a specified radius of vehicle
        :param node:
        :return: bool
        """
        x_dist = math.pow(node.x_cord - self.vehicle_position.x_cord, 2)
        y_dist = math.pow(node.y_cord - self.vehicle_position.y_cord, 2)
        return x_dist + y_dist <= 10000

    def __repr__(self):
        return f"ID {self.id}"

    def compute_time_matrix(self, distance_matrix: Dict[Node, Dict[Node, float]]):
        for starting_node in distance_matrix:
            for destination_node in distance_matrix.get(starting_node):
                dist = distance_matrix.get(starting_node).get(destination_node)
                time_to_travel = (dist / self.vehicle_speed) * 60  # Convert to Minutes
                time_to_travel += destination_node.unloading_time

                if self.time_matrix.get(starting_node) is None:
                    self.time_matrix[starting_node] = {}

                self.time_matrix.get(starting_node).update({destination_node:time_to_travel})


    def get_route_service_time(self):
        service_time = 0
        for i in range(len(self.vehicle_route.node_sequence) - 1):
            starting_node = self.vehicle_route.node_sequence[i]
            destination_node = self.vehicle_route.node_sequence[i + 1]

            time = self.time_matrix.get(starting_node).get(destination_node)
            service_time += time

        return service_time



