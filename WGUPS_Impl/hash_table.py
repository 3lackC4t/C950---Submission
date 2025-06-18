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
    def _insert_node(self, package: Package):
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
    