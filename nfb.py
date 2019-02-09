"""Example program to show how to read a multi-channel time series from LSL."""

from pylsl import StreamInlet, resolve_stream
import matplotlib.pyplot as plt
import numpy as np
from statistics import mean

channels =  {
	'F7':0, 'Fp1':1, 'Fp2':2, 'F8':3, 'F3':4, 'Fz':5, 'F4':6, 'C3':7,
	'Cz':8, 'P8':9, 'P7':10, 'Pz':11, 'P4':12, 'T3':13, 'P3':14, 'O1':15,
	'O2':16, 'C4':17, 'T4':18, 'A2':19, 'ACC20':20, 'ACC21':21, 'ACC22':22,
	'Packet Counter':23, 'TRIGGER':24
	}
#parameter
ROI_elec = 'Pz'
ROI = channels[ROI_elec]	#見たい電極
N = 512					#表示するデータ数＆FFTのサンプル数

#高速フーリエ変換
def fft():
    # データのパラメータ
    dt = 1 / samling_late          # サンプリング間隔
    t = np.arange(0, N*dt, dt) # 時間軸
    freq = np.linspace(0, 1.0/dt, N) # 周波数軸

    f = data_buffer

    # 高速フーリエ変換
    F = np.fft.fft(f)

    # 振幅スペクトルを計算
    Amp = np.abs(F)

    return freq, Amp

#プロットする関数
def plot():
    # get a new sample (you can also omit the timestamp part if you're not
    # interested in it)
    sample, timestamp = inlet.pull_sample()
    data_buffer.pop(0)
    data_buffer.append(sample[ROI] - m)
    f.set_data(x, data_buffer)
    freq, Amp = fft()
    F.set_data(freq, Amp)
    plt.pause(1 / samling_late)

#オフセット除去（平均を引いただけ）
def offset():
	for i in range(len(data_buffer)):
		data_buffer[i] = data_buffer[i] - m

	return data_buffer

if __name__ == '__main__':
	# first resolve an EEG stream on the lab network
	print("looking for an EEG stream...")
	streams = resolve_stream('type', 'EEG')
	# create a new inlet to read from the stream
	inlet = StreamInlet(streams[0])

	samling_late = inlet.info().nominal_srate()

	data_buffer = []	#ストリーミングデータ

	#data_bufferの初期化
	while len(data_buffer) < N:	
		sample, timestamp = inlet.pull_sample()
		data_buffer.append(sample[ROI])

	m = mean(data_buffer)

	data_buffer = offset()

	#初期値グラフ表示
	freq, Amp = fft()
	x = np.arange(0, N, 1)
	plt.figure(figsize=(10,6))
	plt.subplot(211)
	f, = plt.plot(x, data_buffer)
	plt.title(ROI_elec)
	plt.ylim(min(data_buffer)-1000, max(data_buffer)+1000)
	plt.subplot(212)
	F, = plt.plot(freq, Amp)
	plt.xlim(0, samling_late / 2)
	
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