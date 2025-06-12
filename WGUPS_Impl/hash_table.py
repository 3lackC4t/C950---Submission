
class Node:
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


class HashTable:
    def __init__(self, capacity):
        self.capacity = capacity
        self.size = 0
        self.table: Node = [None] * capacity

    # Using the SDBM hash algorithm to hash the package_id
    def _make_hash(self, key):
        hash_val = 0
        for char in str(key):
            hash_val = ord(char) + (hash_val << 6) + (hash_val << 16) - hash_val
        return hash_val % self.capacity
    
    # Using the hash table chaining method to handle potential collisions
    def _insert_node(self, package_id, address, deadline, city, zipcode, weight, status):
        new_node: Node = Node(package_id, address, deadline, city, zipcode, weight, status)
        node_hash = self._make_hash(package_id)
        if self.table[node_hash] is not None:
            self.table[node_hash] = new_node
            self.size += 1
        else:
            temp: Node = self.table[node_hash]
            while temp.next:
                if temp.package_id == package_id:
                    return
                temp = temp.next
            new_node.next = self.table[node_hash]
            self.table[node_hash] = new_node
            self.size += 1

    def _remove_node(self, package_id):
        index = self._make_hash(package_id)
        current: Node = self.table[index]
        previous: Node = None

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
        bucket: Node = self.table[self._make_hash(package_id)]
        while bucket:
            if bucket.package_id == package_id:
                return bucket
            bucket = bucket.next
        
        raise KeyError(package_id)
    
    def __str__(self):
        result = []
        for node in self.table:
            chain = []
            while node:
                chain.append(node)
                node = node.next
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
    