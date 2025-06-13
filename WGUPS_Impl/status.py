from enum import Enum

class Status(Enum):
    AT_HUB = "At Hub"
    EN_ROUTE = "En Route"
    DELIVERED = "Delivered"
    DELAYED = "Delayed"