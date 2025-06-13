# Author: Cameron Minty
# Student ID: 012312886

from package import Package
from hash_table import HashTable
from truck import Truck
from status import Status 

import csv
import argparse
import pathlib


def import_csv_data(filepath: str):
    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile)
        return list(reader)

def truck_signal(token: str):
    TRUCK_SEMAPHOR.append(token)

def truck_wait() -> str:
    if len(TRUCK_SEMAPHOR) > 0:
        token = TRUCK_SEMAPHOR.pop()
        return token
    else:
        return "WAIT"


# Employing a Greedy Activity Selection ALgortihm.
# A truck can move at most 18 miles an hour,
# A truck can only start moving at 0800
# A truck can hold up to 16 packages at a time
# There are 3 trucks and 2 drivers => Only 2 trucks running
# at a time
def main():
    # Basic Process: at 0800 the trucks will grab the maximum number of packages
    # They can support. 
    distance_data = import_csv_data(pathlib.Path("C950---Submission\WGUPS_Impl\data\WGUPS_Distance_Table_Cleaned.csv")) 
    distance_index_map = {}
    index = 1
    for location in distance_data[0][1::]:
        distance_index_map[location] = index
        index += 1

    package_data = import_csv_data(pathlib.Path("C950---Submission\WGUPS_Impl\data\WGUPS_Package_File_Cleaned.csv"))

    truck1: Truck = Truck(distance_data[0][1])
    truck2: Truck = Truck(distance_data[0][1])
    truck3: Truck = Truck(distance_data[0][1])

    total_packages = []
    for package in package_data[1::]:
       new_package: Package = Package(package_id=package[0],
                                      address=package[1],
                                      city=package[2],
                                      zipcode=package[4],
                                      deadline=package[5],
                                      weight=package[6],
                                      note=package[7],
                                      status=Status.AT_HUB)
       total_packages.append(new_package)


if __name__ == "__main__":
    main()