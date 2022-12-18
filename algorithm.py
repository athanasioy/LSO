from typing import Protocol, Tuple, List

from mapmanager import MapManager
from node import Node, Vehicle


class Algorithm(Protocol):
    def find_next_nodes(self) -> Tuple[List[Node], List[Vehicle]]:
        pass


class BaseAlgo(Algorithm):

    def __init__(self, _map: MapManager):
        self.map = _map

    def run(self):
        end = False
        while not end:
            self.run_iteration()
            end = self.check_if_ended()

    def run_iteration(self):

        nodes, vehicles = self.find_next_nodes()

        for node, vehicle in zip(nodes, vehicles):
            if node:  # If the algo returns a node for said vehicle
                self.map.add_vehicle_route(vehicle, node)
                self.map.update_vehicle_position(vehicle)
                self.map.update_node(node)

    def find_next_nodes(self) -> Tuple[List[Node], List[Vehicle]]:
        vehicles_solution = []
        nodes_solution = []

        for vehicle in self.map.vehicles:
            if self.check_if_available_nodes_left():  # if no available nodes are left, return the solution
                return nodes_solution, vehicles_solution

            vehicles_solution.append(vehicle)

            nearest_node = self.find_nearest_node(vehicle)
            if nearest_node:  # if there is a nearest node available (we may run out of capacity)
                nearest_node.do_not_consider = True  # until we push the update to the map, do not use this node again

            nodes_solution.append(nearest_node)

        self.reset_consider_nodes()
        return nodes_solution, vehicles_solution

    def find_nearest_node(self, vehicle) -> Node:
        min_dist = 99999
        min_node = None

        for node in self.map.nodes:

            if node.do_not_consider or node.has_been_visited or not vehicle.has_enough_capacity(node_to_add=node):
                continue

            distance = self.map.compute_node_distance(vehicle.vehicle_position, node)
            if distance < min_dist:
                min_node = node
                min_dist = distance

        return min_node

    def reset_consider_nodes(self):
        for node in self.map.nodes:
            node.do_not_consider = False

    def check_if_available_nodes_left(self):
        return all((node.do_not_consider or node.has_been_visited) for node in self.map.nodes)

    def check_if_ended(self) -> bool:
        has_been_visited = [node.has_been_visited for node in self.map.nodes]
        return all(has_been_visited)  # if every node has been visited, return True


class BetterAlgo:

    def __init__(self, _map: MapManager):
        self.map = _map

    def run(self):
        end = False
        iterations = 0
        while not end:
            print(f"iteration {iterations}")
            self.run_iteration()
            end = self.check_if_ended()
            iterations += 1
            if iterations > 20:
                end = True

    def run_iteration(self):

        nodes, vehicles = self.find_next_nodes()
        for node, vehicle in zip(nodes, vehicles):
            if node:  # If the algo returns a node for said vehicle
                self.map.add_vehicle_route(vehicle, node)
                self.map.update_vehicle_position(vehicle)
                self.map.update_node(node)

    def find_next_nodes(self) -> Tuple[List[Node], List[Vehicle]]:
        vehicles_solution = []
        nodes_solution = []

        vehicle_nearest_nodes = []
        for vehicle in self.map.vehicles:
            nearest_node, min_dist = self.find_nearest_node(vehicle)
            vehicle_nearest_nodes.append((vehicle, nearest_node, min_dist))
        vehicle_nearest_nodes.sort(key=lambda x: x[2])  # Sort by distance

        for vehicle, node, dist in vehicle_nearest_nodes:
            if node is None:
                continue  # if find_nearest_node failed to find any node, skip

            if node.do_not_consider:
                next_best_node, dist = self.find_nearest_node(vehicle)

                if next_best_node is None:
                    continue

                next_best_node.do_not_consider = True
                vehicles_solution.append(vehicle)
                nodes_solution.append(next_best_node)
            else:
                vehicles_solution.append(vehicle)
                nodes_solution.append(node)
                node.do_not_consider = True

        self.reset_consider_nodes()
        return nodes_solution, vehicles_solution

    def find_nearest_node(self, vehicle: Vehicle) -> Tuple[Node, float]:
        min_dist = 99999
        min_node = None

        for node in self.map.nodes:

            if node.do_not_consider or node.has_been_visited or not vehicle.has_enough_capacity(
                    node_demand=node.demand) or not vehicle.in_radius_of(node):
                continue

            distance = self.map.compute_node_distance(vehicle.vehicle_position, node)
            if distance < min_dist:
                min_node = node
                min_dist = distance

        return min_node, min_dist

    def check_if_ended(self) -> bool:
        has_been_visited = [node.has_been_visited for node in self.map.nodes]
        return all(has_been_visited)  # if every node has been visited, return True

    def reset_consider_nodes(self):
        for node in self.map.nodes:
            node.do_not_consider = False


class BaseAlgo2:

    def __init__(self, _map: MapManager):
        self.map = _map

    def run(self):
        end = False
        c= 0
        while not end:
            self.run_iteration()
            end = self.check_if_ended()
            print(f"iteration {c}")
            c+=1
    def run_iteration(self):

        for vehicle in self.map.vehicles:

            node = self.find_next_nodes(vehicle)
            if node:
                self.map.add_vehicle_route(vehicle, node)
                self.map.update_vehicle_position(vehicle)
                self.map.update_node(node)

    def find_next_nodes(self, vehicle:Vehicle) -> Node:


        vehicle_pos = vehicle.vehicle_route.get_last_node()

        distances = self.map.distance_matrix.get(vehicle_pos)
        distances = {node:dist for node,dist in distances.items() if not node.has_been_visited and vehicle.has_enough_capacity(node.demand)}

        if not distances:
            return None

        nearest_node = min(distances, key=distances.get)

        return nearest_node


    def reset_consider_nodes(self):
        for node in self.map.nodes:
            node.do_not_consider = False

    def check_if_available_nodes_left(self):
        return all((node.do_not_consider or node.has_been_visited) for node in self.map.nodes)

    def check_if_ended(self) -> bool:
        has_been_visited = [node.has_been_visited for node in self.map.nodes]
        return all(has_been_visited)  # if every node has been visited, return True