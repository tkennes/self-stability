import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot():
    df = pd.read_csv('./results.csv')
    N_monte_carlo = 100

    sns.set(color_codes=True)
    sns.set(style="white", palette="muted")
    sns.distplot(df['Steps'], bins=100, hist_kws={'range': (0, min(N_monte_carlo, max(df['Steps'])*1.1))})

    plt.xlim(0, N_monte_carlo)
    plt.savefig("./hisogram_required_steps.png")

if __name__ == '__main__':
    plot()

    filename = './simulations/simulation-1/iteration-1.json'
    with open(filename) as f:
      iter = json.loads(json.load(f))

    print(iter['nodes'])
    print(iter['workloads'])
