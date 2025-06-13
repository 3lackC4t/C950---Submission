# Author: Cameron Minty
# Student ID: 012312886

from package import Package
from hash_table import HashTable
from truck import Truck

import csv
import argparse
import pathlib

def import_csv_data(filepath: str):
    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile)
        return list(reader)


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
    package_data = import_csv_data(pathlib.Path("C950---Submission\WGUPS_Impl\data\WGUPS_Package_File_Cleaned.csv"))
    print(package_data)


if __name__ == "__main__":
    main()