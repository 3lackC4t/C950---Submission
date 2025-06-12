class Package:
    def __init__(self, package_id, address, deadline, city, zipcode, weight, status):
        self.package_id = package_id 
        self.address = address
        self.deadline = deadline
        self.city = city
        self.zipcode = zipcode
        self.weight = weight
        self.status = status
        self.next = None 

    def __str__(self):
        return f"""
            Delivery Address: {self.address}
            Deadline: {self.deadline}
            City: {self.city}
            Zip Code: {self.zipcode}
            Weight: {self.weight}
            Status: {self.status}
        """


