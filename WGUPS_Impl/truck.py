from package import Package
from hash_table import HashTable

class Truck:
    def __init__(self, current_location):
        self.avg_speed: int = 18
        self.max_inventory: int = 16
        self.current_location = current_location 
        self.miles_driven = 0
        self.packages: HashTable = HashTable(self.max_inventory)
        self.schedule: list = []

    def get_package(self, package_id):
        if len(self.packages) != 16:
            self.packages._insert_node(package_id)
        else:
            print("Truck is full")

    def drop_off_package(self, package_id):
        package = self.packages._lookup(package_id)
        if package:
            package.status = "delivered"

    def move_truck(self, address: str, distance: float):
        self.current_location = address
        self.miles_driven += distance