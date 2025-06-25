from hash_table import HashTable
from package import Package
from status import Status

import threading
import csv
import pathlib
import logging

"""
PackageDispatch handles all logic pertaining to scheduling and distributing
packages to trucks. The create_available_packages method plays a part in ensuring
a "Greedy" approach to package distribution by sorting packages by earliest deadline first
and delayed packages second.
"""
class PackageDispatch:
    def __init__(self, csv_file_path: pathlib.Path, location: str):
        self.packages = self.load_all_packages(csv_file_path)
        self.delivered_packages = HashTable(len(self.packages))
        self.package_interface = HashTable(len(self.packages))
        self.location = location
        self.package_lock = threading.Lock()
        
    def load_all_packages(self, csv_file: pathlib.Path):
        all_packages = []
        
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            total_packages = list(reader)
       
        for package in total_packages[1::]:
            new_package: Package = Package(package_id=int(package[0]),
                                        address=package[1],
                                        city=package[2],
                                        zipcode=package[4],
                                        deadline=package[5],
                                        weight=float(package[6]),
                                        note=package[7],
                                        status=Status.AT_HUB)
            
            if "Delayed on flight" in new_package.note:
                new_package.status.on_event("DELAY_PACKAGE")
            
            all_packages.append(new_package)

        all_packages.sort(key=lambda p: (p.deadline, bool(p.note)))
        return all_packages

    def has_available_packages(self):
        with self.package_lock:
            return len(self.packages) > 0
        
    def get_packages_for_truck(self, truck, capacity_needed: int):
        print("Taking Packages from Hub")
        packages_to_load = []

        with self.package_lock:
            print("Packages Locked")
            if not self.has_available_packages():
                print("No packages available at hub")
                return packages_to_load
            
            packages_to_assign = []

            for package in self.packages:
                print(f"Checking package {package.package_id}")
                if ("Can only be on truck 2" in package.note or package.package_id == 15) and truck.truckId != "truck-2":
                    continue

                if package.status == Status.DELAYED and not truck.can_take_delayed():
                    continue

                if len(packages_to_assign) < capacity_needed:
                    packages_to_assign.append()
                else:
                    break

            for package in packages_to_assign:
                print(f"Loading package {package.package_id}")
                new_status = package.status.on_event()
                if new_status:
                    package.status = new_status
                packages_to_load.append(package)
                self.packages.remove(package)
                package.package_log.append(f"[{package.package_id}] - [{truck.current_time_readable()}] : Package [{package.package_id}] loaded onto truck [{truck.truckId}]")

        return packages_to_load

    def mark_delivered(self, package: Package):
        with self.package_lock:
            package.status = package.status.on_event("DELIVER")
            self.delivered_packages.insert_node(package)

