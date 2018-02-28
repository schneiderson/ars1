import h5py
from keras.models import Sequential
from keras.layers import Dense

filepath = "weights/w1.hdf5"

# Build a straight forwards sequential ANN
model = Sequential()
# INPUT+HIDDEN LAYER: Takes 12 inputs from the IR sensors, feeds to 6 hidden nodes
model.add(Dense(6, activation='sigmoid', input_shape=(12,)))
# OUTPUT: tanh squishes engine power for L/R wheels in range [-1,1]
model.add(Dense(2, activation='tanh'))

# Print a summary of the neural network structure
model.summary()

# Retrieve the weights as an array of arrays, so that they can be evolved
weights = model.get_weights()

for ar in weights:
    print(ar)

# Set the model weights from the array of arrays, so that evolved weights can be applied
model.set_weights(weights)

# Store the weights in a file, so we can load them later
model.save_weights(filepath)

# Load the weights from a file
model.load_weights(filepath, by_name=False)
