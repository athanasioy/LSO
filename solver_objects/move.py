from dataclasses import dataclass, field

from map_objects.node import Vehicle, Node


@dataclass
class OptimizerMove:
    first_pos: int
    second_pos: int
    vehicle1: Vehicle
    vehicle2: Vehicle
    distance_cost: float
    time_cost: float
    move_cost: float = field(init=False)

    def __post_init__(self):
        self.move_cost = 100000*self.time_cost + self.distance_cost


@dataclass
class MinimumInsertionMove:
    target_pos: int
    node_to_add: Node
    vehicle: Vehicle
    distance_cost: float
    time_cost: float
    move_cost: float = field(init=False)

    def __post_init__(self):
        self.move_cost = 100000 * self.time_cost + self.distance_cost
