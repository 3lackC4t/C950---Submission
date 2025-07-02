from hash_table import HashTable
from package import Package
from status import Status

import threading
import csv
import pathlib
import copy
"""
PackageDispatch handles all logic pertaining to scheduling and distributing
packages to trucks. The create_available_packages method plays a part in ensuring
a "Greedy" approach to package distribution by sorting packages by earliest deadline first
and delayed packages second.
"""
class PackageDispatch:
    def __init__(self, csv_file_path: pathlib.Path, location: str):
        self.packages = self.load_all_packages(csv_file_path)
        self.package_interface = self.build_interface() 
        self.package_history = {}
        self.location = location
        self.package_lock = threading.Lock()

    """
        Pulls in the package data from the csv file, creates package objects, and uses the 
        Status.on_event() state machine manager to handle selecting DELAYED for delayed packages
    """    
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
            
            new_package.package_log.append(f"Package {new_package.package_id} loaded from data file, current status: {new_package.status}, current expected destination: {new_package.address}, current deadline: {new_package.deadline}")
            
            if "Delayed on flight" in new_package.note:
                new_status = new_package.status.on_event("DELAY_PACKAGE")
                if new_status:
                    new_package.status = new_status
            
            all_packages.append(new_package)

        all_packages.sort(key=lambda p: (p.deadline, bool(p.note)))
        return all_packages
    
    def build_interface(self):
        interface = HashTable(len(self.packages))
        for package in self.packages:
            interface.insert_node(package)
        return interface
    
    # Creates a snapshot of the current status of all packages and stores it in the dispatche's package history.
    def snapshot(self, truck):
        interface_copy: HashTable = copy.deepcopy(self.package_interface)
        timestamp = truck.current_time.hour
        if timestamp not in self.package_history:
            self.package_history[timestamp] = (truck.current_time, interface_copy)

    # Checks to see if there are packages to take from the dispatch
    def has_available_packages(self):
        with self.package_lock:
            return len(self.packages) > 0
    
    # This is the return side of the thread-safe "request/response" model being used to handle
    # Thread safe access to the package inventory at the dispatch. This method also includes 
    # Logic for the specific constraints that many of the packages have.
    def get_packages_for_truck(self, truck, capacity_needed: int):
        packages_to_load = []
        
        if not self.has_available_packages():
            return packages_to_load

        with self.package_lock:
                        
            packages_to_assign = []

            for package in self.packages:
                if "Can only be on truck 2" in package.note and truck.truckId != "truck-2":
                    continue

                if package.package_id in [13, 14, 15, 19, 20] and truck.truckId != "truck-1":
                    continue

                if package.status == Status.DELAYED and truck.truckId != "truck-2":
                    continue

                if len(packages_to_assign) < capacity_needed:
                    packages_to_assign.append(package)
                else:
                    break

            for package in packages_to_assign:
                try:
                    new_status = package.status.on_event("LOAD_TRUCK")
                    if new_status:
                        package.status = new_status
                    packages_to_load.append(package)
                    self.packages.remove(package)
                    package.package_log.append(f"[{package.package_id}] - [{truck.current_time_readable()}] : Package [{package.package_id}] loaded onto truck [{truck.truckId}]")
                except ValueError as e:
                    print(f"Invalid State Change on package {package.package_id}")

        return packages_to_load
    
    # Thread safe management of currently delivered packages
    def mark_delivered(self, package: Package):
        with self.package_lock:
            package.status = package.status.on_event("DELIVER")
            self.package_interface.insert_node(package)

