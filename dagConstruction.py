import re
import networkx as nx
import matplotlib
import numpy as np
import spacy
import itertools as it
import os
nlp = spacy.load('en_core_web_sm')
from collections import defaultdict
import random
import copy
import sys
from utils import *
import pickle
import math
import scipy.stats as st

def dfs(l, vis, a, b):
    """Performs a Depth First Search.

    Parameters
    ----------
    l : Set of current edges
    vis : Boolean to check bit mask
    a : Current Vertex
    b : Target Vertex

    Returns
    -------
    Nothing

    """
    if a == b:
        return
    for i in l[a]:
        if vis[i] == False:
            vis[i] = True
            dfs(l, vis, i, b)
    return

def checkpath(l, a, b):
    N = len(l)
    vis = list()
    for i in range(N):
        vis.append(False)
    vis[a] = True
    dfs(l, vis, a, b)
    return vis[b]

def DAGcon(G, N):
    """A method to construct a Directed Acyclic graph

    Parameters
    ----------
    G : The subsumption set.
    N : The number of nodes.

    Returns
    -------
    Returns the DAG as a list.

    """
    l = list()
    caches = list()
    l_g = sorted(G, key=lambda x: G[x], reverse = True)

    for i in range(N):
        l.append(set())
        caches.append(set())

    for i in range(len(l_g)):
        if i%10000 == 0:
            print(i)
        a, b = l_g[i][0], l_g[i][1]
        if b in caches[a] or a in caches[b]:
            continue
        elif checkpath(l, b, a):
            caches[b].add(a)
            continue
        elif checkpath(l, a, b):
            caches[a].add(b)
            continue
        else:
            #print(a,b)
            caches[b].add(a)
            l[b].add(a)
    return l, caches
