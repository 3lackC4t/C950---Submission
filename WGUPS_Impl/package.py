from status import Status
from datetime import datetime, timedelta

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
        self.next = None 

    def convert_deadline(self, deadline_str: str):
        if deadline_str == "EOD":
            return timedelta(hours=23)
        else:
            raw_time = datetime.strptime(deadline_str, "%H:%M %p")
            return timedelta(hours=raw_time.hour, minutes=raw_time.minute, seconds=raw_time.second)

    def __str__(self):
        return f"""
            Delivery Address: {self.address}
            Deadline: {self.deadline}
            City: {self.city}
            Zip Code: {self.zipcode}
            Weight: {self.weight}
            Note: {self.note}
            Status: {self.status.value}
        """


