import functools
import numpy as np
import json


def random_AZ(AZs):
    return AZs[np.random.randint(0, high=len(AZs), size=1)[0]]

def check_lists_equal(list1, list2):
    if len(list1) != len(list2):
        return False
    return functools.reduce(lambda i, j : i and j, map(lambda m, k: m == k, list1, list2), True)

def remove_duplicate_dictionaries(input_list):
    list_of_strings = set([json.dumps(dictionary) for dictionary in input_list])
    return [json.loads(item) for item in list_of_strings]

def total_dict_of_lists(workload_allocation):
    tot = 0
    for item in workload_allocation:
        tot += item['count']
    return tot


# Methods for assessing differences between the current state and the target state
def find_allocation(allocations, specific_allocation):
    allocations = list(filter(lambda allocation: allocation['type'] == specific_allocation['type'], allocations))
    allocations = list(filter(lambda allocation: allocation['AZ'] == specific_allocation['AZ'], allocations))
    if len(allocations) > 1:
        print("ALLOCATIONS")
        print(allocations)
        raise Exception("Too Many Exceptions were found! There seem to be duplicates")
    elif len(allocations) == 0:
        return {'type': specific_allocation['type'], 'AZ': specific_allocation['AZ'], 'count': 0}
    else:
        return allocations[0]

def allocation_diff(current_allocation, target_allocation):
    diffs = []
    for allocation in target_allocation:
        alloc = find_allocation(current_allocation, allocation)
        diffs += [{'type': allocation['type'], 'AZ': allocation['AZ'], 'diff': allocation['count'] - alloc['count']}]

    for allocation in current_allocation:
        alloc = find_allocation(target_allocation, allocation)
        diffs += [{'type': allocation['type'], 'AZ': allocation['AZ'], 'diff':  alloc['count'] - allocation['count']}]

    # Now we probably will have counted some differences twice, so let's fix that
    diffs = remove_duplicate_dictionaries(diffs)
    return check_require_action(diffs)

def check_require_action(diffs):
    return [diff for diff in diffs if diff['diff'] != 0]



