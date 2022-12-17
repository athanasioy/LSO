from typing import List

import matplotlib.pyplot as plt

from node import Node, Vehicle


class UI:

    def __init__(self, home_depot: Node, customer_nodes: List[Node], vehicles: List[Vehicle]):
        self.home_depot = home_depot
        self.customer_nodes = customer_nodes
        self.vehicles = vehicles

    def plot_routes(self):

        fig, ax = plt.subplots(figsize=(8, 10))

        ax.scatter(self.home_depot.x_cord, self.home_depot.y_cord, c='red', s=35)

        for node in self.customer_nodes:
            ax.scatter(node.x_cord, node.y_cord, c='black', s=15)
            ax.text(node.x_cord, node.y_cord, s=node.demand)

        cmap = plt.colormaps['nipy_spectral']

        for index, vehicle in enumerate(self.vehicles):
            x_cords = []
            y_cords = []

            for i in range(len(vehicle.vehicle_route.node_sequence) - 1):
                x_cords += [node.x_cord for node in vehicle.vehicle_route.node_sequence[i: i + 2]]
                y_cords += [node.y_cord for node in vehicle.vehicle_route.node_sequence[i: i + 2]]

            ax.plot(x_cords, y_cords, color=cmap(index / len(self.vehicles)), linewidth=2, label=vehicle)
        ax.legend()
        plt.show()
