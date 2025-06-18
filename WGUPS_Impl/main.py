# Author: Cameron Minty
# Student ID: 012312886

from package import Package
from hash_table import HashTable
from truck import Truck
from status import Status 
from package_dispatch import PackageDispatch

import csv
import pathlib
import datetime
    

def main():  
    dispatcher = PackageDispatch(pathlib.Path("C950---Submission\WGUPS_Impl\data\WGUPS_Package_File_Cleaned.csv"))

    truck1: Truck = Truck(dispatcher)
    truck2: Truck = Truck(dispatcher)
    truck3: Truck = Truck(dispatcher)

    truck1.do_rounds(distance_index_map, distance_data)
    truck2.do_rounds(distance_index_map, distance_data)


    print(truck1.miles_driven + truck2.miles_driven)

if __name__ == "__main__":
    main()