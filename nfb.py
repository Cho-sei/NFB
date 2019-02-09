import matplotlib
matplotlib.interactive( True )
matplotlib.use( 'WXAgg' )

from pylsl import StreamInlet, resolve_stream

import wx

class myWxPlot(wx.Panel):
    def __init__( self, parent):
        from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
        from matplotlib.figure import Figure
        
        self.parent = parent
        wx.Panel.__init__( self, parent)

        #matplotlib figure
        self.figure = Figure( None )
        self.figure.set_facecolor( (0.7,0.7,1.) )
        self.subplot = self.figure.add_subplot( 111 )
        #canvas
        self.canvas = FigureCanvasWxAgg( self, -1, self.figure )
        self.canvas.SetBackgroundColour( wx.Colour( 100,255,255 ) )

        self.buffer = [] * 500

        self.RecieveData()
        self._SetSize()
        self.draw()

        self.timer = wx.Timer(self, 0.01)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.timer.Start(1000)

    def update(self, event):
    	self.RecieveData()
    	self.draw()

    def _SetSize( self ):
        size = tuple( self.parent.GetClientSize() )
        self.SetSize( size )
        self.canvas.SetSize( size )
        self.figure.set_size_inches( float( size[0] )/self.figure.get_dpi(),
                                     float( size[1] )/self.figure.get_dpi() )

    def draw(self):
        import numpy as np

        theta = np.arange(0,200, 0.1)
       # x = self.timestamp
        x = self.buffer

        self.subplot.plot(x, '-r')

        self.subplot.set_title("Sample", fontsize = 12)
        self.subplot.set_xlabel("x")
#        self.subplot.set_ylabel("y")
        self.subplot.set_xlim([0, 4])
#        self.subplot.set_ylim([-4, 4])
        self.canvas.draw()

    def RecieveData(self):
        #first resolve an EEG stream on the lab network
        print("looking for an EEG stream...")
        streams = resolve_stream('type', 'EEG')

        # create a new inlet to read from the stream
        inlet = StreamInlet(streams[0])

        self.sample, self.timestamp = inlet.pull_sample()
        self.buffer.pop(0)
        self.buffer.append(self.sample[0])
        print(self.sample[0])

app = wx.App()
frame = wx.Frame( None, size=(500,500) )
panel = myWxPlot( frame )
frame.Show()
app.MainLoop()