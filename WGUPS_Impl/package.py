from status import Status
from datetime import datetime

"""
    The Package class contains the logic for creating a package object as well as for 
    converting the string formatted deadlines found in the package CSV file.
"""
class Package:
    def __init__(self, package_id: int, 
                 address: str, 
                 deadline: str, 
                 city: str, 
                 zipcode:str, 
                 weight: float, 
                 note: str, 
                 status: Status):

        self.package_id = package_id 
        self.address = address
        self.deadline = self.convert_deadline(deadline)
        self.city = city
        self.zipcode = zipcode
        self.weight = weight
        self.note = note
        self.status = status
        self.package_log = []
        self.delivery_time = None
        self.truck_id = None
        self.next = None 

    def convert_deadline(self, deadline_str: str):
        base_date = datetime.now().date()

        if deadline_str == "EOD":
            return datetime.combine(base_date, datetime.strptime("5:00 PM", "%I:%M %p").time())
        else: 
            raw_time = datetime.strptime(deadline_str, "%I:%M %p").time()
            return datetime.combine(base_date, raw_time)
        
    # Converts the package object to a dictionary for ease of CLI display and API usage.
    def to_dict(self):
        return {
            "ID": self.package_id,
            "TRUCK_ID": self.truck_id,
            "ADDRESS": self.address,
            "DEADLINE": self.deadline.isoformat() if hasattr(self.deadline, 'isoformat') else str(self.deadline),
            "CITY": self.city,
            "ZIPCODE": self.zipcode,
            "WEIGHT": self.weight,
            "NOTE": self.note,
            "STATUS": self.status.value,
            "PACKAGE_LOG": self.package_log,
            "DELIVERY_TIME": self.delivery_time.isoformat() if self.delivery_time and hasattr(self.delivery_time, 'isoformat') else None,
        }

    # Provides overriding of the print() method for any given package object
    def __str__(self):

        log = ""

        for entry in self.package_log:
            log += (entry + "\n")

        return f"""
            PACKAGE ID: [{self.package_id}]
            Delivery Address: {self.address}
            Deadline: {self.deadline}
            City: {self.city}
            Zip Code: {self.zipcode}
            Weight: {self.weight}
            Note: {self.note}
            Status: {self.status.value}
            LOG:
            {log}
        """ 

    # Interface to print the packages logs 
    def print_log(self):
        for indx, log in enumerate(self.package_log):
            print(f"[{indx}] - {log}")


