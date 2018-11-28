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

def insertNode(r, iL, l, j, i):
    if j == len(l):
        return
    if l[j][0] in iL:
        iL[l[j][0]].add(i)
    else:
        iL[l[j][0]] = set()
        iL[l[j][0]].add(i)
    if l[j][0] in r[0]:
        r[0][l[j][0]][1].add(i)
        insertNode(r[0][l[j][0]], iL, l, j+1, i)
    else:
        r[0][l[j][0]] = list()
        r[0][l[j][0]].append(dict())
        r[0][l[j][0]].append(set())
        r[0][l[j][0]][1].add(i)
        insertNode(r[0][l[j][0]], iL, l, j+1, i)
    return

def ConstructPrefixTree(l):
    root = list()
    root.append(dict())
    invertList = dict()
    for i in range(len(l)):
        insertNode(root, invertList, l[i][1], 0, i)
    return root, invertList
