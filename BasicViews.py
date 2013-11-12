import wx
import wx.calendar

import Globals

def dateTimeFromISO(ISO):
	parts = ISO.split('-')
	ret = wx.DateTime()
	ret.Set(int(parts[2]), int(parts[1])-1, int(parts[0]), 0, 0, 0, 0)
	#day 1..30, month 0..11?? widget :(
	return ret

class TaskViewer(wx.Panel):
	def __init__(self, parent, tasks, text, showDates=True, showPriority=True, showUrgency=False, sorter=lambda task: -task.priority):
		super(TaskViewer, self).__init__(parent)
		self.sorter = sorter
		self.box = wx.BoxSizer(orient=wx.VERTICAL)
		self.infoText = wx.StaticText(self, label=text)
		self.showDates = showDates
		self.showPriority = showPriority
		self.showUrgency = showUrgency
		self.box.Add(self.infoText)
		self.updateTasks(tasks)
		self.SetSizerAndFit(self.box)

	def update(self, tasks, text=None):
		self.infoText.Hide()
		self.unmake(self.tasks)
		self.box.Clear()
		self.box = wx.BoxSizer(orient=wx.VERTICAL)
		if text is not None:
			self.infoText.SetLabel(text)
		self.box.Add(self.infoText)
		self.updateTasks(tasks)
		self.infoText.Show()
		self.SetSizerAndFit(self.box)
		self.Layout()
#		self.Fit()

	def updateTasks(self, tasks):
		self.tasks = []
		for e in sorted(tasks, key=self.sorter):
			newThing = TaskField(e, self, self.showDates, self.showPriority, self.showUrgency)
			self.tasks.append(newThing)
			self.box.Add(newThing)

	def unmake(self, keep):
		for f in self.tasks:
			f.unmake()

class TaskField(wx.GridSizer):
	def __init__(self, thing, parent, showDates=True, showPriority=True, showUrgency=True):
		size = 1
		if showDates:
			size += 2
		if showPriority:
			size += 1
		if showUrgency:
			size += 1
		super(TaskField, self).__init__(1, size, 5, 5)
		self.thing = thing
		self.infoButton = wx.Button(parent, label=self.thing.name)
		self.Add(self.infoButton)
		self.infoButton.Bind(wx.EVT_BUTTON, self.giveDetails)
		if showDates:
			self.startDate = wx.StaticText(parent, label=self.thing.startDate)
			self.endDate = wx.StaticText(parent, label=self.thing.endDate)
			self.Add(self.startDate)
			self.Add(self.endDate)
		if showPriority:
			self.priority = wx.StaticText(parent, label=str(self.thing.priority))
			self.Add(self.priority)
		if showUrgency:
			self.urgency = wx.StaticText(parent, label="%2f" % self.thing.urgency())
			self.Add(self.urgency)
	def giveDetails(self, event):
		details = TaskDetails(self.thing)
		details.Show()
	def unmake(self):
		self.infoButton.Destroy()
		if hasattr(self, 'startDate'):
			self.startDate.Destroy()
		if hasattr(self, 'endDate'):
			self.endDate.Destroy()
		if hasattr(self, 'priority'):
			self.priority.Destroy()
		if hasattr(self, 'urgency'):
			self.urgency.Destroy()

class TaskDetails(wx.Frame):
	def __init__(self, thing):
		super(TaskDetails, self).__init__(Globals.mainWindow)
		panel = wx.Panel(self)
		self.thing = thing
		self.box = wx.FlexGridSizer(0, 2)
		self.box.SetFlexibleDirection(wx.VERTICAL)
		nameLabel = wx.StaticText(panel, label="name")
		self.nameField = wx.TextCtrl(panel, value=thing.name)
		startDate = dateTimeFromISO(thing.startDate)
		startLabel = wx.StaticText(panel, label="start date")
		self.startField = wx.calendar.CalendarCtrl(panel, date=startDate, style=wx.calendar.CAL_MONDAY_FIRST)
		endDate = dateTimeFromISO(thing.endDate)
		endLabel = wx.StaticText(panel, label="end date")
		self.endField = wx.calendar.CalendarCtrl(panel, date=endDate, style=wx.calendar.CAL_MONDAY_FIRST)
		priorityLabel = wx.StaticText(panel, label="priority")
		self.priorityField = wx.TextCtrl(panel, value=str(thing.priority))
		saveButton = wx.Button(panel, label="save")
		saveButton.Bind(wx.EVT_BUTTON, self.saveEvent)
		deleteButton = wx.Button(panel, label="delete")
		deleteButton.Bind(wx.EVT_BUTTON, self.deleteEvent)
		self.box.Add(nameLabel)
		self.box.Add(self.nameField)
		self.box.Add(startLabel)
		self.box.Add(self.startField)
		self.box.Add(endLabel)
		self.box.Add(self.endField)
		self.box.Add(priorityLabel)
		self.box.Add(self.priorityField)
		self.box.Add(saveButton)
		self.box.Add(deleteButton)
		panel.SetSizerAndFit(self.box)
		self.Fit()

	def deleteEvent(self, event):
		Globals.removeTaskFunc(self.thing)
		self.Close()

	def saveEvent(self, event):
		name = self.nameField.GetValue()
		start = self.startField.GetDate().FormatISODate()
		end = self.endField.GetDate().FormatISODate()
		priority = int(self.priorityField.GetValue())
		Globals.updateTaskFunc(self.thing, name, start, end, priority)
		self.Close()

