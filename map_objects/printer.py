from solver_objects.solution import Solution


class Printer:
    def __init__(self, solution: Solution):
        self.solution = solution

    def print_solution(self):
        lines = []

        print("Objective:")
        lines.append("Objective:"+"\n")
        print(f"{self.solution.solution_time/60:.5} hr")
        lines.append(f"{self.solution.solution_time/60:.5} hr"+"\n")
        print("Routes:")
        lines.append("Routes:"+"\n")
        print(f"{len(self.solution.map.vehicles)}")
        lines.append(f"{len(self.solution.map.vehicles)}"+"\n")
        print("Route Summary:")
        lines.append("Route Summary:"+"\n")
        for vehicle in self.solution.map.vehicles:
            node_id = [str(x.id) for x in vehicle.vehicle_route.node_sequence]
            print(','.join(node_id))
            r = ','.join(node_id)
            lines.append(r+"\n")
        print(lines)
        with open('solution.txt', 'w') as f:
            f.writelines(lines)


    def print_vehicle_time(self):
        for vehicle in self.solution.map.vehicles:
            print(f"{vehicle},{vehicle.get_route_service_time()}")

    def print_vehicle_demand(self):
        for vehicle in self.solution.map.vehicles:
            print(f"{vehicle},{vehicle.vehicle_route.cumul_demand[-1]}")
