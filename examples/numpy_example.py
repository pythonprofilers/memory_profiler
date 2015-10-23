import numpy as np
import scipy.signal


@profile
def create_data():
    ret = []
    for n in range(70):
        ret.append(np.random.randn(1, 70, 71, 72))
    return ret


@profile
def process_data(data):
    data = np.concatenate(data)
    detrended = scipy.signal.detrend(data, axis=0)
    return detrended


if __name__ == "__main__":
    data1 = create_data()
    data2 = process_data(data1)
