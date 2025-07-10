# Author: Cameron Minty
# Student ID: 012312886
# WGU C950 - WGUPS Package Delivery Simulation

from truck import Truck
from package_dispatch import PackageDispatch

from pathlib import Path
import datetime
import threading
import os

# Define the base directory and file paths for package and distance data
BASE_DIR = Path(__file__).parent.absolute()
PACKAGE_FILE = BASE_DIR / 'data' / 'WGUPS_Package_File_Cleaned.csv'
DISTANCE_FILE = BASE_DIR / 'data' / 'WGUPS_Distance_Table_Cleaned.csv'

# Initialize a global dictionary to store simulation data
simulation_data = {
    'package_history': {},
    'trucks': [],
    'simulation_complete': False,
    'total_miles': 0
}

# Function to run the WGUPS package delivery simulation
def run_simulation():
    
    print("=" * 60)
    print("STARTING WGUPS PACKAGE DELIVERY SIMULATION")
    print("=" * 60)

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

        print("\n" + "=" * 60)
        print("SIMULATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Total miles driven: {simulation_data['total_miles']:0.2f}")
        
    except Exception as e:
        simulation_data['error'] = str(e)
        print(f"Simulation Error: {e}")
        raise

# Display packages in a clean, sorted format
def display_packages_formatted(data, title):
    print("\n" + "=" * 80)
    print(f"{title}")
    print("=" * 80)
    
    # Sort packages by ID (convert string keys to int for proper sorting)
    sorted_packages = sorted(data.items(), key=lambda x: int(x[0]))
    
    for package_id, package_data in sorted_packages:
        print(f"\nPackage ID: {package_id}")
        print("-" * 40)
        
        # Display key information in a clean format
        print(f"  Status: {package_data.get('STATUS', 'Unknown')}")
        print(f"  Address: {package_data.get('ADDRESS', 'Unknown')}")
        print(f"  Deadline: {format_deadline(package_data.get('DEADLINE', ''))}")
        print(f"  Weight: {package_data.get('WEIGHT', 'Unknown')} kg")
        
        if package_data.get('TRUCK_ID'):
            print(f"  Truck: {package_data['TRUCK_ID']}")
        
        if package_data.get('DELIVERY_TIME'):
            delivery_time = format_time(package_data['DELIVERY_TIME'])
            print(f"  Delivered: {delivery_time}")
            
            # Check if delivered on time
            if is_delivered_on_time(package_data):
                print("  On Time Status: ON TIME")
            else:
                print("  On Time Status: LATE")
        
        if package_data.get('NOTE'):
            print(f"  Special Notes: {package_data['NOTE']}")
        
        # Show delivery log if available and not too long
        if package_data.get('PACKAGE_LOG'):
            print("  Delivery Log:")
            for log_entry in package_data['PACKAGE_LOG']:
                print(f"    • {log_entry}")

# Format ISO time string to readable format
def format_time(time_string):
    try:
        formatted_time = datetime.datetime.fromisoformat(time_string)
        return formatted_time.strftime("%I:%M:%S %p")
    except:
        return time_string

# Format deadline to readable format
def format_deadline(deadline_string):
    try:
        formatted_time = datetime.datetime.fromisoformat(deadline_string)
        if formatted_time.time() == datetime.time(17, 0):  # 5:00 PM
            return "End of Day (5:00 PM)"
        return formatted_time.strftime("%I:%M %p")
    except:
        return deadline_string

# Check if package was delivered on time
def is_delivered_on_time(package_data):
    try:
        if not package_data.get('DELIVERY_TIME'):
            return False
        
        delivery_time = datetime.datetime.fromisoformat(package_data['DELIVERY_TIME'])
        deadline = datetime.datetime.fromisoformat(package_data['DEADLINE'])
        return delivery_time <= deadline
    except:
        return False

# Display available timestamps for user selection 
def show_available_timestamps():
    available_times = [k for k in simulation_data['package_history'].keys() if k != 'FINAL']
    available_times.sort(key=lambda x: int(x))
    
    print(f"\nAvailable timestamps: {', '.join(available_times)}")
    print("(These represent the hour when package status was recorded)")

# Display summary statistics of the simulation
def show_summary_statistics():
    print("\n" + "=" * 60)
    print("DELIVERY PERFORMANCE SUMMARY")
    print("=" * 60)
    
    # Analyze final delivery status
    if 'FINAL' in simulation_data['package_history']:
        final_data = simulation_data['package_history']['FINAL']['history']
        
        total_packages = len(final_data)
        delivered_packages = len([p for p in final_data.values() if p.get('DELIVERY_TIME')])
        on_time_packages = len([p for p in final_data.values() if is_delivered_on_time(p)])
        
        print(f"Total Packages: {total_packages}")
        print(f"Successfully Delivered: {delivered_packages}")
        print(f"On-Time Deliveries: {on_time_packages}")
        print(f"Late Deliveries: {delivered_packages - on_time_packages}")
        print(f"Total Miles Driven: {simulation_data['total_miles']}")

# Main function to run the simulation and handle user input
def main():
    run_simulation()
    
    while True:
        print("\n" + "=" * 60)
        print("WGUPS PACKAGE TRACKING SYSTEM")
        print("=" * 60)
        print("Select an option:")
        print("  [F] - View final package status (all packages)")
        print("  [T] - View packages at specific timestamp")
        print("  [S] - View summary statistics")
        print("  [A] - View available timestamps")
        print("  [C] - Clear screen")
        print("  [Q] - Quit")
        print()
        
        display_selection = input("Enter your choice: ").strip().lower()
        
        if display_selection == 'f':
            if 'FINAL' in simulation_data['package_history']:
                data = simulation_data['package_history']['FINAL']['history']
                display_packages_formatted(data, "FINAL PACKAGE STATUS - ALL DELIVERIES")
            else:
                print("Final data not available.")
                
        elif display_selection == 't':
            show_available_timestamps()
            timestamp = input("\nEnter timestamp (hour in 24-hour format (eg. 8 for 8:00AM or 13 for 1:00PM)): ").strip()
            
            if timestamp in simulation_data['package_history']:
                data = simulation_data['package_history'][timestamp]['history']
                time_info = simulation_data['package_history'][timestamp]['time_stamp']
                formatted_time = format_time(time_info)
                display_packages_formatted(data, f"PACKAGE STATUS AT {formatted_time}")
            else:
                print(f"No data found for timestamp '{timestamp}'.")
                print("Use option [A] to see available timestamps.")
                
        elif display_selection == 's':
            show_summary_statistics()
            
        elif display_selection == 'a':
            show_available_timestamps()
            
        elif display_selection == 'q':
            print("\nThank you for using WGUPS Package Tracking System!")
            break

        elif display_selection == 'c':
            os.system('cls' if os.name == 'nt' else 'clear')
            continue
            
        else:
            print(f"Invalid input '{display_selection}'. Please enter F, T, S, A, or Q.")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    main()