"""Example program to show how to read a multi-channel time series from LSL."""

from pylsl import StreamInlet, resolve_stream, resolve_byprop,\
 	proc_clocksync, proc_dejitter, proc_monotonize
from collections import deque
import matplotlib.pyplot as plt
import numpy as np
import msvcrt

channels =  {
	'F7':0, 'Fp1':1, 'Fp2':2, 'F8':3, 'F3':4, 'Fz':5, 'F4':6, 'C3':7,
	'Cz':8, 'P8':9, 'P7':10, 'Pz':11, 'P4':12, 'T3':13, 'P3':14, 'O1':15,
	'O2':16, 'C4':17, 'T4':18, 'A2':19, 'ACC20':20, 'ACC21':21, 'ACC22':22,
	'Packet Counter':23, 'TRIGGER':24
	}
#parameter
#ROI_elec = 'O1'
#ROI = channels[ROI_elec]	#見たい電極
ROI = 0
N = 1024

#データ取得と更新
class BetaInlet(object):
    def __init__(self):
        print("looking for an EEG stream...")
        streams = resolve_byprop("type", "EEG")

        # create a new inlet to read from the stream
        proc_flags = proc_clocksync | proc_dejitter | proc_monotonize
        self.inlet = StreamInlet(streams[0], processing_flags=proc_flags)

        stream_info = self.inlet.info()
        stream_xml = stream_info.desc()
        chans_xml = stream_xml.child("channels")
        self.channel_list = []
        ch = chans_xml.child("channel")
        while ch.name() == "channel":
            self.channel_list.append(ch)
            ch = ch.next_sibling("channel")

    def update(self):
        max_samps = 3276*2
        data = np.nan * np.ones((max_samps, len(self.channel_list)), dtype=np.float32)
        _, timestamps = self.inlet.pull_chunk(max_samples=max_samps, dest_obj=data)
        data = data[:len(timestamps), :]
        return data, np.asarray(timestamps)

    def sampling_rate(self):
    	return self.inlet.info().nominal_srate()

#高速フーリエ変換
def fft():
    window = np.hamming(N)
    windowedData = window * data_buffer
    # データのパラメータ
    dt = 1 / sampling_rate          # サンプリング間隔
    t = np.arange(0, N*dt, dt) # 時間軸
    freq = np.linspace(0, 1.0/dt, N) # 周波数軸

    f = windowedData
    F = np.fft.fft(f)
    Amp = np.abs(F)

    return freq, Amp

#プロットする関数
def plot():
    # get a new sample (you can also omit the timestamp part if you're not
    # interested in it)
    sample, timestamp = betaIn.update()
    data_buffer.extend(sample.T[ROI])#-m
    f.set_data(x, data_buffer)
    plt.ylim(m - (m - min(data_buffer)) * 10, m + (max(data_buffer) - m) * 10)

    freq, Amp = fft()
    F.set_data(freq, Amp)
    plt.pause(1 / sampling_rate)

#オフセット除去（平均を引いただけ）
def offset():
	for i in range(len(data_buffer)):
		data_buffer[i] = data_buffer[i] - m

	return data_buffer

if __name__ == '__main__':

	betaIn = BetaInlet()
	sampling_rate = betaIn.sampling_rate()

	data_buffer = deque([], maxlen=N)	#ストリーミングデータ

	#data_bufferの初期化
	while len(data_buffer) < N:	
		sample, timestamp = betaIn.update()
		if len(sample) != 0:
			data_buffer.extend(sample.T[ROI])

	m = np.average(data_buffer)
    
	#data_buffer = offset()

	#初期値グラフ表示
	freq, Amp = fft()
	x = np.arange(0, len(data_buffer), 1)
	plt.figure(figsize=(10,6))
	plt.subplot(211)
	f, = plt.plot(x, data_buffer)
	#plt.title(ROI_elec)
	plt.ylim(m - (m - min(data_buffer)) * 10, m + (max(data_buffer) - m) * 10)
	plt.subplot(212)
	F, = plt.plot(freq, Amp)
	plt.xlim(0, 60)
	plt.ylim(0, np.average(Amp)/2)
	
	#無限プロット
	while True:
		plot()
	

"""
-------------------------------------------------------------
全チャネル表示
-------------------------------------------------------------

data_buffer = [['' for i in range(500)] for j in range(25)]
# create a new inlet to read from the stream
inlet = StreamInlet(streams[0])

for i in range(500):
	sample, timestamp = inlet.pull_sample()
	for j in range(25):
		data_buffer[j][i] = (sample[j])


x = np.arange(0, 500, 1)
plt.figure(figsize=(10,6))
for i in range(25):
	plt.plot(x, data_buffer[i])
#plt.ylim(0, 700000)

while True:
    # get a new sample (you can also omit the timestamp part if you're not
    # interested in it)
    sample, timestamp = inlet.pull_sample()
    for i in range(25):
    	data_buffer[i].pop(0)
    	data_buffer[i].append(sample[i])
    	plt.plot(x, data_buffer[i])
    plt.pause(0.001)
"""