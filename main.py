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
import pickle
import math
from utils import *
import scipy.stats as st
from dagConstruction import *
from mineSubsumptions import *
from ngramMining import *
from prefixTreeConstruction import *
from solPatternGeneration import *
from syntacticPatternGeneralization import *
from textualPatternGeneration import *

params = {'data_dir': sys.argv[1], 'corpus_fn': sys.argv[2]}
os.chdir(params['data_dir'])

corpus = read_corpus(os.path.join(params['data_dir'], params['corpus_fn']))
textual_patterns = generate_textual_patterns(corpus)
write_textual_patterns_to_file("file.txt", textual_patterns)
textual_patterns = convert_textual_patterns_to_lower_case("file.txt")
post = generate_pos_tags_for_patterns(textual_patterns, "TexPatPosTag.pkl")

seqmining_dataset = generate_seqmining_dataset(textual_patterns)
ngrams = generate_frequent_ngrams(seqmining_dataset, 5)

sol_patterns = generate_sol_patterns(textual_patterns, ngrams)
sol_pos_patterns = generate_sol_pos_patterns(textual_patterns, ngrams, post)
with open('sp_spp.pkl', 'wb') as f:
    pickle.dump([sol_patterns, sol_pos_patterns], f)

pats, poscloud, suppcloud = get_support_of_sols(sol_patterns, sol_pos_patterns)
with open('pat_pos_supp.pkl', 'wb') as f:
    pickle.dump([pats, poscloud, suppcloud], f)

p_s_c, utc = gensyngen(pats, poscloud, suppcloud)
with open('pscaftersec5.pkl', 'wb') as f:
    pickle.dump([p_s_c, utc], f)

strength_pat, conf_pat = get_strength_confidence(p_s_c, utc)
with open('strengthconf.pkl', 'wb') as f:
    pickle.dump([strength_pat, conf_pat], f)

lconfpat = sorted(conf_pat.items(), key=lambda x: (strength_pat[x[0]]), reverse = True)
with open("lconfpat.pkl", "wb") as f:
    pickle.dump(lconfpat, f)

l_p_l_s_c = convert_patterns_list(p_s_c)
T, invertList = ConstructPrefixTree(l_p_l_s_c)
SubSump, SubsumW = MineSubsumptions(T, l_p_l_s_c, invertList, 0)
with open('subsumedgeandweight', 'wb') as f:
    pickle.dump([SubSump, SubsumW], f)

N = len(l_p_l_s_c)
dag, caches = DAGcon(SubsumW, N)
with open('dagcaches', 'wb') as f:
    pickle.dump([dag, caches], f)
