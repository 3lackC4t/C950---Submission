# Author: Cameron Minty
# Student ID: 012312886

from package import Package
from hash_table import HashTable
from truck import Truck
from status import Status 
from package_dispatch import PackageDispatch

import pathlib
import threading
    

def main():  
    dispatcher = PackageDispatch(
            pathlib.Path("C950---Submission\WGUPS_Impl\data\WGUPS_Package_File_Cleaned.csv"),
            "Western Governors University 4001 South 700 East, Salt Lake City, UT 84107"
        )

    truck1: Truck = Truck(dispatcher, "truck-1")
    truck2: Truck = Truck(dispatcher, "truck-2")
    truck2.delayed_truck = True
    truck3: Truck = Truck(dispatcher, "truck-3")

    truck1_thread = threading.Thread(target=truck1.do_rounds)
    truck2_thread = threading.Thread(target=truck2.do_rounds)

    truck1_thread.start()
    truck2_thread.start()

    truck1_thread.join()
    truck2_thread.join()

    print(truck1.miles_driven + truck2.miles_driven)

if __name__ == "__main__":
    main()