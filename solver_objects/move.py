from dataclasses import dataclass, field
from enum import Enum, auto

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
    vehicle1_new_time: float
    vehicle2_new_time: float

    def __post_init__(self):
        self.move_cost = 1000 * self.time_cost + self.distance_cost

    def __eq__(self, other):
        return (self.first_pos, self.second_pos, self.vehicle1, self.vehicle2) == (
            other.first_pos, other.second_pos, other.vehicle1, other.vehicle2)


@dataclass
class MinimumInsertionMove:
    target_pos: int
    node_to_add: Node
    vehicle: Vehicle
    distance_cost: float
    time_cost: float
    move_cost: float = field(init=False)

    def __post_init__(self):
        self.move_cost = 1000 * self.time_cost + self.distance_cost


class DistanceType(Enum):
    NORMAL = auto()
    PENALIZED = auto()


@dataclass
class TSPMove:
    first_pos: int
    second_pos: int
    vehicle: Vehicle
    cost: float
