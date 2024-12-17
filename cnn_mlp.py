# import cv2
# import tensorflow as tf
# import reg
from numpy import asarray

import numpy as np
import tensorflow as tf
from tensorflow import keras
import cv2


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))
def sigmoid_prime(x):
    return sigmoid(x) * (1.0 - sigmoid(x))
def tanh(x):
    return np.tanh(x)
def tanh_prime(x):
    return 1.0 - x ** 2
class MLP:
    def __init__(self, layers, activation='tanh'):
        if activation == 'sigmoid':
            self.activation = sigmoid
            self.activation_prime = sigmoid_prime
        elif activation == 'tanh':
            self.activation = tanh
            self.activation_prime = tanh_prime
            self.acv=0
        self.weights = []
        for i in range(1, len(layers) - 1):
            r = 2 * np.random.random((layers[i - 1] + 1, layers[i] + 1)) - 1
            self.weights.append(r)
        r = 2 * np.random.random((layers[i] + 1, layers[i + 1])) - 1
        self.weights.append(r)
    def fit(self, X, y, learning_rate=0.2, epochs=100):
        ones = np.atleast_2d(np.ones(X.shape[0]))
        X = np.concatenate((ones.T, X), axis=1)
        for k in range(epochs):
            if k % 1000 == 0:
                ep=0
            i = np.random.randint(X.shape[0])
            a = [X[i]]
            for l in range(len(self.weights)):
                dot_value = np.dot(a[l], self.weights[l])
                activation = self.activation(dot_value)
                a.append(activation)
            error = y[i] - a[-1]
            ep=ep+1
            deltas = [error * self.activation_prime(a[-1])]
            for l in range(len(a) - 2, 0, -1):
                deltas.append(deltas[-1].dot(self.weights[l].T) * self.activation_prime(a[l]))
            deltas.reverse()
            for i in range(len(self.weights)):
                layer = np.atleast_2d(a[i])
                delta = np.atleast_2d(deltas[i])
                self.weights[i] += learning_rate * layer.T.dot(delta)

    def predict(self, x):
        a = np.concatenate((np.ones(1).T, np.array(x)), axis=0)
        for l in range(0, len(self.weights)):
            a = self.activation(np.dot(a, self.weights[l]))
        return a
    def glcm_extract(self,data):
        # (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
        #data = np.asmatrix(data)
        encoder_input = keras.Input(shape=(28, 28, 1), name='img')
        x = keras.layers.Flatten()(encoder_input)
        encoder_output = keras.layers.Dense(25, activation="relu")(x)
        encoder = keras.Model(encoder_input, encoder_output, name='encoder')
        for x in data:
            self.acv+=x
        return encoder
    def result(self):
        return  self.acv

# if __name__ == '__main__':
#     img = cv2.imread('data\\greyscale.png', 0)
#     bp=1
#     numpydata = asarray(img)
#     X=(np.array(numpydata))
#     z=[]
#     for x in numpydata:
#         for y in x:
#             z.append(int(y))
#     X = np.array([[1, 0]])
#     y = np.array([1])
#
#     nn = BPNNetwork([2, 2, 1])
#     nn.fit(X, y,z)
#     print(nn.result())