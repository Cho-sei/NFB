from pylsl import StreamInlet, resolve_stream, resolve_byprop

streams = resolve_byprop("type", "EEG")
inlet = StreamInlet(streams[0])

stream_info = inlet.info()
print(stream_info.as_xml())