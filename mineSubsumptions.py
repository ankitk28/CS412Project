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

def MineSubsumptions(T, l, iL, alpha):
    """Short summary.

    Parameters
    ----------
    l : List of patterns
    iL : List (invert list)
    alpha : type
        Description of parameter `alpha`.

    Returns
    -------
    Returns a list of subsumptions and its weights

    """
    S  = list()
    W = dict()
    for i in range(len(l)-1,-1,-1):
        si = dict()
        for j in range(len(l[i][1]) -1, -1, -1):
            ci = iL[l[i][1][j][0]]
            for pat in ci:
                if pat not in si:
                    si[pat] = 1
                else:
                    si[pat] += 1
        for j in si:
            if (len(l[j][1]) - si[j]) <= alpha and i!=j:
                S.append((j,i))
                W[(j,i)] = calculate_wilson_score(set(l[j][1]), set(l[i][1]), 0.95)
    return S, W
