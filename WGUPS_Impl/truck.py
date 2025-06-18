from package import Package
from hash_table import HashTable
from status import Status
from package_dispatch import PackageDispatch

import datetime
import pathlib
import csv

class Truck:
    def __init__(self, dispatcher: PackageDispatch):
        self.avg_speed: int = 18
        self.max_inventory: int = 16
        self.current_location = dispatcher.location
        self.dispatcher = dispatcher
        self.miles_driven = 0
        self.start_time = datetime.datetime.combine(datetime.date.today(), datetime.time(8, 0, 0, 0, None))
        self.current_time= self.start_time
        self.distance_data = self.get_distance_data()
        self.distance_index_map = self.get_distance_map()
        self.packages: list = []

    def get_distance_data(self):
        with open(pathlib.Path("C950---Submission\WGUPS_Impl\data\WGUPS_Distance_Table_Cleaned.csv"), newline="") as csvfile:
            reader = csv.reader(csvfile)
            return reader

    def get_distance_map(self):
        distance_index_map = {}
        index = 1
        for location in self.distance_data[0][1::]:
            distance_index_map[location.strip()] = index
            index += 1

        return distance_index_map
            
    def current_time_readable(self):
        return self.start_time + datetime.timedelta(seconds=self.current_seconds)
 
    def drop_off_package(self, package: Package):
        print(package)
        if package:
            package.status = Status.DELIVERED
            self.packages.remove(package)
        else:
            raise AttributeError(f"Package Not Found")

    def should_return_to_hub(self):
        return (len(self.packages) == 0 and self.dispatcher.has_available_packages())

    def load_packages(self):
        capacity_needed = self.max_inventory - len(self.packages)

        if self.current_location != self.dispatcher.location:
            distance_to_hub = self.get_distance(
                self.distance_index_map[self.current_location],
                self.distance_index_map[self.dispatcher.location],
            )
            self.move_truck(self.dispatcher.location, distance_to_hub)

        new_packages = self.dispatcher.get_packages_for_truck(self, capacity_needed)
        self.packages.extend(new_packages)
        return len(new_packages) > 0

    def move_truck(self, address: str, distance: float) -> int:
        print(f"Current Location: {self.current_location}")
        self.current_location = address
        self.miles_driven += distance
        self.current_time += datetime.timedelta(hours=distance / self.avg_speed)
        print(f"New Location: {self.current_location}")

    def get_distance(self, index_one, index_two) -> float:
        return float(self.distance_data[index_one][index_two])

    def do_rounds(self, distance_index_map: dict, distance_table: list):
        current_radius: int = 0
        while len(self.packages) > 0:
            candidates = []
            for pack in self.packages:
                distance = self.get_distance(distance_index_map[self.current_location], distance_index_map[pack.address], distance_table)
                if distance <= current_radius:
                    candidates.append((pack, distance))

            if candidates:
                best_pack, best_distance = min(candidates, key=lambda x: x[1])
                best_pack.status = Status.EN_ROUTE
                self.move_truck(best_pack.address, best_distance)
                self.drop_off_package(best_pack)
                print(self.current_time_readable())
            else:
                current_radius += 2
        
            
