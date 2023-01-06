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


class Algorithm(Protocol):
    def find_next_nodes(self) -> Tuple[List[Node], List[Vehicle]]:
        pass