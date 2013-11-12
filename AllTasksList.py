import wx
import Globals

import BasicViews

class AllTasksList(wx.BoxSizer):
	def __init__(self, parent, model):
		super(AllTasksList, self).__init__(orient=wx.VERTICAL)
		self.taskList = BasicViews.TaskViewer(parent, model.getAllTasks(), "")
		text = wx.StaticText(parent, label="All tasks")

		buttons = wx.BoxSizer(orient=wx.HORIZONTAL)
		add = wx.Button(parent, label="new task")
		startDate = wx.Button(parent, label="start date")
		endDate = wx.Button(parent, label="end date")
		priority = wx.Button(parent, label="priority")
#		urgency = wx.Button(self, label="urgency")
		add.Bind(wx.EVT_BUTTON, self.addTask)
		startDate.Bind(wx.EVT_BUTTON, self.sortByStartDate)
		endDate.Bind(wx.EVT_BUTTON, self.sortByEndDate)
		priority.Bind(wx.EVT_BUTTON, self.sortByPriority)
#		urgency.Bind(wx.EVT_BUTTON, self.sortByUrgency)
		buttons.Add(add)
		buttons.Add(startDate)
		buttons.Add(endDate)
		buttons.Add(priority)
#		buttons.Add(urgency)

		self.Add(text)
		self.Add(buttons)
		self.Add(self.taskList)

	def addTask(self, event):
		Globals.addTaskFunc()
	def sortByStartDate(self, event):
		self.taskList.sorter = lambda task: task.startDate
		Globals.updateViewFunc()
	def sortByEndDate(self, event):
		self.taskList.sorter = lambda task: task.endDate
		Globals.updateViewFunc()
	def sortByPriority(self, event):
		self.taskList.sorter = lambda task: -task.priority
		Globals.updateViewFunc()
	def sortByUrgency(self, event):
		self.taskList.sorter = lambda task: -task.urgency()
		Globals.updateViewFunc()
	def update(self, model):
		self.taskList.update(model.getAllTasks())
