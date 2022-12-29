from dataclasses import dataclass, field

from map_objects.node import Vehicle


@dataclass  # We need frozen=true so that dataclass in unmutable thus hashable
class Move:
    first_pos: int
    second_pos: int
    vehicle1: Vehicle
    vehicle2: Vehicle
    distance_cost: float
    time_cost: float

    def __post_init__(self):
        self.move_cost = 100000*self.time_cost + self.distance_cost