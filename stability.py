import copy
import errno
import json
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns
import shutil

from tqdm import tqdm

from SSTA.components import State
from SSTA import iteration

def rm_dir_p(dir):
    try:
        shutil.rmtree(dir)
    except FileNotFoundError:
        print("Folder does not exist")

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python ≥ 2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        # possibly handle other errno cases here, otherwise finally:
        else:
            raise

# Initialization
AZs = ['AZ-1', 'AZ-2', 'AZ-3']
WORKLOAD_TYPES = ['A', 'B', 'C']
MAX_NUMBER_OF_NODES = 15
INITIAL_NODE_ALLCATION_PER_AZ = [5, 5, 5]
INITIAL_WORKLOAD_TYPE_PER_AZ = [
    {'type': 'A', 'AZ': AZs[0], 'count': 3},
    {'type': 'A', 'AZ': AZs[1], 'count': 3},
    {'type': 'A', 'AZ': AZs[2], 'count': 3},
    {'type': 'B', 'AZ': AZs[0], 'count': 1},
    {'type': 'B', 'AZ': AZs[1], 'count': 1},
    {'type': 'B', 'AZ': AZs[2], 'count': 1},
    {'type': 'C', 'AZ': AZs[0], 'count': 1},
    {'type': 'C', 'AZ': AZs[1], 'count': 1},
    {'type': 'C', 'AZ': AZs[2], 'count': 1}
]
TARGET_WORKLOAD_NODE_ALLOCATION = [
    {'type': 'A', 'AZ': AZs[0], 'count': 3},
    {'type': 'A', 'AZ': AZs[1], 'count': 3},
    {'type': 'A', 'AZ': AZs[2], 'count': 3},
    {'type': 'B', 'AZ': AZs[0], 'count': 1},
    {'type': 'B', 'AZ': AZs[1], 'count': 1},
    {'type': 'B', 'AZ': AZs[2], 'count': 0},
    {'type': 'C', 'AZ': AZs[0], 'count': 1},
    {'type': 'C', 'AZ': AZs[1], 'count': 1},
    {'type': 'C', 'AZ': AZs[2], 'count': 0}
]


N_monte_carlo = 100
N_simulations = 10

if __name__ == '__main__':
    main_folder = './simulations'
    results = []
    initial_state = State(
        AZs=AZs,
        INITIAL_NODE_ALLCATION_PER_AZ=INITIAL_NODE_ALLCATION_PER_AZ,
        INITIAL_WORKLOAD_TYPE_PER_AZ=INITIAL_WORKLOAD_TYPE_PER_AZ,
        MAX_NUMBER_OF_NODES=MAX_NUMBER_OF_NODES
    )


    rm_dir_p(main_folder)


    for j in tqdm(range(N_simulations)):
        finish = False
        mkdir_p(main_folder + '/simulation-{}'.format(j))
        for i in range(N_monte_carlo):
            if i == 0:
                state = copy.deepcopy(initial_state)

            state, done = iteration(
                state=state,
                TARGET_WORKLOAD_NODE_ALLOCATION=TARGET_WORKLOAD_NODE_ALLOCATION,
                MAX_NUMBER_OF_NODES=MAX_NUMBER_OF_NODES,
                iteration_number=i
            )

            with open('./simulations/simulation-{}/iteration-{}.json'.format(j, i), 'w') as f:
                json.dump(initial_state.toJSON(), f)

            if done:
                results += [{'iteration': j, 'Steps': i, 'nodes': state.count_nodes(), 'time': state.time}]
                finish = True
                break

        if not finish:
            results += [{'iteration': j, 'Steps': None, 'nodes': state.count_nodes(), 'time': state.time}]

    df = pd.DataFrame(results)
    df.to_csv('results.csv')

    sns.set(color_codes=True)
    sns.set(style="white", palette="muted")
    sns.distplot(df['Steps'], bins=N_monte_carlo, hist_kws={'range': (0, min(N_monte_carlo, max(df['Steps'])*1.1))})

    plt.xlim(0, 10)
    plt.savefig("./hisogram_required_steps.png")
