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

if __name__ == "__main__":
    main()