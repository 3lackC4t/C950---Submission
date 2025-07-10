from enum import Enum

"""
    Extends the Enum class to create a state-machine for package status
"""
class Status(Enum):
    AT_HUB = "At Hub"
    EN_ROUTE = "En Route"
    DELIVERED = "Delivered"
    DELAYED = "Delayed"

    # State machine manager is used as an interface to change a package's state.
    # Only returns a state object in the event of a valid state change
    def on_event(self, event: str):
        state_machine = {
            (Status.AT_HUB, "LOAD_TRUCK"): Status.EN_ROUTE,
            (Status.AT_HUB, "DELAY_PACKAGE"): Status.DELAYED,
            (Status.DELAYED, "LOAD_TRUCK"): Status.EN_ROUTE,
            (Status.EN_ROUTE, "DELIVER"): Status.DELIVERED,
            (Status.EN_ROUTE, "RETURN_TO_HUB"): Status.AT_HUB
        }

        new_state = state_machine.get((self, event))
        if new_state is None:
            raise ValueError(f"Invalid state transition {self.value} to {event}")
        
        return new_state