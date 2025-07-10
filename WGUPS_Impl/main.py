from truck import Truck
from package_dispatch import PackageDispatch

from pathlib import Path
from time import sleep
import datetime
import threading
from pprint import pprint

BASE_DIR = Path(__file__).parent.absolute()
PACKAGE_FILE = BASE_DIR / 'data' / 'WGUPS_Package_File_Cleaned.csv'
DISTANCE_FILE = BASE_DIR / 'data' / 'WGUPS_Distance_Table_Cleaned.csv'


simulation_data = {
    'package_history': {},
    'trucks': [],
    'simulation_complete': False,
    'total_miles': 0
}


def run_simulation():

    dispatcher = PackageDispatch(
            PACKAGE_FILE,
            "Western Governors University 4001 South 700 East, Salt Lake City, UT 84107"
        )
    
    # Were using two trucks (only two drivers) and one will be dedicated to taking delayed packages
    # Because of this a normal and delayed start time are defined 
    normal_start = datetime.datetime.combine(datetime.date.today(), datetime.time(8, 0, 0, 0, None))
    delayed_start = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 5, 0, 0, None))

    # Create truck objects and selects who is the delayed truck
    truck1: Truck = Truck(dispatcher, DISTANCE_FILE, "truck-1", normal_start)
    truck2: Truck = Truck(dispatcher, DISTANCE_FILE, "truck-2", delayed_start)
    truck2.delayed_truck = True
    truck3: Truck = Truck(dispatcher, DISTANCE_FILE, "truck-3", normal_start)

    try:
        # Using the python threading library, start each truck thread targeting it's core loop 'do_rounds'
        truck1_thread = threading.Thread(target=truck1.do_rounds)
        truck2_thread = threading.Thread(target=truck2.do_rounds)

        # Start and then "join" (finish) each trucks core loop
        truck1_thread.start()
        truck2_thread.start()

        truck1_thread.join()
        truck2_thread.join()

        simulation_data['simulation_complete'] = True
        simulation_data['total_miles'] = (truck1.miles_driven + truck2.miles_driven)
        simulation_data['package_history'] = dispatcher.package_history
        simulation_data['trucks'] = [
            truck1.get_truck_data(),
            truck2.get_truck_data(),
            truck3.get_truck_data()
        ]
        print(f"SIM COMPLETE: {simulation_data['simulation_complete']}")
        print(f"TOTAL MILES: {simulation_data['total_miles']}")
    except Exception as e:
        simulation_data['error'] = str(e)
        print(f"Simulation Error: {e}")
        raise


def main():
    run_simulation()
    while True:
        display_selection: str = input("Would you like to view the [F]inal state, a specific [T]imestamp, or [Q]uit? ")
        if display_selection.lower() == 'f':
            print("Displaying final package status for all packages including package logs.")
            sleep(1)
            data = simulation_data['package_history']['FINAL']['history']
            sorted(data.keys(), key=lambda x: int(x))
            for key in data:
                print("=" * 50)
                print(f"    Package ID: {key}")
                pprint(data[key], indent=3, width=160)
                print("=" * 50)
        elif display_selection.lower() == 't':
            timestamp = input("Enter the hour of the timestamp you want to view in military time (e.g., 8 for 8 AM, 15 for 3 PM): ")
            if timestamp in simulation_data['package_history']:
                data = simulation_data['package_history'][timestamp]['history']
                sorted(data.keys(), key=lambda x: int(x))
                for key in data:
                    print("=" * 50)
                    print(f"    Package ID: {key}")
                    pprint(data[key], indent=3, width=160)
                    print("=" * 50)
            else:
                print(f"No data found for timestamp '{timestamp}'.")
        elif display_selection.lower() == 'q':
            break
        else:
            print(f"Input '{display_selection}' not recognized. Please enter either F, T, or Q")
if __name__ == "__main__":
    main()