import ECA as eca
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# randbstr randomly generates a binary string of input length.
def randbstr(stringlength):
    rng = np.random.default_rng()
    key = ''
    for i in range(stringlength):
        temp = str(rng.integers(1, endpoint = True))
        key += temp
    return key

# initcentercell returns binary string with a single 1 in the center,
# taking as input the number of zeroes on either side of the 1.
def initcentercell(numZeroes):
    key = ''
    for i in range(numZeroes):
        key += '0'
    key += '1'
    for i in range(numZeroes):
        key += '0'
    return key

rules = np.empty(256, dtype='U8')

# This loop creates an array of 8-digit strings of the binary
# representations of integers 0-255.
for x in range(256):
    rules[x] = np.binary_repr(x,8)

myrule = eca.ECA(rules[110])

data = myrule.N_Gens(randbstr(10000), 'periodic', 11250)

hsv_modified = plt.cm.get_cmap('hsv',256)

bg = ListedColormap(hsv_modified(np.linspace(0.3, 0.7, 256)))

fig, ax = plt.subplots(figsize=(16,9))

plt.imshow(data, cmap=bg, interpolation="nearest")
plt.show()

