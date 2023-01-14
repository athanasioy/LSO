from solver_objects.solution import Solution


class Printer:
    def __init__(self, solution: Solution):
        self.solution = solution

    def print_solution(self):
        print("Objective:")
        print(f"{self.solution.solution_time/60:.5} hr")
        print("Routes:")
        print(f"{len(self.solution.map.vehicles)}")
        print("Route Summary:")
        for vehicle in self.solution.map.vehicles:
            node_id = map(lambda x: str(x.id), vehicle.vehicle_route.node_sequence)
            print(','.join(node_id))

    def print_vehicle_time(self):
        for vehicle in self.solution.map.vehicles:
            print(f"{vehicle},{vehicle.get_route_service_time()}")

    def print_vehicle_demand(self):
        for vehicle in self.solution.map.vehicles:
            print(f"{vehicle},{vehicle.vehicle_route.cumul_demand[-1]}")
