import json
import os
import pathlib

import networkx as nx
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from tqdm import tqdm

liker_graph = nx.DiGraph()

with open("bkp_tags/waldgang.json", encoding="utf-8") as f:
    data = json.load(f)

users = set()

def generate_user_node(user_dict, path_to_images, g):
    user_name = user_dict["username"]
    path_to_image = pathlib.Path(path_to_images, user_name)
    g.add_node(user_name, image = mpimg.imread(path_to_image) if os.path.exists(path_to_image) else mpimg.imread("img/bor.is_schnell.jpg"))
    return user_name

for post in tqdm(data[:50]):
    poster_name = post["user"]["username"]
    if liker_graph.has_node(poster_name):
        poster_node = liker_graph[poster_name]
    else:
        poster_node = generate_user_node(post["user"], "img", liker_graph)
    for liker in post.get("likers", []):
        liker_name = liker["username"]
        if liker_graph.has_node(liker_name):
            liker_node = liker_graph[liker_name]
        else:
            liker_node = generate_user_node(liker, "img", liker_graph)
        if liker_graph.has_edge(liker_name, poster_name):
            liker_graph[liker_name][poster_name]["weight"] += 1
        else:
            liker_graph.add_edge(liker_name, poster_name, weight=1)

# G=nx.Graph()
# G.add_node(0,image= img)
# G.add_node(1,image= img)
# G.add_node(2,image= img)
# G.add_node(3,image= img)
# G.add_node(4,image= img)
# G.add_node(5,image= img)
#
# print(G.nodes())
# G.add_edge(0,1)
# G.add_edge(0,2)
# G.add_edge(0,3)
# G.add_edge(0,4)
# G.add_edge(0,5)
# print(G.edges())
# pos=nx.circular_layout(G)

g = liker_graph

pos = nx.spring_layout(g)
fig=plt.figure(figsize=(50, 50))
ax=plt.subplot(111)
ax.set_aspect('equal')
nx.draw_networkx_edges(g,pos,ax=ax, width=10, edge_color="red")

plt.xlim(-1.5,1.5)
plt.ylim(-1.5,1.5)

trans=ax.transData.transform
trans2=fig.transFigure.inverted().transform

piesize=0.05 # this is the image size
p2=piesize/2.0
for n in tqdm(g):
    xx,yy=trans(pos[n]) # figure coordinates
    xa,ya=trans2((xx,yy)) # axes coordinates
    a = plt.axes([xa-p2,ya-p2, piesize, piesize])
    a.set_aspect('equal')
    a.imshow(g.nodes[n]['image'])
    a.axis('off')
ax.axis('off')
plt.show()
