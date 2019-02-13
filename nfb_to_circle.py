"""Example program to show how to read a multi-channel time series from LSL."""

from pylsl import StreamInlet, resolve_stream, resolve_byprop,\
 	proc_clocksync, proc_dejitter, proc_monotonize
from psychopy import visual, event, core
from collections import deque
import numpy as np
import threading

channels =  {
	'F7':0, 'Fp1':1, 'Fp2':2, 'F8':3, 'F3':4, 'Fz':5, 'F4':6, 'C3':7,
	'Cz':8, 'P8':9, 'P7':10, 'Pz':11, 'P4':12, 'T3':13, 'P3':14, 'O1':15,
	'O2':16, 'C4':17, 'T4':18, 'A2':19, 'ACC20':20, 'ACC21':21, 'ACC22':22,
	'Packet Counter':23, 'TRIGGER':24
	}
#parameter
ROI_elec = 'O1'
ROI = channels[ROI_elec]	#見たい電極
N = 1024
ex_duration = 5			#秒

#データ取得と更新
class BetaInlet(object):
    def __init__(self):
        print("looking for an EEG stream...")
        streams = resolve_byprop("type", "EEG")

        # create a new inlet to read from the stream
        proc_flags = proc_clocksync | proc_dejitter | proc_monotonize
        self.inlet = StreamInlet(streams[0], processing_flags=proc_flags)

    def update(self):
        max_samps = 3276*2
        data = np.nan * np.ones((max_samps, 25), dtype=np.float32)
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

if __name__ == '__main__':

	betaIn = BetaInlet()
	sampling_rate = betaIn.sampling_rate()

	data_buffer = deque([], maxlen=N)	#ストリーミングデータ

	#data_bufferの初期化
	while len(data_buffer) < sampling_rate:	
		sample, timestamp = betaIn.update()
		if len(sample) != 0:
			data_buffer.extend(sample.T[ROI])

	m = np.average(data_buffer)

	#psychopy初期化
	win = visual.Window(
		size=(1920, 1080), units='pix', fullscr=True, allowGUI=False)

	FB_circle = visual.Circle(
		win, edges=32, fillColor='green', lineColor='green')

	clock = core.Clock()

	t_start = clock.getTime()
	t_duration = clock.getTime() - t_start

	while t_duration < ex_duration:
		sample, timestamp = betaIn.update()
		data_buffer.extend(sample.T[ROI])
		freq, Amp = fft()
		alpha = Amp[8:13]
		circle_radius = np.average(alpha)
		FB_circle.setRadius(circle_radius * 0.01)
		FB_circle.setOpacity(0.5)
		FB_circle.draw()

		t_duration = clock.getTime() - t_start

		win.flip()

