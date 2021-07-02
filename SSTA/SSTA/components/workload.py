"""
"""
import logging

logging.basicConfig(
    filename='example.log',
    format='[%(asctime)s] p%(process)s:%(threadName)-4s - Func: %(funcName)-24s - %(filename)s@%(lineno)-2s - %(levelname)-8s - %(message)s',
    encoding='utf-8', level=logging.DEBUG
)


class Workload():
    def __init__(self, id, AZ=None, state=None, workload_type=None, node=None):
        if type(id) != int:
            raise TypeError("id should be int")
        if type(AZ) != str and AZ:
            raise TypeError("AZ should be a string")
        if type(state) != str and state:
            raise TypeError("state should be a string")
        if type(workload_type) != str and workload_type:
            raise TypeError("type_ should be a string")
        if type(node) != str and node:
            raise TypeError("node should be a string")

        self.id = id
        self.AZ = AZ
        self.state = state
        self.node = node
        self.type = workload_type

    def allocate_to_node(self, node):
        if type(node) != int:
            raise TypeError("node should be int")
        self.node = node
        self.state = 'busy'

    def evict(self):
        self.node = None
        self.state = 'pending'

    def __str__(self):
        return 'Workload: {}\t Type: {}\t AZ: {}\t node: {}\t State: {}'.format(
                self.id, self.type, self.AZ, self.node, self.state
            )
