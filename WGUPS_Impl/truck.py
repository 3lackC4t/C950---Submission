from package import Package
from package_dispatch import PackageDispatch

import datetime
import pathlib
import csv
import logging

class Truck:
    def __init__(self, dispatcher: PackageDispatch, truckId: str):
        self.avg_speed: int = 18
        self.max_inventory: int = 16
        self.truckId = truckId
        self.current_location = dispatcher.location
        self.dispatcher = dispatcher
        self.miles_driven = 0
        self.start_time = datetime.datetime.combine(datetime.date.today(), datetime.time(8, 0, 0, 0, None))
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
            self.dispatcher.mark_delivered(package)
            self.packages.remove(package)
            logging.info(f"TRUCK: [{self.truckId}] :: Delivered package {package.package_id} at {self.current_location} at time: {self.current_time_readable()} :: DEADLINE: {package.deadline}")
            if self.current_time > package.deadline:
                logging.info("TRUCK: [{self.truckId}] :: THIS PACKAGE WAS DELIVERED LATE!!!")
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
        logging.info(f"TRUCK: [{self.truckId}] :: Current Location: {self.current_location}")
        self.current_location = address
        self.miles_driven += distance
        self.current_time += datetime.timedelta(hours=distance / self.avg_speed)
        logging.info(f"TRUCK: [{self.truckId}] :: New Location: {self.current_location}")

    def get_distance(self, index_one, index_two) -> float:
        return float(self.distance_data[index_one][index_two])

    def do_rounds(self):
        current_radius: int = 0

        while len(self.dispatcher.packages) > 0 or len(self.packages) > 0:
            if self.dispatcher.has_available_packages() and len(self.packages) == 0:
                if self.load_packages():
                    current_radius = 0
                    continue
                else:
                    break

            if len(self.packages) == 0:
                break

            candidates = []
            for package in self.packages:
                try:
                    distance = self.get_distance(
                            self.distance_index_map[self.current_location], 
                            self.distance_index_map[package.address]
                        )
                    if distance <= current_radius:
                        candidates.append((package, distance))
                except KeyError as e:
                    logging.error(e)
                    logging.error(f"Address not found in distance map: {package.address}")
                    continue

            if candidates:
                best_package, best_distance = min(candidates, key=lambda x: x[1])
                self.move_truck(best_package.address, best_distance)
                self.drop_off_package(best_package)
                current_radius = 0
            else:
                if current_radius <= 100:
                    current_radius += 2
                else:
                    break

    def can_take_delayed(self) -> bool:
        return self.delayed_truck
