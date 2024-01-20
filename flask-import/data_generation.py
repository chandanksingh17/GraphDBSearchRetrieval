# -*- coding: utf-8 -*-
"""
Created on Thu May 30 09:31:29 2019

@author: yinr0002
"""

import os, sys
import pandas as pd
import numpy as np
import random
import torch
import warnings

from Bio import SeqIO
from model import calculate_label
from model import generate_feature
from model import strain_selection
from model import replace_uncertain_amino_acids
from model import train_test_split_data

warnings.filterwarnings('ignore')

def cnn_training_data(Antigenic_dist, seq):
    raw_data = strain_selection(Antigenic_dist, seq)
    #replace unambiguous with substitutions
    Btworandom = 'DN'
    Jtworandom = 'IL'
    Ztworandom = 'EQ'
    Xallrandom = 'ACDEFGHIKLMNPQRSTVWY'
    for i in range(0, 2):
        for j in range(0, len(raw_data[0])):
            seq = raw_data[i][j]
            seq = seq.replace('B',random.choice(Btworandom))
            seq = seq.replace('J',random.choice(Jtworandom))
            seq = seq.replace('Z',random.choice(Ztworandom))
            seq = seq.replace('X',random.choice(Xallrandom))
            raw_data[i][j] = seq

    #embedding with ProVect    
    df = pd.read_csv('protVec_100d_3grams.csv', delimiter = '\t')
    trigrams = list(df['words'])
    trigram_to_idx = {trigram: i for i, trigram in enumerate(trigrams)}
    trigram_vecs = df.loc[:, df.columns != 'words'].values

    feature = []
    label = raw_data[2]
    for i in range(0, len(raw_data[0])):
        trigram1 = []
        trigram2 = []
        strain_embedding = []
        seq1 = raw_data[0][i]
        seq2 = raw_data[1][i]
    
        for j in range(0, len(raw_data[0][0])-2):
            trigram1 = seq1[j:j+3]
            if trigram1[0] == '-' or trigram1[1] == '-' or trigram1[2] == '-':
                tri1_embedding = trigram_vecs[trigram_to_idx['<unk>']]
            else:
                tri1_embedding = trigram_vecs[trigram_to_idx[trigram1]]
        
            trigram2 = seq2[j:j+3]
            if trigram2[0] == '-' or trigram2[1] == '-' or trigram2[2] == '-':
                tri2_embedding = trigram_vecs[trigram_to_idx['<unk>']]
            else:
                tri2_embedding = trigram_vecs[trigram_to_idx[trigram2]]
        
            tri_embedding = tri1_embedding - tri2_embedding
            strain_embedding.append(tri_embedding)
  
        feature.append(strain_embedding)
    return feature, label
    





































