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

#replacing non entity non frequent n gram by wildcard
def generate_sol_patterns(patterns, ngrams):
    """A method to generate SOL patterns given the textual patterns and ngrams.

    Parameters
    ----------
    patterns : type List
        Textual Patterns
    ngrams : type List of tuples
        NGrams

    Returns
    -------
    type List
        Returns SOL Patterns

    """
    pos_patterns = []
    for pattern_index, pattern in enumerate(patterns):
        words = pattern.split(" ")
        line = []
        pos_line = []
        for word_index, word in enumerate(words):
            if word.startswith("CHEMICAL_") or word.startswith("DISEASE_") or word.startswith("GENE_"):
                line.append("<ENTITY>")
                #pos_line.append("<ENTITY>")
            else:
                line.append(word)
                #pos_line.append(post[pattern_index][word_index])
        line = ' '.join(line)
        times = 0
        for string, suport in ngrams:
            if string in line:
                if times <= 4:
                    line = line.replace(" "+string+" ", " $ $ $ ")
                    times += 1
                else:
                    break
        words = line.split(" ")
        assert len(words) == len(pattern.split(" "))
        for i in range(len(words)):
            if words[i] != "$" and words[i] != "<ENTITY>" :
                words[i] = "*"
        toks = pattern.split(" ")
        for i in range(len(words)):
            if words[i] == "<ENTITY>" or words[i] == "$":
                pos_line.append(toks[i])
            elif words[i]!=words[i-1]:
                pos_line.append("*")
        strpos =  ' '.join(pos_line)
        pos_patterns.append(strpos)
    return pos_patterns

#replacing non entity non frequent n gram by wildcard
def generate_sol_pos_patterns(patterns, ngrams, post):
    """A method to generate SOL Patterns with POS tags.

    Parameters
    ----------
    patterns : type List
        Textual Patterns
    ngrams : type List of tuples
        NGrams
    post : type List
        POS Tag patterns

    Returns
    -------
    type List
        List of patterns with POS Tags

    """
    sol_pos_patterns = []
    for pattern_index, pattern in enumerate(patterns):
        words = pattern.split(" ")
        line = []
        pos_line = []
        for word_index, word in enumerate(words):
            if word.startswith("CHEMICAL_") or word.startswith("DISEASE_") or word.startswith("GENE_"):
                line.append("<ENTITY>")
                #pos_line.append("<ENTITY>")
            else:
                line.append(word)
                #pos_line.append(post[pattern_index][word_index])
        line = ' '.join(line)
        times = 0
        for string, suport in ngrams:
            if string in line:
                if times <= 4:
                    line = line.replace(" "+ string+ " ", " $ $ $ ")
                    times += 1
                else:
                    break
        words = line.split(" ")
        for i in range(len(words)):
            if words[i] != "$" and words[i] != "<ENTITY>" :
                words[i] = "*"
        for i in range(len(words)):
            if words[i] == "<ENTITY>":
                pos_line.append("<ENTITY>")
            elif words[i] == "$":
                pos_line.append(post[pattern_index][i])
            elif words[i]!=words[i-1]:
                pos_line.append("*")
        strpos =  ' '.join(pos_line)
        sol_pos_patterns.append(strpos)
    return sol_pos_patterns

def obtainpat(patlist):
    strpat = list()
    entlist = list()
    toks = patlist.split(" ")
    cnt = 0
    for w in toks:
        if w.startswith("CHEMICAL"):
            strpat.append("<CHEMICAL>")
            entlist.append(w)
        elif w.startswith("DISEASE"):
            strpat.append("<DISEASE>")
            entlist.append(w)
        elif w.startswith("GENE"):
            strpat.append("<GENE>")
            entlist.append(w)
        else:
            strpat.append(w)
            if w!="*":
                cnt+=1
    try:
        assert cnt%3==0
    except AssertionError:
        pass
    strpat = ' '.join(strpat)
    entstr = ' '.join(entlist)
    return strpat, entstr

def get_support_of_sols(sol_patterns, sol_pos_patterns):
    """A function to get support of each of the SOL and POS replaced SOL patterns.

    Parameters
    ----------
    sol_patterns : LIST
    sol_pos_patterns : LIST

    Returns
    -------
    type Tuple
        Returns tuple of dictionaries with keys as pattern and value as support.

    """
    suppcloud = dict()
    poscloud = dict()

    pats = list()
    for i in range(len(sol_patterns)):
        pat, ent = obtainpat(sol_patterns[i])
        if pat not in suppcloud:
            pats.append(pat)
            suppcloud[pat] = dict()
            pospat = sol_pos_patterns[i]
            poscloud[pat] = pospat
        if ent not in suppcloud[pat]:
            suppcloud[pat][ent] = 1
        else:
            suppcloud[pat][ent] += 1
    return pats, poscloud, suppcloud
