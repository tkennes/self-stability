"""Main module."""
from SSTA.helpers import allocation_diff
import logging

logging.basicConfig(
    filename='simulation.log',
    format='[%(asctime)s] p%(process)s:%(threadName)-4s - Func: %(funcName)-24s - %(filename)s@%(lineno)-2s - %(levelname)-8s - %(message)s',
    encoding='utf-8', level=logging.DEBUG
)

def update_workloads(state, TARGET_WORKLOAD_NODE_ALLOCATION, iteration_number):
    # Check whether workloads should be evicted
    differences = allocation_diff(state.get_scheduled_type_az_allocation(), TARGET_WORKLOAD_NODE_ALLOCATION)

    # If there are differences, there is work to be done
    if len(differences) > 0:
        logging.info("Iteration: {} - Differences were detected".format(iteration_number))
        logging.info("Iteration: {} - Differences: {}".format(iteration_number, differences))

        for difference in differences:
            # If there are too many workloads
            if difference['diff'] < 0:
                logging.info('Iteration: {} - Too many deployments of a workloads type: {}, AZ: {}. Evicting.'.format(
                    iteration_number, difference['type'], difference['AZ'])
                )
                state.evict_workload_by_type_and_az(
                    workload_type=difference['type'], AZ=difference['AZ'], number=abs(difference['diff'])
                )

            # If there are not enough worklaods
            else:
                # If there are free nodes
                if state.has_free_nodes():
                    logging.info("Iteration: {} - Trying to allocate workloads!".format(iteration_number))
                    state.update_workload_node_allocation()
        return state, False

    else:
        return state, True

def update_nodes(state, iteration_number, MAX_NUMBER_OF_NODES):
    done = True
    if state.has_non_allocated_workloads() and state.count_nodes() < MAX_NUMBER_OF_NODES:
        logging.info("Iteration: {} - added a node!".format(iteration_number))
        state.add_node()
        done = False

    if state.has_free_nodes():
        state.remove_node()
        logging.info("Iteration: {} - Removed a node!".format(iteration_number))
        done = False

    return state, done

def iteration(state, TARGET_WORKLOAD_NODE_ALLOCATION, MAX_NUMBER_OF_NODES, iteration_number):
    state, workloads_done = update_workloads(state, TARGET_WORKLOAD_NODE_ALLOCATION, iteration_number)
    state, nodes_done = update_nodes(state, iteration_number, MAX_NUMBER_OF_NODES)

    logging.info("Iteration: {} - Workloads done: {}".format(iteration_number, str(workloads_done)))
    logging.info("Iteration: {} - Nodes done: {}".format(iteration_number, str(nodes_done)))

    logging.info("Iteration: {} - Nodes: {}".format(iteration_number, state.print_nodes(return_=True)))
    logging.info("Iteration: {} - Workloads: {}".format(iteration_number, state.print_workloads(return_=True)))

    done = workloads_done and nodes_done
    return state, done
