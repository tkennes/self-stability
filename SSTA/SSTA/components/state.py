import json
import logging

from SSTA.components.node import Node
from SSTA.components.workload import Workload
from SSTA.helpers import total_dict_of_lists
from SSTA.scheduling import eviction_heuristic, node_removal_heuristic, planning_heuristic, planning_AZ_heuristic


logging.basicConfig(
    filename='simulation.log',
    format='[%(asctime)s] p%(process)s:%(threadName)-4s - Func: %(funcName)-24s - %(filename)s@%(lineno)-2s - %(levelname)-8s - %(message)s',
    encoding='utf-8', level=logging.DEBUG
)


class State():
    ADD_NODE_TIME = 10*60
    REMOVE_NODE_TIME = 2*60
    EVICT_WORKLOAD_TIME = 30
    SCHEDULE_WORKLOAD_TIME = 30

    def __init__(
        self, workloads=None, nodes=None, iteration=None, start_time=None,
        AZs=None, INITIAL_NODE_ALLCATION_PER_AZ=None, INITIAL_WORKLOAD_TYPE_PER_AZ=None, MAX_NUMBER_OF_NODES=None
    ):
        self.iteration = iteration
        self.MAX_NUMBER_OF_NODES = MAX_NUMBER_OF_NODES
        if start_time:
            self.time = start_time
        else:
            self.time = 0

        # Initialize Workloads and Node Allocation
        if workloads and nodes:
            self.workloads = workloads
            self.nodes = nodes
        else:
            if not AZs:
                logging.error("AZs was not supplied to State, neither were workloads or nodes")
                raise Exception("Init failed")
            elif not INITIAL_NODE_ALLCATION_PER_AZ:
                logging.error("INITIAL_NODE_ALLCATION_PER_AZ was not supplied to State, neither were workloads or nodes")
                raise Exception("Init failed")
            elif not INITIAL_WORKLOAD_TYPE_PER_AZ:
                logging.error("INITIAL_WORKLOAD_TYPE_PER_AZ was not supplied to State, neither were workloads or nodes")
                raise Exception("Init failed")
            elif not MAX_NUMBER_OF_NODES:
                logging.error("MAX_NUMBER_OF_NODES was not supplied to State, neither were workloads or nodes")
                raise Exception("Init failed")

            self.AZs = AZs
            self.INITIAL_NODE_ALLCATION_PER_AZ = INITIAL_NODE_ALLCATION_PER_AZ
            self.INITIAL_WORKLOAD_TYPE_PER_AZ = INITIAL_WORKLOAD_TYPE_PER_AZ
            self.MAX_NUMBER_OF_NODES = MAX_NUMBER_OF_NODES

            self.set_initial_state()
            self.MAX_WORKLOAD_ID = max([workload.id for workload in self.workloads])
            self.update_workload_node_allocation()

    # Initialization
    def set_initial_state(self):
        if total_dict_of_lists(self.INITIAL_WORKLOAD_TYPE_PER_AZ) > self.MAX_NUMBER_OF_NODES:
            logging.warning("More Workloads are to be allocated than nodes exist")

        if sum(self.INITIAL_NODE_ALLCATION_PER_AZ) > self.MAX_NUMBER_OF_NODES:
            logging.error("More nodes are to be allocated than are allowed to exist. Increase MAX_NUMBER_OF_NODES or change your allocation")
            raise Exception("Init failed")

        self.nodes = []
        id = 1
        for i, AZ in enumerate(self.AZs):
            for _ in range(self.INITIAL_NODE_ALLCATION_PER_AZ[i]):
                self.nodes += [Node(id=id, AZ=AZ, state='free')]
                id += 1

        self.workloads = []
        id = 1
        for workload in self.INITIAL_WORKLOAD_TYPE_PER_AZ:
            for _ in range(workload['count']):
                self.workloads += [Workload(id=id, workload_type=workload['type'], AZ=workload['AZ'], state='pending', node=None)]
                id += 1


    # Counters
    def count_scheduled_workloads_type_az(self, workload_type, target_AZ):
        if type(target_AZ) != str:
            raise TypeError("target_AZ should be a string")
        if type(workload_type) != str:
            raise TypeError("workload_type should be a string")
        return len([workload for workload in self.workloads if workload.type == workload_type and workload.AZ == target_AZ and workload.node != None])

    def count_scheduled_workloads_type(self, workload_type):
        if type(workload_type) != str:
            raise TypeError("workload_type should be a string")
        return len([workload for workload in self.workloads if workload.type == workload_type and workload.node != None])

    def count_scheduled_workloads_az(self, target_AZ):
        if type(target_AZ) != str:
            raise TypeError("target_AZ should be a string")
        return len([workload for workload in self.workloads if workload.AZ == target_AZ and workload.node != None])

    def count_workloads_type_az(self, workload_type, target_AZ):
        if type(target_AZ) != str:
            raise TypeError("target_AZ should be a string")
        if type(workload_type) != str:
            raise TypeError("workload_type should be a string")
        return len([workload for workload in self.workloads if workload.type == workload_type and workload.AZ == target_AZ])

    def count_workloads_type(self, workload_type):
        if type(workload_type) != str:
            raise TypeError("workload_type should be a string")
        return len([workload for workload in self.workloads if workload.type == workload_type])

    def count_workloads_az(self, target_AZ):
        if type(target_AZ) != str:
            raise TypeError("target_AZ should be a string")
        return len([workload for workload in self.workloads if workload.AZ == target_AZ])

    def count_nodes(self):
        return len(self.nodes)

    def count_workloads(self):
        return len(self.workloads)

    # Creators
    def add_node(self, AZ=None):
        if type(AZ) != str and AZ:
            raise TypeError("AZ should be a str")
        if not AZ:
            AZ = planning_AZ_heuristic(self.AZs)

        new_id = self.max_node_id() + 1
        logging.debug("Adding Node with id: {} - AZ: {} - state: {}".format(new_id, AZ, 'free'))
        self.nodes += [Node(id=new_id, AZ=AZ, state='free')]
        self.add_time(self.ADD_NODE_TIME)

    def add_workload(self, workload_type, AZ=None):
        if type(AZ) != str and AZ:
            raise TypeError("AZ should be a str")
        if type(workload_type) != str:
            raise TypeError("workload_type should be a str")
        if not AZ:
            AZ = planning_AZ_heuristic(self.AZs)

        new_id = self.max_workload_id(increase=True) + 1
        logging.debug("Adding Workload with id: {} - type: {} - AZ: {} - state: {}".format(new_id, workload_type, AZ, 'pending'))
        self.workloads += [Workload(id=new_id, workload_type=workload_type, AZ=AZ, state='pending', node=None)]
        self.add_time(self.SCHEDULE_WORKLOAD_TIME)

    # Evictors / Removors
    def add_time(self, time_addition):
        self.time += time_addition

    def evict_workload_on_node(self, node_id):
        """ Evict A workload, called by the Node Scaler when there are too many nodes.
        This node is to be removed, and the workload should hence be evicted.

        Args:
            node_id (int): Integer-based ID of the node

        Raises:
            TypeError: node_id is not an integer
        """
        if type(node_id) != int:
            raise TypeError("node_id should be a int")
        workloads = self._get_workloads(['node'], [node_id])

        if len(workloads) == 0:
            logging.debug("No workloads where found for node_id: {}. Node already was free".format(node_id))
        else:
            for workload in workloads:
                logging.debug("Evicted Workload with id: {} - type: {} - AZ: {}".format(workload.id, workload.type, workload.AZ))
                workload.evict()
        self.add_time(self.EVICT_WORKLOAD_TIME)

    def evict_workload_by_type_and_az(self, workload_type, AZ, number=1):
        """ Evict A workload, called by the workload scheduler when there are too many workloads

        Args:
            workload_type (str): Type of the workload, string
            AZ (str): Name of the Availability Zone the workload should be deployed to (AZ)
            number (int, optional): The number of workloads to be evicted. Defaults to 1.

        Raises:
            Exception: eviction candidates < number: too many workloads to be evicted
            Exception: nodes > 1: to many nodes to be marked free
            Exception: nodes == 0: too little nodes to be marked free
        """
        eviction_candidate_workloads = self._get_workloads(['type', 'AZ', 'state'], [workload_type, AZ, 'busy'])

        if len(eviction_candidate_workloads) < number:
            raise Exception("Too many nodes are required to be evicted. I don't have that many nodes")
        else:
            eviction_workload_ids = [w.id for w in eviction_heuristic(eviction_candidate_workloads, number)]

        new_workloads = []
        for workload in self.workloads:
            if workload.id in eviction_workload_ids:
                # Update the node
                nodes = self._get_nodes(['id'], [workload.node])

                if len(nodes) > 1:
                    raise Exception("Too many Nodes where found. Workloads only run on one node")
                elif len(nodes) == 0:
                    raise Exception("No nodes where Found. Workloads should be running on a node. Otherwise they cannot be evicted")
                nodes[0].mark_free()
                logging.debug("Removed Workload with id: {}, type: {}, AZ: {}, state: {}".format(workload.id, workload.type, workload.AZ, workload.state))

                # Evict the workload (Yes, this is not totally logical, but otherwise you run into issues)
                workload.evict()
            else:
                new_workloads += [workload]
        self.workloads = new_workloads
        self.add_time(self.EVICT_WORKLOAD_TIME)

    def remove_node(self, number=1):
        if type(number) != int:
            raise Exception("number should be int")
        if self.count_nodes() < number:
            raise Exception("Too many nodes are required to be removed: I do not have that many")

        removal_node_ids = [n.id for n in node_removal_heuristic(self.nodes, number)]
        nodes = []
        for node in self.nodes:
            if node.id in removal_node_ids:
                # Evict the workload
                self.evict_workload_on_node(node.id)

                # Mark the node as free
                logging.debug("Removed node with id: {}, AZ: {}, state: {}".format(node.id, node.AZ, node.state))
                node.mark_free()

                # And do not incorporate this node in the new list of nodes
            else:
                nodes += [node]
        self.nodes = nodes
        self.add_time(self.REMOVE_NODE_TIME)


    # Getters
    def _get_nodes(self, keys, values):
        if type(keys) != list:
            raise TypeError("key should be a list")
        if type(values) != list:
            raise TypeError("value should be a list")

        nodes = self.nodes
        for key, value in zip(keys, values):
            nodes = list(filter(lambda node: getattr(node, key) == value, nodes))
        return nodes

    def _get_workloads(self, keys, values):
        if type(keys) != list:
            raise TypeError("key should be a list")
        if type(values) != list:
            raise TypeError("value should be a list")

        workloads = self.workloads
        for key, value in zip(keys, values):
            workloads = list(filter(lambda workload: getattr(workload, key) == value, workloads))
        return workloads

    def get_non_allocated_workloads(self):
        return self._get_workloads(['node', 'state'], [None, 'pending'])

    def get_free_nodes(self):
        return self._get_nodes(['state'], ['free'])

    def get_scheduled_type_az_allocation(self):
        return (
            [{'type': 'A', 'AZ': AZ, 'count': self.count_scheduled_workloads_type_az('A', AZ)} for AZ in self.AZs] +
            [{'type': 'B', 'AZ': AZ, 'count': self.count_scheduled_workloads_type_az('B', AZ)} for AZ in self.AZs] +
            [{'type': 'C', 'AZ': AZ, 'count': self.count_scheduled_workloads_type_az('C', AZ)} for AZ in self.AZs]
        )

    def get_total_workloads(self):
        return len(self.workloads)

    def get_total_nodes(self):
        return len(self.nodes)

    # Printers
    def __str__(self):
        return self.print_nodes(return_=True) + '\n\n' + self.print_workloads(return_=True)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def print_nodes(self, return_=False):
        str_ = '----- Nodes -----\n'
        for node in self.nodes:
            str_ += str(node) + '\n'
        if not return_:
            print(str_)
        else:
            return str_

    def print_workloads(self, return_=False):
        str_ = '----- Workloads -----\n'
        for workload in self.workloads:
            str_ += str(workload) + '\n'
        if not return_:
            print(str_)
        else:
            return str_

    # Property Checkers
    def has_free_nodes(self):
        return len(self.get_free_nodes()) > 0

    def has_non_allocated_workloads(self):
        return len(self.get_non_allocated_workloads()) > 0

    def max_node_id(self):
        return max([node.id for node in self.nodes])

    def max_workload_id(self, increase=False):
        if increase:
            self.MAX_WORKLOAD_ID = self.MAX_WORKLOAD_ID + 1
            return self.MAX_WORKLOAD_ID - 1
        else:
            return self.MAX_WORKLOAD_ID

    # Setters
    def set_times(self, add_node_time=None, remove_node_time=None, evict_workload_time=None, schedule_workload_time=None):
        if add_node_time:
            self.ADD_NODE_TIME = add_node_time
        if remove_node_time:
            self.REMOVE_NODE_TIME = remove_node_time
        if evict_workload_time:
            self.EVICT_WORKLOAD_TIME = evict_workload_time
        if schedule_workload_time:
            self.SCHEDULE_WORKLOAD_TIME = schedule_workload_time

    # Updaters
    def update_node(self, id, key, value):
        if type(id) != str:
            raise TypeError("id should be a string")
        if type(key) != str:
            raise TypeError("key should be a str")
        if type(value) != str:
            raise TypeError("value should be a str")

        nodes = []
        for node in self.nodes:
            if node.id == id:
                setattr(node, key, value)
        self.nodes = nodes

    def update_workload(self, id, key, value):
        if type(id) != str:
            raise TypeError("id should be a string")
        if type(key) != str:
            raise TypeError("key should be a str")
        if type(value) != str:
            raise TypeError("value should be a str")

        workloads = []
        for workload in self.workloads:
            if workload.id == id:
                setattr(workload, key, value)
        self.workloads = workloads

    def update_workload_node_allocation(self):
        for workload in self.workloads:
            if not workload.node:
                free_nodes = self._get_nodes(['state', 'AZ'], ['free', workload.AZ])
                if len(free_nodes) > 0:
                    target_node = planning_heuristic(free_nodes)

                    logging.debug("Allocate workload: {} - {} - {}, to node: {} - {}".format(
                        workload.id, workload.type, workload.AZ,
                        target_node.id, target_node.AZ
                    ))
                    # Update Nodes
                    target_node.mark_busy()

                    # Update Workloads
                    workload.allocate_to_node(target_node.id)
