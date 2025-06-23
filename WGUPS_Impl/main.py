# Author: Cameron Minty
# Student ID: 012312886

from truck import Truck
from package_dispatch import PackageDispatch

import pathlib
import threading
import logging    

def main():  

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler() 
        ]
    )

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

    print(f"""
            Final package delivered
            Total Miles Driven: {truck1.miles_driven + truck2.miles_driven:.2f}
        """)
    
    while True:
        user_input = input("Key - Lookup, print all or quit? [l/p/q]")    
        if user_input == 'l' or user_input =='L':
            while True:
                try:
                    package_lookup = input("Input desired package id: ")
                    if package_lookup == 'q' or package_lookup == 'Q':
                        break
                    else:
                        package = dispatcher.delivered_packages.lookup(package_lookup)
                        print(package)
                        print(f"PACKAGE LOG FOR {package.package_id}")
                        for log in package.package_log:
                            print(log)
                except KeyError:
                    print("Package ID not found, please enter a valid ID or 'q' for quit")
        elif user_input == 'p' or user_input == 'P':
            for package in dispatcher.delivered_packages:
                print("=+"*26)
                print(package)
                print(f"PACKAGE LOG FOR {package.package_id}")
                for log in package.package_log:
                    print(log)
                print("=+"*26)
        elif user_input == 'q' or 'Q':
            print("Thank you and have a good day")
            break

if __name__ == "__main__":
    main()