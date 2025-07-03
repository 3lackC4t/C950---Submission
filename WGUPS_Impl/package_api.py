from flask import Flask, jsonify, request
from flask_cors import CORS
from simulator_app.truck import Truck
from simulator_app.package_dispatch import PackageDispatch

import pathlib
import threading
import logging    
import datetime
import os

app = Flask(__name__)
CORS(app)

simulation_data = {
    'package_history': {},
    'trucks': [],
    'simulation_complete': False,
    'total_miles': 0
}

@app.route('/', methods=['GET', 'POST'])
def home():
    if (request.method == 'GET'):
        data = "hello world"
        return jsonify({'data': data})
    

@app.route('/api/simulate/package-history', methods = ['GET'])
def get_history():
    run_simulation()
    if (request.method == 'GET'):
        return simulation_data['package_history']


def fix_location():
    curr_location = pathlib.Path.cwd()
    if curr_location.name == "WGUPS_Impl":
        print("TRUE")
        os.chdir("..")


def run_simulation():

    fix_location()

    dispatcher = PackageDispatch(
            pathlib.Path("WGUPS_Impl/data/WGUPS_Package_File_Cleaned.csv"),
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
    except Exception as e:
        simulation_data['error'] = str(e)
        print(f"Simulation Error: {e}")
        raise