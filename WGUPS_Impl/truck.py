from package import Package
from package_dispatch import PackageDispatch

import datetime
import pathlib
import csv
import logging

class Truck:
    def __init__(self, dispatcher: PackageDispatch, truckId: str, start_time: datetime):
        self.avg_speed: int = 18
        self.max_inventory: int = 16
        self.truckId = truckId
        self.current_location = dispatcher.location
        self.dispatcher = dispatcher
        self.miles_driven = 0
        self.start_time = start_time
        self.current_time= self.start_time
        self.delayed_truck = False

        # Create Distance Data
        self.distance_data = self.get_distance_data()
        self.distance_index_map = self.get_distance_map()
        self.packages: list = []

    def get_distance_data(self):
        with open(pathlib.Path("C950---Submission\WGUPS_Impl\data\WGUPS_Distance_Table_Cleaned.csv"), newline="") as csvfile:
            reader = csv.reader(csvfile)
            return list(reader)

    def get_distance_map(self):
        distance_index_map = {}
        for index, location in enumerate(self.distance_data[0][1::], 1):
            distance_index_map[location.strip()] = index
        return distance_index_map
            
    def current_time_readable(self):
        return self.current_time.strftime("%I:%M:%S :p")
 
    def drop_off_package(self, package: Package):
        if package in self.packages:
            package.delivery_time = self.current_time
            self.dispatcher.mark_delivered(package)
            self.packages.remove(package)
            package.package_log.append((f"[{package.package_id}] - [{self.current_time_readable()}] : Delivered package at {self.current_location} at time: {self.current_time_readable()} :: DEADLINE: {package.deadline}"))
            if self.current_time > package.deadline:
                logging.error(f"[{package.package_id}] - [{self.current_time_readable()}] : THIS PACKAGE WAS DELIVERED LATE!!!")
        else:
            raise AttributeError(f"Package Not Found")

    def should_return_to_hub(self):
        return (len(self.packages) == 0 and self.dispatcher.has_available_packages())

    def load_packages(self):
        print("Loading Packages")
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

    def find_nearest_package(self):
        print("Finding Nearest Package")
        if not self.packages:
            return None, 0
        
        min_distance = float("inf")
        nearest_package = None

        for package in self.packages:
            address = package.address
            if package.package_id == 9:
                if self.current_time.time() >= datetime.time(hour=10, minute=20):
                    package.address = "410 S. State St., Salt Lake City, UT 84111"
                else:
                    continue
            
            current_indx = self.distance_index_map[self.current_location]
            destination_indx = self.distance_index_map[address]
            distance = self.get_distance(current_indx, destination_indx)

            deadline_prio = 1
            if package.deadline.time() <= datetime.time(hour=10, minute=20):
                deadline_prio = 0.5

            weighted_distance = distance * deadline_prio

            if weighted_distance < min_distance:
                min_distance = distance
                nearest_package = package

        return nearest_package, min_distance

    def move_truck(self, address: str, distance: float) -> int:
        self.current_location = address
        self.miles_driven += distance
        self.current_time += datetime.timedelta(hours=distance / self.avg_speed)

    def get_distance(self, index_one, index_two) -> float:
        return float(self.distance_data[index_one][index_two])

    def do_rounds(self):
        while True:

            if len(self.packages) == 0 and self.dispatcher.has_available_packages():
                if not self.load_packages():
                    break
                continue

            if len(self.packages) == 0:
                break

            nearest_package, min_distance = self.find_nearest_package()

            if nearest_package is None:
                break

            address = nearest_package.address
            if nearest_package.package_id == 9 and self.current_time.time() >= datetime.time(10, 20):
                address = "410 S. State St., Salt Lake City, UT 84111"
                nearest_package.address = address

            self.move_truck(address, min_distance)
            self.drop_off_package(nearest_package)

    def can_take_delayed(self) -> bool:
        return self.delayed_truck
