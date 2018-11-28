import networkx as nx
import math
import scipy.stats as st
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



def read_corpus(file):
    corpus = []
    with open(file, 'rb') as f:
        for line in f:
            line = line.strip()
            line = str(line,'utf-8')
            corpus.append(line)
    return corpus

#helper funtion to check entities
def check_entities(sentence):
    possible_entities = ["CHEMICAL_", "GENE_", "DISEASE_"]
    sentence_words = sentence.split(" ")
    total_present = 0
    entities_present = []
    for ent in possible_entities:
        result = [word for word in sentence_words if ent in word]
        if len(result) > 0:
            result = set(result)
            total_present += len(result)
            entities_present.extend(list(result))
    return total_present, entities_present

def shortest_dependency_path(doc, e1=None, e2=None):
    edges = []
    for token in doc:
        for child in token.children:
            edges.append(('{0}'.format(token),
                          '{0}'.format(child)))
    graph = nx.Graph(edges)
    try:
        shortest_path = nx.shortest_path(graph, source=e1, target=e2)
    except nx.NetworkXNoPath:
        shortest_path = []
    return shortest_path

def adv_mod_deps(x, dep_parse):
    for token in dep_parse:
        if token.dep_ == "advmod":
            for word in x:
                if str(token) == word:
                    x.insert(x.index(str(token)), str(token.head.text))
                    break
                if str(token.head.text) == word:
                    x.insert(x.index(str(token.head.text)), str(token))
                    break
    return x

def detype(pat):
    words = pat.split(" ")
    strret = list()
    for w in words:
        if w == "<CHEMICAL>" or w == "<DISEASE>" or w == "<GENE>":
            strret.append("<ENTITY>")
        else:
            strret.append(w)
    strret = ' '.join(strret)
    return strret

def get_strength_confidence(p_s_c, utc):
    strength = dict()
    confidence = dict()
    for pat in utc:
        strength[pat] = len(utc[pat])
    for pat in p_s_c:
        strength[pat] = len(p_s_c[pat])
    for pat in p_s_c:
        confidence[pat] = strength[pat] / strength[(detype(pat))]
    return strength, confidence

def convert_patterns_list(p_s_c):
    p_l_s_c = dict()
    for it in p_s_c:
        p_l_s_c[it] = sorted(p_s_c[it].items(), key=lambda x: x[1], reverse = True)
    l_p_l_s_c = list(p_l_s_c.items())
    return  l_p_l_s_c

# calculate_wilson_score(['a', 'b', 'c'], ['c', 'd', 'a', 'b'], 0.05)

def calculate_wilson_score(s, b, confidence=0.05):
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    pos = len(list(set(s) & set(b)))
    n = len(s)
    ph = 1.0 * pos / n
    sqr = math.sqrt((ph * (1 - ph) + z * z / (4 * n)) / n)
    numer = (ph + z * z / (2 * n))# - z * sqr) #uncomment for lower bound on wilson score
    denom = (1 + z * z / n)
    return numer/denom

#calculate_wilson_score([ 'a','b'], ['a','b','c','d','e','f', 'g','h','i','j'], 0.95)

# strength_pat, conf_pat = get_strength_confidence(p_s_c, utc)
def generate_pos_tags_for_patterns(textual_patterns, filename):
    post = list()
    i = 0
    for pat in textual_patterns:
        dep = nlp(pat)
        ls = list()
        for t in dep:
            ls.append(t.pos_)
        post.append(ls)
    print("Done")
    with open(filename, 'wb') as f:
        pickle.dump([textual_patterns, post], f)
    return post
