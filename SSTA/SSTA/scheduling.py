import numpy as np
import logging


def eviction_heuristic(eviction_candidate_workloads, number):
    if len(eviction_candidate_workloads) == 0:
        message = "The list of candidate workloads is empty"
        logging.error(message)
        raise Exception(message)
    indices = np.random.randint(0, high=len(eviction_candidate_workloads), size=number).tolist()
    return [eviction_candidate_workloads[index] for index in indices]

def node_removal_heuristic(removal_candidate_nodes, number):
    if len(removal_candidate_nodes) == 0:
        message = "The list of candidate removal nodes is empty"
        logging.error(message)
        raise Exception(message)
    indices = np.random.randint(0, high=len(removal_candidate_nodes), size=number).tolist()
    return [removal_candidate_nodes[index] for index in indices]

def planning_heuristic(candidate_nodes):
    if len(candidate_nodes) == 0:
        message = "The list of candidate planning nodes is empty"
        logging.error(message)
        raise Exception(message)
    index = np.random.randint(0, high=len(candidate_nodes), size=1)[0]
    return candidate_nodes[index]

def planning_AZ_heuristic(AZs):
    if len(AZs) == 0:
        message = "The list of candidate planning AZs is empty"
        logging.error(message)
        raise Exception(message)
    index = np.random.randint(0, high=len(AZs), size=1)[0]
    return AZs[index]
