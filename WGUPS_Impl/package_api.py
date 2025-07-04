from flask import Flask, jsonify, request
from flask_cors import CORS
from simulator_app.truck import Truck
from simulator_app.package_dispatch import PackageDispatch

import pathlib
import threading
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

def check_sim_run():
    if not simulation_data['simulation_complete']:
        run_simulation()


@app.route('/', methods=['GET', 'POST'])
def home():
    if (request.method == 'GET'):
        data = "hello world"
        return jsonify({'data': data})

@app.route('/api/simulate', methods = ['GET'])
def get_sim_data():
    check_sim_run()
    return jsonify(simulation_data)


@app.route('/api/simulate/final-state', methods = ['GET'])
def get_final_state():
    check_sim_run() 

    if (request.method == 'GET'):
        return jsonify(simulation_data['package_history']['FINAL'])
    
@app.route('/api/simulate/package/<int:package_id>/history', methods = ['GET'])
def get_package_over_time(package_id):
    check_sim_run()

    package_timeline = []

    for timestamp in simulation_data['package_history']:
        data = simulation_data['package_history'][timestamp]['history']
        if str(package_id) in data:
            package_data = data[str(package_id)]
            package_timeline.append({
                'timestamp': timestamp,
                'time_readable': simulation_data['package_history'][timestamp]['time_stamp'],
                'package_data': package_data
            })
    
    if not package_timeline:
        return jsonify({'error': f'Package {package_id} not found'})
    
    return jsonify({
        'package_id': package_id,
        'timeline': package_timeline,
        'total_snapshots': len(package_timeline)
    })


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
        print(f"SIM COMPLETE: {simulation_data['simulation_complete']}")
        print(f"TOTAL MILES: {simulation_data['total_miles']}")
    except Exception as e:
        simulation_data['error'] = str(e)
        print(f"Simulation Error: {e}")
        raise