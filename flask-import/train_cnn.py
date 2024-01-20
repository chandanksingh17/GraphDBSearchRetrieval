from model import CNN, SENet18b
from validation import get_time_string
from validation import list_summary
from validation import evaluate
from validation import get_mcc
from validation import get_f1score
from validation import get_recall
from validation import get_precision
from validation import get_accuracy
from validation import get_confusion_matrix
import os
import sys
import torch
import torch.nn.functional as F
import math
import time
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn import ensemble
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import matthews_corrcoef
from sklearn.linear_model import LogisticRegression


def predictions_from_output(scores):
    """
    Maps logits to class predictions.
    """
    prob = F.softmax(scores, dim=1)
    _, predictions = prob.topk(1)
    return predictions


def verify_model(model, X, Y, batch_size):
    """
    Checks the loss at initialization of the model and asserts that the
    training examples in a batch aren't mixed together by backpropagating.
    """
    print('Sanity checks:')
    criterion = torch.nn.CrossEntropyLoss()
    scores, _ = model(X, model.init_hidden(Y.shape[0]))
    print(' Loss @ init %.3f, expected ~%.3f' %
          (criterion(scores, Y).item(), -math.log(1 / model.output_dim)))

    mini_batch_X = X[:, :batch_size, :]
    mini_batch_X.requires_grad_()
    criterion = torch.nn.MSELoss()
    scores, _ = model(mini_batch_X, model.init_hidden(batch_size))

    non_zero_idx = 1
    perfect_scores = [[0, 0] for i in range(batch_size)]
    not_perfect_scores = [[1, 1] if i == non_zero_idx else [0, 0]
                          for i in range(batch_size)]

    scores.data = torch.FloatTensor(not_perfect_scores)
    Y_perfect = torch.FloatTensor(perfect_scores)
    loss = criterion(scores, Y_perfect)
    loss.backward()

    zero_tensor = torch.FloatTensor([0] * X.shape[2])
    for i in range(mini_batch_X.shape[0]):
        for j in range(mini_batch_X.shape[1]):
            if sum(mini_batch_X.grad[i, j] != zero_tensor):
                assert j == non_zero_idx, 'Input with loss set to zero has non-zero gradient.'

    mini_batch_X.detach()
    print('Backpropagated dependencies OK')

# Save the trained models
network_H1N1 = CNN()
torch.save(network_H1N1.state_dict(), './cnn_saved')
network_H3N2 = SENet18b()
torch.save(network_H3N2.state_dict(), './cnn_saved_H3N2')
network_H5N1 = SENet18b()
torch.save(network_H5N1.state_dict(), './cnn_saved_H5N1')