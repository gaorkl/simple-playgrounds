import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('./perftest-results.csv')


# plot Time vs # of Agents

depth = False
fullBlind = True

mapSizes = df['mapSize'].unique()
for mapSize in mapSizes:
    filtered = df.loc[(df['depth'] == depth) & (df['mapSize'] == mapSize)]
    plt.plot(filtered['nbAgents'], filtered['perf'], "o")
plt.legend([str(m) + " x " + str(m) + " map" for m in mapSizes])

blindLabel = ( "full " if fullBlind else "")+( "" if depth else "blind")

plt.xlabel("Number of agents " + blindLabel)
plt.ylabel("Execution time for 100 steps (seconds)")
plt.show()

# plot Time vs Map Size

numbers = df['nbAgents'].unique()
for nb in numbers:
    filtered = df.loc[(df['depth'] == depth) & (df['nbAgents'] == nb)]
    plt.plot(filtered['mapSize'], filtered['perf'], "o")

blindLabel = ( "full " if fullBlind else "")+( "" if depth else "blind")
plt.legend([(str(n) + " agents "+ blindLabel) for n in numbers])
plt.xlabel("Map size (n by n)")
plt.ylabel("Execution time for 100 steps (seconds)")
plt.show()
