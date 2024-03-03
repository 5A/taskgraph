import matplotlib.pyplot as plt
import networkx as nx

from taskgraph import TaskGraphProject

proj = TaskGraphProject()
task1 = proj.add_task(proj.task_root)
task2 = proj.add_task(proj.task_root)
task3 = proj.add_task(proj.task_root)
task4 = proj.add_task(task1)
task5 = proj.add_task(task2)
proj.add_dependency(task5, task1)

for layer, nodes in enumerate(nx.topological_generations(proj.dag)):
    # `multipartite_layout` expects the layer as a node attribute, so add the
    # numeric layer value as a node attribute
    for node in nodes:
        proj.dag.nodes[node]["layer"] = layer

# get lables
node_labels = dict()
for node in proj.dag.nodes:
    if "Name" in proj.metadata[node]:
        node_labels[node] = proj.metadata[node]["Name"]
    else:
        node_labels[node] = ""

# Compute the multipartite_layout using the "layer" node attribute
pos = nx.multipartite_layout(proj.dag, subset_key="layer")

fig, ax = plt.subplots()
nx.draw_networkx(proj.dag, pos=pos, ax=ax, labels=node_labels)
ax.set_title("DAG layout in topological order")
fig.tight_layout()
plt.show()
