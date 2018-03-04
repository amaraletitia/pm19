import pygraphviz as pgv
import networkx as nx
import matplotlib.pyplot as plt
#Gtmp = pgv.AGraph('../result/state.dot')
G = nx.read_dot('../result/state.dot')
nx.draw(G)
plt.show()