

class Package:
    def __init__(self, note: str, address: str):
        self.note: str = note 
        self.address: str = address 
        self.data: dict[str:str] = {
            "NOTE": self.note,
            "ADDRESS": self.address
        }