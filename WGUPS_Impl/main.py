# Author: Cameron Minty
# Student ID: 012312886

from truck import Truck
from package_dispatch import PackageDispatch

import pathlib
import threading
import logging    
import datetime

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

    # Were using two trucks (only two drivers) and one will be dedicated to taking delayed packages
    # Because of this a normal and delayed start time are defined 
    normal_start = datetime.datetime.combine(datetime.date.today(), datetime.time(8, 0, 0, 0, None))
    delayed_start = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 5, 0, 0, None))

    # Create truck objects and selects who is the delayed truck
    truck1: Truck = Truck(dispatcher, "truck-1", normal_start)
    truck2: Truck = Truck(dispatcher, "truck-2", delayed_start)
    truck2.delayed_truck = True
    truck3: Truck = Truck(dispatcher, "truck-3", normal_start)

    # Using the python threading library, start each truck thread targeting it's core loop 'do_rounds'
    truck1_thread = threading.Thread(target=truck1.do_rounds)
    truck2_thread = threading.Thread(target=truck2.do_rounds)

    # Start and then "join" (finish) each trucks core loop
    truck1_thread.start()
    truck2_thread.start()

    truck1_thread.join()
    truck2_thread.join() 


    # Convenience print for informing the use that the simulation is complete and printing the total miles driven.
    print(f"""
            Final package delivered
            Total Miles Driven: {truck1.miles_driven + truck2.miles_driven:.2f}
        """)

    while True:
        user_input = input("Would you like to inspect a specific package's manifest? [Y/n]")
        if user_input == 'Y':
            package_select = input("Type the number of the package you want to inspect, or type 'q' to quit: ")
            if package_select == 'q' or package_select == 'Q':
                break
            else:
                package = dispatcher.delivered_packages.lookup(int(package_select))
                print(package)
                package.print_log()
        elif user_input == 'n':
            break
        else:
            print("Unkown input detected please type 'Y' or 'n'")


if __name__ == "__main__":
    main()