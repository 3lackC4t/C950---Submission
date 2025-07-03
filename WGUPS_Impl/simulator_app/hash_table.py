from simulator_app.package import Package

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
    def insert_node(self, package: Package):
        package_hash = self._make_hash(package.package_id)

        if not self.table[package_hash]:
            # The slot is empty, just insert
            self.table[package_hash] = package 
            self.size += 1
        else:
            # Check for a duplicate
            temp: Package= self.table[package_hash]
            while temp:
                if temp.package_id == package.package_id:
                    return
                temp = temp.next

            # No duplicate, insert at head of chain
            package.next = self.table[package_hash]
            self.table[package_hash] = package 
            self.size += 1

    # Searches the hash table using a given package id if one is found it will check to see if the 
    # node is in a chain and if so performs standard linked list logic to remove it.
    def remove_node(self, package_id):
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

    # Return a package by it's ID
    def lookup(self, package_id):
        current: Package= self.table[self._make_hash(package_id)]
        while current:
            if current.package_id == package_id:
                return current 
            current = current.next
        
        raise KeyError(package_id)
    
    # In order to output the HashTable object and it's contents to
    # The API endpoint it will have to be serializable as a python
    # dictionary
    def to_dict(self):
        res = {}

        # For each node in the table, turn that node and any nodes chained to it
        # in a linked list to dictionary objects.
        for node in self.table:
            
            current = node

            while current is not None:
                res[str(current.package_id)] = current.to_dict()
                current = current.next
            
            return res

    # Print the has table, useful for replicating python's standard dictionary methods
    def __str__(self):
        result = []
        for package in self.table:
            chain = []
            while package:
                chain.append(package)
                package = package.next
            result.extend(chain)

        return str(result)

    # Be able to use the hash table in a for loop
    def __iter__(self):
        for package in self.table:
            current = package
            while current:
                yield current
                current = current.next
    
    # be able to use len() on a hash table to return it's current size
    def __len__(self):
        return self.size

    # Be able to use the 'in' keyword on a hashtable 
    def __contains__(self, package_id):
        try:
            self.lookup(package_id)
            return True
        except KeyError:
            return False
    