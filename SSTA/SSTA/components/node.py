"""
"""

class Node():
    def __init__(self, id, AZ=None, state=None):
        if type(id) != int:
            raise TypeError("id should be int")
        if type(AZ) != str and AZ:
            raise TypeError("AZ should be a string")
        if type(state) != str and state:
            raise TypeError("state should be a string")

        self.id = id
        self.AZ = AZ
        self.state = state

    def mark_free(self):
        self.state = 'free'

    def mark_busy(self):
        self.state = 'busy'

    def __str__(self):
        return 'Node {} - AZ: {} - State: {}'.format(
            self.id, self.AZ, self.state
        )
