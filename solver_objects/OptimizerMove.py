from dataclasses import dataclass, field

from map_objects.node import Vehicle


@dataclass
class Move:
    first_pos: int
    second_pos: int
    vehicle1: Vehicle
    vehicle2: Vehicle
    distance_cost: float
    time_cost: float

    def __post_init__(self):
        self.move_cost = 1000*self.time_cost + self.distance_cost