# -*- coding: utf-8 -*-
"""Patty.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1i384T3xDPcBHuGizmjMhbMihbiuILbcN
"""

import spacy.cli
spacy.cli.download("en_core_web_sm")

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

params = {'data_dir': "Data", 'corpus_fn': 'train1.ner.txt'}

#rad line return list of lines
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

#build tree from spacy output and given 2 entities it finds shortest path between 2 entities
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

#add adv mod dependency to setntence
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

!mkdir Data
!mv *.txt Data

!ls

corpus = read_corpus(os.path.join(params['data_dir'], params['corpus_fn']))

#section 3 generate textual patterns
def generate_textual_patterns(corpus):
    textual_patterns = []
    for i, sentence in enumerate(corpus):
        dep_parse = nlp(sentence)
        entity_length, entities = check_entities(sentence)
        try:
            if entity_length == 2:
                path = shortest_dependency_path(dep_parse, entities[0], entities[1])
                if len(path) != 2:
                    shortest_path = ' '.join(path)
                    textual_patterns.append(adv_mod_deps(shortest_path, dep_parse))
            elif entity_length > 2:
                print(entity_length)
                pairs = it.combinations(entities, 2)
                for pair in pairs:
                    path = shortest_dependency_path(dep_parse, pair[0], pair[1])
                    if len(path) != 2:
                        shortest_path = ' '.join(path)
                        textual_patterns.append(adv_mod_deps(shortest_path, dep_parse))
        except:
            pass
        if i%10000 == 0:
            print(len(textual_patterns))
    return(textual_patterns)

textual_patterns = generate_textual_patterns(corpus)

#textual_patterns = generate_textual_patterns(corpus)
textual_patterns = []
with open("Data/file.txt", 'rb') as f:
    for line in f:
        line = line.strip()
        line = str(line,'utf-8')
        w = line.split(" ")
        if(len(w) <=2):
            continue
        f = 0
        if w[0].startswith("CHEMICAL_") or w[0].startswith("DISEASE_") or w[0].startswith("GENE_"):
            pass
        else:
            f = 1
        if w[len(w)-1].startswith("CHEMICAL_") or w[len(w)-1].startswith("DISEASE_") or w[len(w)-1].startswith("GENE_"):
            pass
        else:
            f = 1
        if f == 0:
            fl = 0
            for ii in range(len(w)):
                i = w[ii]
                fl = 1*("CHEMICAL_" in i) + 1*("DISEASE_" in i) + 1*("GENE_" in i)
                if fl!=1:
                    w[ii]  = str.lower(i)
                if fl > 1:
                    break
            if fl > 1:
                #print(line)
                continue
            strmed = ' '.join(w[1:len(w)-1])
            strmed = str(w[0]) + " " + strmed + " " + str(w[len(w)-1]) 
            textual_patterns.append(strmed)

print(len(textual_patterns))

print(len(textual_patterns))
texpat = copy.deepcopy(textual_patterns)
textual_patterns = list()
for i in range(len(texpat)):
    w = texpat[i].split(" ")
    if(len(w) <=1):
        continue
    f = 0
    if w[0].startswith("CHEMICAL_") or w[0].startswith("DISEASE_") or w[0].startswith("GENE_"):
        pass
    else:
        f = 1
    if w[len(w)-1].startswith("CHEMICAL_") or w[len(w)-1].startswith("DISEASE_") or w[len(w)-1].startswith("GENE_"):
        pass
    else:
        f = 1
    if f == 0:
        textual_patterns.append(texpat[i])

print(len(textual_patterns))

post = list()
i = 0
for pat in textual_patterns:
    dep = nlp(pat)
    ls = list()
    for t in dep:
        ls.append(t.pos_)
    post.append(ls)
    i += 1
    if i <10:
        print(pat)
        print(ls)   
    if i%10000 == 0:
        print(i)

#textual_patterns, post

import pickle

with open('TexPatPosTag.pkl', 'wb') as f:
    pickle.dump([textual_patterns, post], f)

    
"""with open('TexPatPosTag.pkl', 'rb') as f:
    textual_patterns, post = pickle.load(f)
"""

def generate_seqmining_dataset(patterns):
    smining_dataset = []
    for pattern in patterns:
        words = pattern.split(" ")
        temp = []
        for word in words:
            if word.startswith("CHEMICAL_") or word.startswith("DISEASE_") or word.startswith("GENE_"):
                if len(temp) != 0:
                    temp = ' '.join(temp)
                    smining_dataset.append(temp)
                    temp = []
            else:
                temp.append(word)
        #if cnt!=2:
            #print(cnt)
    return smining_dataset

seqmining_dataset = generate_seqmining_dataset(textual_patterns)

print(len(seqmining_dataset))
print(seqmining_dataset[0])
print(seqmining_dataset[1])

#generate frequent n gram
def generate_frequent_ngrams(dataset, min_sup):
    gen_dict = defaultdict(int)
    for line in dataset:
        lst = line.split()
        for i in range(3, 4):
            for j in range(len(lst) - i + 1):
                gen_dict[tuple(lst[j:j + i])] += 1
    fs = {' '.join(k):v for k,v in gen_dict.items() if v >= min_sup}
    sorted_by_value = sorted(fs.items(), key=lambda kv: (-kv[1], kv[0]))
    return sorted_by_value

ngrams = generate_frequent_ngrams(seqmining_dataset, 5)

print(len(ngrams))
for i,j in enumerate(ngrams):
    if i == 10:
        break
    print(j)

#replacing non entity non frequent n gram by wildcard
def generate_sol_patterns(patterns, ngrams):
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

sol_patterns = generate_sol_patterns(textual_patterns, ngrams)
sol_pos_patterns = generate_sol_pos_patterns(textual_patterns, ngrams, post)

for i in range(len(sol_patterns)):
    assert len(sol_patterns[i].split(" ")) == len(sol_pos_patterns[i].split(" "))
with open('sp_spp.pkl', 'wb') as f:
    pickle.dump([sol_patterns, sol_pos_patterns], f)

    
"""with open('TexPatPosTag.pkl', 'rb') as f:
    textual_patterns, post = pickle.load(f)"""

print(len(sol_patterns))
for i in range(len(sol_patterns)):
    if sol_patterns[i].startswith("CHEMICAL") or sol_patterns[i].startswith("GENE") or sol_patterns[i].startswith("DISEASE"):
        continue
    #print(sol_patterns[i])#+"\n"+ sol_pos_patterns[i])
    #print(sol_patterns[i]+"\n"+ sol_pos_patterns[i])
    
for i in range(10):
    print(sol_patterns[i]+"\n"+ sol_pos_patterns[i])

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
        print(patlist)
    strpat = ' '.join(strpat)
    entstr = ' '.join(entlist)
    return strpat, entstr

def get_support_of_sols(sol_patterns, sol_pos_patterns):
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

pats, poscloud, suppcloud = get_support_of_sols(sol_patterns, sol_pos_patterns)

def generate_pos_replaced_patterns(patterns, textual_patterns):
    typed_support = defaultdict(int)
    untyped_support = defaultdict(int)
    typed_support_sets = defaultdict(list)
    untyped_support_sets = defaultdict(list)
    for pattern in patterns:
        xdoc = nlp(pattern)
        typed_sentence = []
        untyped_sentence = []
        for token in xdoc:
            m = str(token)
            if m.startswith("CHEMICAL_"):
                typed_sentence.append("<CHEMICAL>")
                untyped_sentence.append("<ENTITY>")
            elif m.startswith("DISEASE"):
                typed_sentence.append("<DISEASE>")
                untyped_sentence.append("<ENTITY>")
            elif m.startswith("GENE"):
                typed_sentence.append("<GENE>")
                untyped_sentence.append("<ENTITY>")
            elif token.pos_ == "ADJ" or token.pos_ == "ADV" or token.pos_ == 'VERB':
                typed_sentence.append("[" + token.pos_ + "]")
                untyped_sentence.append("[" + token.pos_ + "]")
            else:
                untyped_sentence.append(str(token))
                typed_sentence.append(str(token))
        typed_sentence = ' '.join(typed_sentence)
        untyped_sentence = ' '.join(untyped_sentence)
        typed_support[typed_sentence] += 1
        untyped_support[untyped_sentence] += 1
        typed_support_sets[typed_sentence].append(pattern)
        untyped_support_sets[untyped_sentence].append(pattern)
    return typed_support, untyped_support, typed_support_sets, untyped_support_sets

typed_support, untyped_support, typed_support_sets, untyped_support_sets = generate_pos_replaced_patterns(sol_patterns, textual_patterns)

print(len(typed_support), typed_support[0], typed_support[1])
print(len(untyped_support), untyped_support[0], untyped_support[1])
print(len(typed_support_sets), typed_support_sets[0], typed_support_sets[1])
print(len(untyped_support_sets), untyped_support_sets[0], untyped_support_sets[1])

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def get_support_confidence_of_sol_patterns(typed_set, untyped_set):
    supports = defaultdict(int)
    confidence = defaultdict(int)
    rep = {"<CHEMICAL>":"<ENTITY>", "<CHEMICAl>":"<ENTITY>", "<DISEASE>":"<ENTITY>", "<GENE>":"<ENTITY>"}
    for pattern in typed_set.keys():
        supports[pattern] = typed_set[pattern]
        upattern = replace_all(pattern, rep)
        confidence[pattern] = typed_set[pattern]/untyped_set[upattern]
    return supports, confidence

import pickle
"""
with open('objs.pkl', 'wb') as f:
    pickle.dump([ngrams, sol_patterns,typed_support, untyped_support, typed_support_sets, untyped_support_sets], f)

with open('objs.pkl', 'rb') as f:
    obj0, obj1, obj2 = pickle.load(f)
"""

pattern_supports, pattern_confidence = get_support_confidence_of_sol_patterns(typed_support, untyped_support)

print(len(pattern_supports))

k = 0
for id in untyped_support:
    k+=1
    print(len(id), id, untyped_support[id])
    if k ==10:
        break

k = 0
for id in untyped_support_sets:
    k+=1
    print(len(id), id, untyped_support_sets[id])
    if k ==1:
        break

k = 0
for id in typed_support:
    k+=1
    print(len(id), id, typed_support[id])
    if k ==10:
        break

k = 0
for id in typed_support_sets:
    k+=1
    print(len(id), id, typed_support_sets[id])
    if k ==1:
        break

"""# Section 5
boo
"""

with open('pat_pos_supp.pkl', 'wb') as f:
    pickle.dump([pats, poscloud, suppcloud], f)

    
"""with open('TexPatPosTag.pkl', 'rb') as f:
    textual_patterns, post = pickle.load(f)"""

import pickle

with open('pat_pos_supp.pkl', 'rb') as f:
    pats, poscloud, suppcloud = pickle.load(f)

#pats, poscloud, suppcloud
def registersupport(syncloudwithsupport, syncloud, activesyn, syn, supp):
    setsup = set(supp.keys())
    
    if syn not in activesyn:
        activesyn[syn] = True
        syncloud[syn] = list()
        syncloud[syn].append(copy.deepcopy(setsup))
        syncloudwithsupport[syn] = dict()
        for k in supp:
            syncloudwithsupport[syn][k] = supp[k]
        return
    
    if activesyn[syn] == False:
        return 
    
    if syn.startswith("<ENTITY>") == False:
        for sets in syncloud[syn]:
            if len(sets.intersection(setsup)) == 0:
                activesyn[syn] = False
            return
    
    syncloud[syn].append(copy.deepcopy(setsup))
    for k in supp:
        if k not in syncloudwithsupport[syn]:
            syncloudwithsupport[syn][k] = supp[k]
        else:
            syncloudwithsupport[syn][k] += supp[k]    
    return

#pattern is a list- each list elements will be one of entity, n-grams, *
#sup is set of tuples. tuples size will be equal to no. of entity in pattern
def gensyngen(pats, poscloud, supps):
    syncloud = dict()
    activesyn = dict()
    syncloudwithsupport = dict()
    #ghanta = 0
    for p in range(len(pats)):
        
        patstr = pats[p]
        pat = patstr.split(" ")
        poss = poscloud[patstr]
        poss = poss.split(" ")
        f = 0
        for i in range(len(poss)):
            if poss[i]=="<ENTITY>":
                pass
            elif poss[i] =="*":
                pass
            else:
                f = 1
                break
        if f==0:
            #ghanta+=1
            continue
        #typeuntye
        registersupport(syncloudwithsupport, syncloud, activesyn, patstr, supps[patstr])
        syn = copy.deepcopy(patstr)
        syn = syn.replace("<CHEMICAL>", "<ENTITY>")
        syn = syn.replace("<DISEASE>", "<ENTITY>")
        syn = syn.replace("<GENE>", "<ENTITY>")
        registersupport(syncloudwithsupport, syncloud, activesyn, syn, supps[patstr])
        
        #ngram contraction
        Nngram = list()
        for i in range(len(pat)):
            if pat[i]== "<CHEMICAL>" or pat[i]== "<DISEASE>" or pat[i]== "<GENE>" or pat[i] == "*":
                pass
            else:
                Nngram.append(i)
        try:
            assert len(Nngram)%3 == 0
        except AssertionError:
            print(patstr)
        
        for ii in range(0,len(Nngram),3):
            ing = Nngram[ii]
            syn = " "
            tok = []
            for i in range(len(pat)):
                if (i == ing+1) or (i== ing + 2):
                    pass
                elif i == ing:
                    if pat[i+3] != "*"  or pat[i-1] != "*":
                        tok.append("*")
                else:
                    tok.append(pat[i])
            syn = ' '.join(tok)
            syn = syn.replace(" * * "," * ")
            registersupport(syncloudwithsupport, syncloud, activesyn, syn, supps[patstr])
            syn = syn.replace("<CHEMICAL>", "<ENTITY>")
            syn = syn.replace("<DISEASE>", "<ENTITY>")
            syn = syn.replace("<GENE>", "<ENTITY>")
            registersupport(syncloudwithsupport, syncloud, activesyn, syn, supps[patstr])
       
        lenpos = 0
        
        for ipos in range(len(pat)):
            if (poss[ipos] == "<ENTITY>") or (poss[ipos] =="*"):
                continue
            else:
                lenpos += 1
                ptemp = copy.deepcopy(pat)
                
                ptemp[ipos] = poss[ipos]
                syn = ' '.join(ptemp)
                registersupport(syncloudwithsupport, syncloud, activesyn, syn, supps[patstr])
                
                ptemp[ipos] = "[WORD]"
                syn = ' '.join(ptemp)
                registersupport(syncloudwithsupport, syncloud, activesyn, syn, supps[patstr])
                
                ptemp[ipos] = poss[ipos]
                syn = ' '.join(ptemp)
                syn = syn.replace("<CHEMICAL>", "<ENTITY>")
                syn = syn.replace("<DISEASE>", "<ENTITY>")
                syn = syn.replace("<GENE>", "<ENTITY>")
                registersupport(syncloudwithsupport, syncloud, activesyn, syn, supps[patstr])
                
                ptemp[ipos] = "[WORD]"
                syn = ' '.join(ptemp)
                syn = syn.replace("<CHEMICAL>", "<ENTITY>")
                syn = syn.replace("<DISEASE>", "<ENTITY>")
                syn = syn.replace("<GENE>", "<ENTITY>")
                registersupport(syncloudwithsupport, syncloud, activesyn, syn, supps[patstr])
        
        
                
        if lenpos > 1:
            ptemp = copy.deepcopy(pat)
            for ipos in range(len(pat)):
                if (poss[ipos] == "<ENTITY>") or (poss[ipos] =="*"):
                    pass
                else:
                    ptemp[ipos] = poss[ipos]
            syn = ' '.join(ptemp)
            registersupport(syncloudwithsupport, syncloud, activesyn, syn, supps[patstr])
            ptemp = copy.deepcopy(pat)
            for ipos in range(len(pat)):
                if (poss[ipos] == "<ENTITY>") or (poss[ipos] =="*"):
                    pass
                else:
                    ptemp[ipos] = "[WORD]"
            syn = ' '.join(ptemp)
            registersupport(syncloudwithsupport, syncloud, activesyn, syn, supps[patstr])
            
        if lenpos > 1:
            ptemp = copy.deepcopy(poss)
            for ipos in range(len(pat)):
                if (poss[ipos] == "<ENTITY>") or (poss[ipos] =="*"):
                    pass
                else:
                    ptemp[ipos] = poss[ipos]
            syn = ' '.join(ptemp)
            registersupport(syncloudwithsupport, syncloud, activesyn, syn, supps[patstr])
            ptemp = copy.deepcopy(poss)
            for ipos in range(len(pat)):
                if (poss[ipos] == "<ENTITY>") or (poss[ipos] =="*"):
                    pass
                else:
                    ptemp[ipos] = "[WORD]"
            syn = ' '.join(ptemp)
            registersupport(syncloudwithsupport, syncloud, activesyn, syn, supps[patstr])
            
        #raise ValueError("bs")
        
    
    retsyncloud = dict()
    untypedcloud = dict()
    for syn in syncloud:
        if activesyn[syn] == True:
            if syn.startswith("<ENTITY>") == False:
                retsyncloud[syn] = copy.deepcopy(syncloudwithsupport[syn])
            else:
                untypedcloud[syn] = copy.deepcopy(syncloudwithsupport[syn])
    #print(ghanta)
    return retsyncloud, untypedcloud

p_s_c, utc = gensyngen(pats, poscloud, suppcloud)

with open('pscaftersec5.pkl', 'wb') as f:
    pickle.dump([p_s_c, utc], f)

import pickle

with open('pat_pos_supp.pkl', 'rb') as f:
    pats, poscloud, suppcloud = pickle.load(f)
with open('pscaftersec5.pkl', 'rb') as f:
    p_s_c, utc = pickle.load(f)

print(len(pats))
print(len(p_s_c),len(utc))
old_p_s_c = copy.deepcopy(p_s_c)

boo = 0

for i in old_p_s_c:
    sm = 0
    for j in p_s_c[i]:
        sm += p_s_c[i][j]
    if sm >=10:
        #print(i)
        boo +=1
    else:
        pass     
print(boo)

for i,j in enumerate(pats):
    print(j)
    if i ==9:
        break

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

strength_pat, conf_pat = get_strength_confidence(p_s_c, utc)

print(len(strength_pat), len(conf_pat))

with open('strengthconf.pkl', 'wb') as f:
    pickle.dump([strength_pat, conf_pat], f)

lconfpat = sorted(conf_pat.items(), key=lambda x: (x[1],strength_pat[x[0]]), reverse = True)
for i in range(0,10,1):
    print(lconfpat[i][0], lconfpat[i][1], strength_pat[lconfpat[i][0]])

"""# Section 7
Taxonomy Construction
input: p_s_c: a dicitonary of dict (tuple:int)

## Transforming input to different data type
converting input to a list of list of (support set, frequency) pair where the inner list is sorted by their val pair

Toy example (for debugging)
p_s_c = dict()
p_s_c["<Politician> was governor of <State>"] = dict()
p_s_c["<Politician> politician from <State>"] = dict()
p_s_c["<Person> daughter of <Person>"] = dict()
p_s_c["<Person> child of <Person>"] = dict()
A = ("A","a")
B = ("B","b")
C = ("C","c")
D = ("D","d")
E = ("E","e")
F = ("F","f")
G = ("G","g")
H = ("H","h")
I = ("I","i")
J = ("J","j")
K = ("K","k")
p_s_c["<Politician> was governor of <State>"][B]=75
p_s_c["<Politician> was governor of <State>"][C]=70
p_s_c["<Politician> was governor of <State>"][A]=80
p_s_c["<Politician> politician from <State>"][A]=80
p_s_c["<Politician> politician from <State>"][B]=75
p_s_c["<Politician> politician from <State>"][D]=66
p_s_c["<Politician> politician from <State>"][E]=64
p_s_c["<Politician> politician from <State>"][C]=70
p_s_c["<Person> daughter of <Person>"][F] = 78
p_s_c["<Person> daughter of <Person>"][H] = 66
p_s_c["<Person> daughter of <Person>"][G] = 75
p_s_c["<Person> child of <Person>"][I] = 88
p_s_c["<Person> child of <Person>"][F] = 78
p_s_c["<Person> child of <Person>"][J] = 87
p_s_c["<Person> child of <Person>"][K] = 64
p_s_c["<Person> child of <Person>"][G] = 75
"""

p_l_s_c = dict()
for it in p_s_c:
    p_l_s_c[it] = sorted(p_s_c[it].items(), key=lambda x: x[1], reverse = True)
l_p_l_s_c = list(p_l_s_c.items()) 
print(len(l_p_l_s_c))

for i in range(5):
    print(l_p_l_s_c[i][0])
    for j in range(min(5, len(l_p_l_s_c[i][1]))):
        print(l_p_l_s_c[i][1][j])

"""## Prefix Tree construction
Now, from the list obtained from previous step we construct prefix tree and also an inverted data list (storing the ids of patterns for every entity).
"""

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

"""def reverseTree(root):
    terminalNodes = list()
    
    return terminalNodes"""

def ConstructPrefixTree(l):
    root = list()
    root.append(dict())
    invertList = dict()
    for i in range(len(l)):
        #print(l[i][0])
        insertNode(root, invertList, l[i][1], 0, i)                 
    return root, invertList
T, invertList = ConstructPrefixTree(l_p_l_s_c)
#print(T)
#print(iL)

"""## Mining Subsumptions from the Prefix-Tree
input: prefix tree, inverted data list, subsumption treshold
output: set of subsumption relations
"""

# calculate_wilson_score(['a', 'b', 'c'], ['c', 'd', 'a', 'b'], 0.05)
import math
import scipy.stats as st

def calculate_wilson_score(s, b, confidence=0.05):
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    pos = len(list(set(s) & set(b)))
    n = len(s)
    phat = 1.0 * pos / n
    return (phat + z * z / (2 * n) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)

#calculate_wilson_score([ 'a','b'], ['a','b','c','d','e','f', 'g','h','i','j'], 0.95)

def MineSubsumptions(T, l, iL, alpha):
    S  = list()
    W = dict()
    #print(l)
    #print(iL)
    for i in range(len(l)-1,-1,-1):
        si = dict()
        #print(len(l[i][1]))
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
SubSump, SubsumW = MineSubsumptions(T, l_p_l_s_c, invertList, 0)
N = len(l_p_l_s_c)

for i in range(1000,1100,5):
    print(SubSump[i], SubsumW[SubSump[i]])
N = len(l_p_l_s_c)

with open('subsumedgeandweight', 'wb') as f:
    pickle.dump([SubSump, SubsumW], f)

"""## DAG construction

Toy Example
SubsumW = {(0, 1): 2, (1, 0): 3, (0,2) : 2, (1,2):1, (2,1): 1}
N = 8
"""

def dfs(l, vis, a, b):
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
    l = list()
    caches = list()
    l_g = sorted(G, key=lambda x: G[x], reverse = True)
    
    for i in range(N):
        l.append(set())
        caches.append(set())
    
    print(len(l_g))
    for i in range(len(l_g)):
        if i%10000 == 0:
            print(i)
        a, b = l_g[i][0], l_g[i][1]
        if b in caches[a] or a in caches[b]:
            continue
        elif checkpath(l, a, b):
            caches[a].add(b)
            continue
        elif checkpath(l, b, a):
            caches[b].add(a)
            continue
        else:
            #print(a,b)
            caches[a].add(b)
            l[a].add(b)
    
    return l, caches

dag, caches = DAGcon(SubsumW, N)
#print(dag)
#print(caches)



with open('dagcaches', 'wb') as f:
    pickle.dump([dag, caches], f)
