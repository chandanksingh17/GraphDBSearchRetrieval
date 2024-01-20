from http.client import responses
from flask import Flask, request, render_template, Response, jsonify
from flask_cors import CORS, cross_origin
import subprocess
import os
import sys
import numpy as np
import pandas as pd
import torch
import warnings

from model import CNN, SENet18b
from data_generation import cnn_training_data
from train_cnn import predictions_from_output

app = Flask(__name__, template_folder='../demo')

# cors = CORS(app, resources={
#             r"/predict": {"origins": "*"}})
cors = CORS(app)

# load trained model here
network_H1N1 = CNN()
saved_state = torch.load('./cnn_saved')
network_H1N1.load_state_dict(saved_state)
print('H1N1 modal loaded')

# load trained model here
network_H3N2 = SENet18b()
saved_state_H3N2 = torch.load('./cnn_saved_H3N2')
network_H3N2.load_state_dict(saved_state_H3N2)
print('H3N2 modal loaded')

# load trained model here
network_H5N1 = SENet18b()
saved_state_H5N1 = torch.load('./cnn_saved_H5N1')
network_H5N1.load_state_dict(saved_state_H5N1)
print('H5N1 modal loaded')


@app.route('/')
def home():
   return render_template('index.html')

@app.route('/predict/', methods=['POST'])
def predict():
    '''
    strains1 : []
    seqs1 : []
    strains2: []
    seqs2 : []
    '''

    json_data = request.json
    strains1 = json_data.get('strains1', [])
    strains2 = json_data.get('strains2', [])
    seqs1 = json_data.get('seqs1', [])
    seqs2 = json_data.get('seqs2', [])

    antigenic_pairs = []
    sequences = []
    for i in range(len(strains1)):
        antigenic_pairs.append({
            'Strain1': strains1[i],
            'Strain2': strains2[i],
            'Distance': 0,
        })
        sequences.append({
            'seq': seqs1[i],
            'description': strains1[i],
        })
        sequences.append({
            'seq': seqs2[i],
            'description': strains2[i],
        })

    antigenic_pair_data = pd.DataFrame(antigenic_pairs)
    sequence_data = pd.DataFrame(sequences)
    print(antigenic_pair_data)
    print(sequence_data)

    feature, label = cnn_training_data(antigenic_pair_data, sequence_data)

    train_x = np.array(feature)
    train_y = np.array(label)

    train_x = np.reshape(train_x, (np.array(train_x).shape[0], 1, np.array(
        train_x).shape[1], np.array(train_x).shape[2]))

    train_x = torch.tensor(train_x, dtype=torch.float32)
    train_y = torch.tensor(train_y, dtype=torch.int64)

    test_scores = network_H1N1(train_x)
    predictions = predictions_from_output(test_scores)
    predictions = predictions.view_as(train_y).numpy()

    results = []
    for i in range(len(predictions)):
        results.append({
            '{}||{}'.format(strains1[i], strains2[i]): int(predictions[i])
        })

    return jsonify(results)


@app.route('/predict_by_type/<sub_type>/', methods=['POST'])
def predict_by_type(sub_type):
    '''
    strains1 : []
    seqs1 : []
    strains2: []
    seqs2 : []
    '''
    print(sub_type)
    json_data = request.json
    strains1 = json_data.get('strains1', [])
    strains2 = json_data.get('strains2', [])
    seqs1 = json_data.get('seqs1', [])
    seqs2 = json_data.get('seqs2', [])

    antigenic_pairs = []
    sequences = []
    for i in range(len(strains1)):
        antigenic_pairs.append({
            'Strain1': strains1[i],
            'Strain2': strains2[i],
            'Distance': 0,
        })
        sequences.append({
            'seq': seqs1[i],
            'description': strains1[i],
        })
        sequences.append({
            'seq': seqs2[i],
            'description': strains2[i],
        })

    antigenic_pair_data = pd.DataFrame(antigenic_pairs)
    sequence_data = pd.DataFrame(sequences)
    print(antigenic_pair_data)
    print(sequence_data)

    feature, label = cnn_training_data(antigenic_pair_data, sequence_data)

    train_x = np.array(feature)
    train_y = np.array(label)

    train_x = np.reshape(train_x, (np.array(train_x).shape[0], 1, np.array(
        train_x).shape[1], np.array(train_x).shape[2]))

    train_x = torch.tensor(train_x, dtype=torch.float32)
    train_y = torch.tensor(train_y, dtype=torch.int64)

    if sub_type == "H5N1":
        test_scores = network_H5N1(train_x)
    elif sub_type == "H3N2":
        test_scores = network_H3N2(train_x)
    else:
        test_scores = network_H1N1(train_x)

    predictions = predictions_from_output(test_scores)
    predictions = predictions.view_as(train_y).numpy()

    results = []
    for i in range(len(predictions)):
        results.append({
            '{}||{}'.format(strains1[i], strains2[i]): int(predictions[i])
        })

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, port=8888, host='0.0.0.0')
