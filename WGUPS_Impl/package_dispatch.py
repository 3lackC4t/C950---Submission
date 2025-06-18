from hash_table import HashTable
from package import Package
from status import Status
from truck import Truck

import threading
import csv
import pathlib

"""
PackageDispatch handles all logic pertaining to scheduling and distributing
packages to trucks. The create_available_packages method plays a part in ensuring
a "Greedy" approach to package distribution by sorting packages by earliest deadline first
and delayed packages second.
"""
class PackageDispatch:
    def __init__(self, csv_file_path: pathlib.Path, location: str):
        self.packages = self.load_packages_from_csv(csv_file_path)[1::]
        self.available_packages = self.get_available_packages()
        self.delivered_packages = HashTable(len(self.packages))
        self.location = location
        self.package_lock = threading.lock()
        self.global_time_lock = threading.lock()

    def load_packages_from_csv(self, csv_file: pathlib.Path): 
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            return list(reader)
        
    def get_available_packages(self):
        early_packages = []
        delayed_packages = []

        for package in self.packages:
            new_package: Package = Package(package_id=package[0],
                                        address=package[1],
                                        city=package[2],
                                        zipcode=package[4],
                                        deadline=package[5],
                                        weight=package[6],
                                        note=package[7],
                                        status=Status.AT_HUB)
            
            if new_package.note:
                new_package.status = Status.DELAYED
                delayed_packages.append(new_package)
            else:
                early_packages.append(new_package)

        early_packages.sort(key=lambda p: p.deadline)
        delayed_packages.sort(key=lambda p: p.deadline)
        delayed_packages.extend(early_packages)
        delayed_packages.reverse()

        return delayed_packages

    def has_available_packages(self):
        return len(self.packages) > 0

    def get_packages_for_truck(self, truck: Truck, capacity_needed: int):
        packages_to_load = []
        for _ in range(capacity_needed):
            packages_to_load.append(self.available_packages.pop())

        return packages_to_load

    def mark_delivered(self, package: Package):
        self.delivered_packages._insert_node(package)