import wx
import wx.calendar

import Model
import Globals

def dateTimeFromISO(ISO):
	parts = ISO.split('-')
	ret = wx.DateTime()
	ret.Set(int(parts[2]), int(parts[1])-1, int(parts[0]), 0, 0, 0, 0)
	#day 1..30, month 0..11?? widget :(
	return ret

class KeyValuesViewer(wx.Panel):
	def __init__(self, parent, text, keys, keyNameFunc, detailsFunc, valueFuncs, sorter=lambda key: 0):
		super(KeyValuesViewer, self).__init__(parent)
		self.box = wx.BoxSizer(orient=wx.VERTICAL)
		self.infoText = wx.StaticText(self, label=text)
		self.valueFuncs = valueFuncs
		self.detailsFunc = detailsFunc
		self.keyNameFunc = keyNameFunc
		self.sorter = sorter
		self.box.Add(self.infoText)
		self.updateKeys(keys)
		self.SetSizerAndFit(self.box)
	def update(self, keys, text=None, sorter=None):
		self.infoText.Hide()
		self.unmake()
		self.box.Clear()
		self.box = wx.BoxSizer(orient=wx.VERTICAL)
		if sorter is not None:
			self.sorter = sorter
		if text is not None:
			self.infoText.SetLabel(text)
		self.box.Add(self.infoText)
		self.updateKeys(keys)
		self.infoText.Show()
		self.SetSizerAndFit(self.box)
		self.Layout()
	def updateKeys(self, keys):
		self.keys = []
		for e in sorted(keys, key=self.sorter):
			newKey = KeyValuesField(self, e, self.keyNameFunc, self.detailsFunc, self.valueFuncs)
			self.keys.append(newKey)
			self.box.Add(newKey)
	def unmake(self):
		for f in self.keys:
			f.unmake()

class KeyValuesField(wx.GridSizer):
	def __init__(self, parent, key, keyNameFunc, detailsFunc, valueFuncs):
		size = len(valueFuncs)+1
		super(KeyValuesField, self).__init__(1, size, 5, 5)
		self.keyButton = wx.Button(parent, label=keyNameFunc(key))
		self.detailsFunc = detailsFunc
		self.key = key
		self.keyButton.Bind(wx.EVT_BUTTON, self.giveDetails)
		self.Add(self.keyButton)
		self.values = []
		for f in valueFuncs:
			newField = wx.StaticText(parent, label=f(key))
			self.values.append(newField)
			self.Add(newField)
	def giveDetails(self, event):
		self.detailsFunc(self.key)
	def unmake(self):
		self.keyButton.Destroy()
		for i in self.values:
			i.Destroy()
		self.values = []

class RepeatViewer(wx.Panel):
	def __init__(self, parent, repeats, text, showRepeat=True, showNext=True, sorter=lambda repeat: repeat.nextRepeat):
		super(RepeatViewer, self).__init__(parent)
		keyNameFunc = lambda repeat: repeat.name
		self.sorter = sorter
		valueFuncs = []
		if showRepeat:
			valueFuncs.append(lambda repeat: Model.repeatName(repeat.repeatCondition))
		if showNext:
			valueFuncs.append(lambda repeat: repeat.nextRepeat)

		self.keyValues = KeyValuesViewer(self, text, repeats, keyNameFunc, self.showRepeat, valueFuncs, self.sorter)

	def showRepeat(self, repeat):
		RepeatDetails(repeat).Show()

	def update(self, repeats, text=None):
		self.keyValues.update(repeats, text, self.sorter)
		self.Layout()

class TaskViewer(wx.Panel):
	def __init__(self, parent, tasks, text, showStartDate=True, showEndDate=True, showPriority=False, showUrgency=False, sorter=lambda task: task.endDate):
		super(TaskViewer, self).__init__(parent)
		keyNameFunc = lambda task: task.name
		self.sorter = sorter
		valueFuncs = []
		if showStartDate:
			valueFuncs.append(lambda task: task.startDate)
		if showEndDate:
			valueFuncs.append(lambda task: task.endDate)
		if showPriority:
			valueFuncs.append(lambda task: str(task.priority))
		if showUrgency:
			valueFuncs.append(lambda task: "%2f" % task.urgency())

		self.keyValues = KeyValuesViewer(self, text, tasks, keyNameFunc, self.showTask, valueFuncs, self.sorter)

	def showTask(self, task):
		TaskDetails(task).Show()

	def update(self, tasks, text=None):
		self.keyValues.update(tasks, text, self.sorter)
		self.Layout()

class RepeatDetails(wx.Frame):
	def __init__(self, repeat):
		super(RepeatDetails, self).__init__(Globals.mainWindow)
		panel = wx.Panel(self)
		self.repeat = repeat
		self.box = wx.FlexGridSizer(0, 2)
		self.box.SetFlexibleDirection(wx.VERTICAL)
		nameLabel = wx.StaticText(panel, label="name")
		self.nameField = wx.TextCtrl(panel, value=repeat.name)
		nextRepeatDate = dateTimeFromISO(repeat.nextRepeat)
		nextRepeatLabel = wx.StaticText(panel, label="next repetition")
		self.nextRepeatField = wx.calendar.CalendarCtrl(panel, date=nextRepeatDate, style=wx.calendar.CAL_MONDAY_FIRST)
		repeatLabel = wx.StaticText(panel, label="repeats")
		self.repeatBox = wx.ComboBox(panel, value=Model.repeatName(repeat.repeatCondition), choices=Model.repeatNames, style=wx.CB_DROPDOWN|wx.CB_READONLY)
		taskNameLabel = wx.StaticText(panel, label="task name")
		self.taskNameField = wx.TextCtrl(panel, value=repeat.taskName)
		taskLengthLabel = wx.StaticText(panel, label="task length")
		self.taskLengthField = wx.TextCtrl(panel, value=str(repeat.taskLength))
		priorityLabel = wx.StaticText(panel, label="task priority")
		self.priorityField = wx.TextCtrl(panel, value=str(repeat.taskPriority))
		descriptionLabel = wx.StaticText(panel, label="repeat description")
		desc = repeat.description
		self.descriptionField = wx.TextCtrl(panel, value=desc, style=wx.TE_MULTILINE)
		taskDescriptionLabel = wx.StaticText(panel, label="task description")
		taskDesc = repeat.taskDescription
		self.taskDescriptionField = wx.TextCtrl(panel, value=taskDesc, style=wx.TE_MULTILINE)
		saveButton = wx.Button(panel, label="save")
		saveButton.Bind(wx.EVT_BUTTON, self.saveEvent)
		deleteButton = wx.Button(panel, label="delete")
		deleteButton.Bind(wx.EVT_BUTTON, self.deleteEvent)
		self.box.Add(nameLabel)
		self.box.Add(self.nameField)
		self.box.Add(nextRepeatLabel)
		self.box.Add(self.nextRepeatField)
		self.box.Add(repeatLabel)
		self.box.Add(self.repeatBox)
		self.box.Add(taskNameLabel)
		self.box.Add(self.taskNameField)
		self.box.Add(taskLengthLabel)
		self.box.Add(self.taskLengthField)
		self.box.Add(priorityLabel)
		self.box.Add(self.priorityField)
		self.box.Add(descriptionLabel)
		self.box.Add(self.descriptionField)
		self.box.Add(taskDescriptionLabel)
		self.box.Add(self.taskDescriptionField)
		self.box.Add(saveButton)
		self.box.Add(deleteButton)
		panel.SetSizerAndFit(self.box)
		self.Fit()

	def deleteEvent(self, event):
		Globals.removeRepeatFunc(self.repeat)
		self.Close()

	def saveEvent(self, event):
		name = self.nameField.GetValue()
		nextRepeat = self.nextRepeatField.GetDate().FormatISODate()
		repeat = Model.repeatFunc(self.repeatBox.GetValue())
		taskPriority = int(self.priorityField.GetValue())
		description = ""
		for i in range(0, self.descriptionField.GetNumberOfLines()):
			if i > 0:
				description += '\n'
			description += self.descriptionField.GetLineText(i)
		taskDescription = ""
		for i in range(0, self.taskDescriptionField.GetNumberOfLines()):
			if i > 0:
				taskDescription += '\n'
			taskDescription += self.taskDescriptionField.GetLineText(i)
		taskName = self.taskNameField.GetValue()
		taskLength = int(self.taskLengthField.GetValue())
		Globals.updateRepeatFunc(self.repeat, name, nextRepeat, repeat, taskLength, taskName, taskPriority, description, taskDescription)
		self.Close()

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
		descriptionLabel = wx.StaticText(panel, label="description")
		desc = ""
		if hasattr(thing, 'description'):
			desc = thing.description
		self.descriptionField = wx.TextCtrl(panel, value=desc, style=wx.TE_MULTILINE)
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
		self.box.Add(descriptionLabel)
		self.box.Add(self.descriptionField)
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
		description = ""
		for i in range(0, self.descriptionField.GetNumberOfLines()):
			if i > 0:
				description += '\n'
			description += self.descriptionField.GetLineText(i)
		Globals.updateTaskFunc(self.thing, name, start, end, priority, description)
		self.Close()

