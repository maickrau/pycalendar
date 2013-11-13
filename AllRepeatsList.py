import wx
import Globals

import BasicViews

class AllRepeatsList(wx.BoxSizer):
	def __init__(self, parent, model):
		super(AllRepeatsList, self).__init__(orient=wx.VERTICAL)
		self.repeatList = BasicViews.RepeatViewer(parent, model.getAllRepeats(), "")
		text = wx.StaticText(parent, label="All repeats")

		buttons = wx.BoxSizer(orient=wx.HORIZONTAL)
		add = wx.Button(parent, label="new repeat")
		repeatType = wx.StaticText(parent, label="repeat type")
		nextRepeat = wx.StaticText(parent, label="next repeat")
		add.Bind(wx.EVT_BUTTON, self.addRepeat)
		buttons.Add(add)
		buttons.Add(repeatType)
		buttons.Add(nextRepeat)

		self.Add(text)
		self.Add(buttons)
		self.Add(self.repeatList)

	def addRepeat(self, event):
		Globals.addRepeatFunc()
	def update(self, model):
		self.repeatList.update(model.getAllRepeats())
