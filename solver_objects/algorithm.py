import random
from typing import Protocol, Tuple, List

from map_objects.mapmanager import MapManager
from map_objects.node import Node, Vehicle
from solver_objects.move import MinimumInsertionMove
from solver_objects.solution import Solution


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
                    node_demand=node.demand):
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
        c = 0
        while not end:
            self.run_iteration()
            end = self.check_if_ended()
            print(f"iteration {c}")
            c += 1

    def run_iteration(self):

        for vehicle in self.map.vehicles:

            node = self.find_next_nodes(vehicle)
            if node:
                self.map.add_vehicle_route(vehicle, node)
                self.map.update_vehicle_position(vehicle)
                self.map.update_node(node)

    def find_next_nodes(self, vehicle: Vehicle) -> Node:

        vehicle_pos = vehicle.vehicle_route.get_last_node()

        distances = self.map.distance_matrix.get(vehicle_pos)
        distances = {node: dist for node, dist in distances.items() if
                     not node.has_been_visited and vehicle.has_enough_capacity(node.demand)}

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


class MinimumInsertions:

    def __init__(self, _map: MapManager, solution: Solution):
        self.map = _map
        self.solution = solution
        self.solution.compute_service_time()
        self.map.update_cumul_costs()
        self.insertions = 0

    def run(self):

        while self.insertions < len(self.map.nodes) - 1:
            self.run_iteration()
            print(self.insertions)

    def run_iteration(self):

        best_move: MinimumInsertionMove = self.find_next_best_move()
        if best_move:
            self.apply_move(best_move)
            self.insertions += 1

    def find_next_best_move(self) -> MinimumInsertionMove:
        min_cost = 10 ** 9
        best_move = None
        for node in self.map.nodes:
            if node.do_not_consider or node.has_been_visited:
                continue

            for vehicle in self.map.vehicles:
                if not vehicle.has_enough_capacity(node.demand):
                    continue

                for j in range(len(vehicle.vehicle_route.node_sequence)):
                    _, target_node, c = vehicle.vehicle_route.get_adjacent_nodes(j)
                    distance_added, distance_removed = self.determine_distance_costs(target_node, c, node, vehicle)
                    distance_cost = distance_added - distance_removed
                    time_cost = self.determine_time_cost(target_node, c, node, vehicle)

                    move = MinimumInsertionMove(
                        target_pos=j, vehicle=vehicle, distance_cost=distance_cost, time_cost=time_cost,
                        node_to_add=node
                    )

                    if best_move is None:
                        best_move = move
                        min_cost = move.move_cost

                    if move.move_cost < min_cost:
                        best_move = move
                        min_cost = move.move_cost

        return best_move

    def determine_distance_costs(self, target_node: Node, c: Node, node_to_add: Node, vehicle: Vehicle):

        distance_removed = self.map.distance_matrix.get(target_node).get(c)
        if target_node == vehicle.vehicle_route.node_sequence[-1]:  # if last node in sequence
            distance_added = self.map.distance_matrix.get(target_node).get(node_to_add)
        else:
            distance_added = self.map.distance_matrix.get(target_node).get(node_to_add)
            distance_added += self.map.distance_matrix.get(node_to_add).get(c)

        return distance_added, distance_removed

    def determine_time_cost(self, target_node, c, node_to_add, vehicle):
        time_removed = self.map.distance_matrix.get(target_node).get(c)

        if target_node == vehicle.vehicle_route.node_sequence[-1]:  # if last node in sequence
            time_added = vehicle.time_matrix.get(target_node).get(node_to_add)
        else:
            time_added = vehicle.time_matrix.get(target_node).get(node_to_add)
            time_added += vehicle.time_matrix.get(node_to_add).get(c)

        new_vehicle_time = vehicle.vehicle_route.cumul_time_cost[-1] + time_added - time_removed

        new_solution_time = self.determine_new_solution_time((vehicle, new_vehicle_time))

        return new_solution_time - self.solution.solution_time

    def apply_move(self, best_move: MinimumInsertionMove):
        self.map.insert_vehicle_route(best_move.vehicle, best_move.node_to_add, best_move.target_pos + 1)

        self.solution.compute_service_time()  # update slowest Vehicle
        best_move.vehicle.update_cumul_time_cost()  # update cumulative costs
        best_move.node_to_add.has_been_visited = True

    def determine_new_solution_time(self, *args: tuple[Vehicle, float]) -> float:
        """
        Compute on the fly new solution time by copying dictionaries of vehicle times
        Returns a float that represents new slowest route
        """
        vehicle_times_copy = self.solution.vehicle_times.copy()

        for vehicle, time in args:
            vehicle_times_copy.update({vehicle: time})
        slowest_vehicle = max(vehicle_times_copy, key=lambda x: vehicle_times_copy.get(x))
        return vehicle_times_copy.get(slowest_vehicle)


class MinimumInsertionsRCL(MinimumInsertions):
    def __init__(self, _map: MapManager, solution: Solution, k=3):
        super().__init__(_map, solution)
        self.RCL = k
        random.seed(2)

    def find_next_best_move(self) -> MinimumInsertionMove:

        best_moves = []
        for node in self.map.nodes:
            if node.do_not_consider or node.has_been_visited:
                continue

            for vehicle in self.map.vehicles:
                if not vehicle.has_enough_capacity(node.demand):
                    continue

                for j in range(len(vehicle.vehicle_route.node_sequence)):
                    _, target_node, c = vehicle.vehicle_route.get_adjacent_nodes(j)
                    distance_added, distance_removed = self.determine_distance_costs(target_node, c, node, vehicle)
                    distance_cost = distance_added - distance_removed
                    time_cost = self.determine_time_cost(target_node, c, node, vehicle)

                    move = MinimumInsertionMove(
                        target_pos=j, vehicle=vehicle, distance_cost=distance_cost, time_cost=time_cost,
                        node_to_add=node
                    )

                    best_moves.append(move)
        best_moves.sort(key= lambda move: move.move_cost)
        k = random.randint(0,self.RCL)
        return best_moves[k]

class NearestNeighborRCL:
    pass

class MinimumInsertionsTree(MinimumInsertions):
    def __init__(self, _map: MapManager, solution: Solution, tree_depth, candidate_moves: int):
        super().__init__(_map, solution)
        self.tree_depth = tree_depth
        self.candidate_moves = candidate_moves
        self.depth = -1

    def run_iteration(self):
        self.depth = 0
        best_moves: list[MinimumInsertionMove] = self.find_next_best_move()
        for best_move in best_moves and self.depth <= self.tree_depth:
            self.depth += 1
            nodes_copy
            routes_copy = self.map.vehicles.copy()

    def find_next_best_move(self) -> list[MinimumInsertionMove]:

        best_move = None
        best_moves = []
        for node in self.map.nodes:
            if node.do_not_consider or node.has_been_visited:
                continue

            for vehicle in self.map.vehicles:
                if not vehicle.has_enough_capacity(node.demand):
                    continue

                for j in range(len(vehicle.vehicle_route.node_sequence)):
                    _, target_node, c = vehicle.vehicle_route.get_adjacent_nodes(j)
                    distance_added, distance_removed = self.determine_distance_costs(target_node, c, node, vehicle)
                    distance_cost = distance_added - distance_removed
                    time_cost = self.determine_time_cost(target_node, c, node, vehicle)

                    move = MinimumInsertionMove(
                        target_pos=j, vehicle=vehicle, distance_cost=distance_cost, time_cost=time_cost,
                        node_to_add=node
                    )

                    best_moves.append(move)
        best_moves.sort(key=lambda x: x.move_cost)

        return best_moves[:self.candidate_moves]
