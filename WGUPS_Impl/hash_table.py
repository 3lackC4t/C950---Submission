from package import Package

class HashTable:
    def __init__(self, capacity):
        self.capacity = capacity
        self.size = 0
        self.table: Package= [None] * capacity

    # Using the SDBM hash algorithm to hash the package_id
    def _make_hash(self, key):
        hash_val = 0
        for char in str(key):
            hash_val = ord(char) + (hash_val << 6) + (hash_val << 16) - hash_val
        return hash_val % self.capacity
    
    # Using the hash table chaining method to handle potential collisions
    def _insert_node(self, package_id, address, deadline, city, zipcode, weight, status):
        new_package: Package= Package(package_id, address, deadline, city, zipcode, weight, status)
        package_hash= self._make_hash(package_id)
        if not self.table[package_hash]:
            self.table[package_hash] = new_package 
            self.size += 1
        else:
            temp: Package= self.table[package_hash]
            while temp.next:
                if temp.package_id == package_id:
                    return
                temp = temp.next
            new_package.next = self.table[package_hash]
            self.table[package_hash] = new_package 
            self.size += 1

    def _remove_node(self, package_id):
        index = self._make_hash(package_id)
        current: Package = self.table[index]
        previous: Package = None

        while current:
            if current.package_id == package_id:
                if previous:
                    previous.next = current.next
                else:
                    self.table[index] = current.next
                self.size -= 1
                return
            previous = current
            current = previous.next

        raise KeyError(package_id)


    def _lookup(self, package_id):
        current: Package= self.table[self._make_hash(package_id)]
        while current:
            if current.package_id == package_id:
                return current 
            current = current.next
        
        raise KeyError(package_id)
    
    def __str__(self):
        result = []
        for package in self.table:
            chain = []
            while package:
                chain.append(package)
                package = package.next
            result.extend(chain)

        return str(result)
    
    def __len__(self):
        return self.size
    
    def __contains__(self, package_id):
        try:
            self._lookup(package_id)
            return True
        except KeyError:
            return False
    