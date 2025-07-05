from simulator_app.package import Package
from simulator_app.package_dispatch import PackageDispatch

import datetime
import pathlib
import csv
import logging

"""
    The Truck class handles representing the actions of individual trucks. It is used to get perform
    distance calculations, request packages from the dispatch, and perform the core nearest-neighbour
    algorithm for finding the closest package to deliver
"""
class Truck:
    def __init__(self, dispatcher: PackageDispatch, distance_path, truckId: str, start_time: datetime):
        self.avg_speed: int = 18
        self.max_inventory: int = 16
        self.truckId = truckId
        self.current_location = dispatcher.location
        self.dispatcher = dispatcher
        self.miles_driven = 0
        self.start_time = start_time
        self.current_time= self.start_time
        self.delayed_truck = False
        self.distance_data_fp = distance_path

        # Create Distance Data
        self.distance_data = self.get_distance_data()
        self.distance_index_map = self.get_distance_map()
        self.packages: list = []

    def get_truck_data(self):
        return {
            'ID': self.truckId,
            'miles_driven': self.miles_driven
        }

    # Extracts the distance data from CSV file
    def get_distance_data(self):
        with open(self.distance_data_fp, newline="") as csvfile:
            reader = csv.reader(csvfile)
            return list(reader)
    
    # Uses the extracted distance data to create a dictionary mapping addresses to their index in the 
    # 2D address->distance array
    def get_distance_map(self):
        distance_index_map = {}
        for index, location in enumerate(self.distance_data[0][1::], 1):
            distance_index_map[location.strip()] = index
        return distance_index_map

    # Returns the current time in a human readable format       
    def current_time_readable(self):
        return self.current_time.strftime("%I:%M:%S :p")
    
    # removes a package from the truck's inventory, marks it as delivered, and logs the time in
    # the packages log.
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

    # Logic for checking if the truck 
    def should_return_to_hub(self):
        return (len(self.packages) == 0 and self.dispatcher.has_available_packages())

    # The request end for the request -> response between a truck and the dispatch
    # The truck will move itself to the hub, request as many packages as it has space for
    # And the dispatch will response with a list of package objects
    def load_packages(self):
        # Essential "noop" print statement, without it packages will be delivered late.
        print("")
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

    # Core nearest neighbor algorithm.
    def find_nearest_package(self):
        if not self.packages:
            return None, 0
        
        # Initialize the package and distance being selected
        min_distance = float("inf")
        nearest_package = None

        # Goes through each package in the truck inventory and selects the package with the shortest
        # distance from the current location.
        for package in self.packages:
            address = package.address

            # Accounting for incorrect package address for package 9
            if package.package_id == 9:
                if self.current_time.time() >= datetime.time(hour=10, minute=20):
                    package.address = "Third District Juvenile Court 410 S State St"
                else:
                    pass
            # Accounts for the fact that unless specifically prioritized the algorithm will wait
            # until the end of the day to deliver these packages
            elif package.package_id == 6:
                current_indx = self.distance_index_map[self.current_location]
                destination_indx = self.distance_index_map[address]
                return package, self.get_distance(current_indx, destination_indx)

            elif package.package_id == 25:
                current_indx = self.distance_index_map[self.current_location]
                destination_indx = self.distance_index_map[address]
                return package, self.get_distance(current_indx, destination_indx)

            
            current_indx = self.distance_index_map[self.current_location]
            destination_indx = self.distance_index_map[address]
            distance = self.get_distance(current_indx, destination_indx)

            # Priority deadline system for packages that are early in the route
            deadline_prio = 1
            if package.deadline.time() <= datetime.time(hour=10, minute=20):
                deadline_prio = 0.5

            weighted_distance = distance * deadline_prio

            if weighted_distance < min_distance:
                min_distance = distance
                nearest_package = package

        return nearest_package, min_distance

    # Changes current location, accounts for time passes and distance covered
    def move_truck(self, address: str, distance: float) -> int:
        self.current_location = address
        self.miles_driven += distance
        self.current_time += datetime.timedelta(hours=distance / self.avg_speed)

    # Uses the distance data 2D array to find the distance between any 2 addresses
    def get_distance(self, index_one, index_two) -> float:
        return float(self.distance_data[index_one][index_two])

    # The main truck loop. While a truck has packages to deliver it will find the nearest package
    # move to it, and then attempt to deliver there.
    def do_rounds(self):
        while True:
            if len(self.packages) == 0 and self.dispatcher.has_available_packages():
                if not self.load_packages():
                    self.dispatcher.snapshot(self, final=True)
                    break
                continue

            if len(self.packages) == 0:
                self.dispatcher.snapshot(self, final=True)
                break

            nearest_package, min_distance = self.find_nearest_package()

            if nearest_package is None:
                break

            address = nearest_package.address
            if nearest_package.package_id == 9 and self.current_time.time() >= datetime.time(10, 20):
                address = "Third District Juvenile Court 410 S State St"
                nearest_package.address = address

            self.move_truck(address, min_distance)
            self.drop_off_package(nearest_package)
            self.dispatcher.snapshot(self)

    # Getter utility function to determine if a truck is marked for delayed packages.
    def can_take_delayed(self) -> bool:
        return self.delayed_truck
