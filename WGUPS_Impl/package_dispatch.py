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
            
            all_packages.append(new_package)
        all_packages.sort(key=lambda p: (p.deadline, bool(p.note)))

        return all_packages

    def has_available_packages(self):
        with self.package_lock:
            return len(self.packages) > 0
        
    def get_packages_for_truck(self, truck, capacity_needed: int):
        packages_to_load = []

        with self.package_lock:
            available_packages = [p for p in self.packages if p.package_id not in self.delivered_packages]

            if not available_packages:
                print("No packages available at hub")
                return packages_to_load

            packages_to_assign = available_packages[:capacity_needed]

            for package in packages_to_assign:
                new_status = package.status.on_event("LOAD_TRUCK")
                if new_status:
                    if package.status == Status.DELAYED:
                        if truck.can_take_delayed():     
                            package.status = new_status
                        else:
                            continue
                    else:
                        package.status = new_status
                else:
                    logging.error("Invalid State Change")

                if package.status == Status.EN_ROUTE:
                    packages_to_load.append(package)
                    self.packages.remove(package)
                    package.package_log.append((f"[{package.package_id}] - [{truck.current_time_readable()}] : Assigned package {package.package_id} to truck {getattr(truck, 'truckId', 'UNKOWN')}"))
                
        return packages_to_load

    def mark_delivered(self, package: Package):
        with self.package_lock:
            package.status = package.status.on_event("DELIVER")
            self.delivered_packages.insert_node(package)

