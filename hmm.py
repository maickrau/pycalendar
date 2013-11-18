import wx
import wx.calendar

import os
import sys

import datetime

import Model
from CalendarView import CalendarView
from AllTasksList import AllTasksList
from AllRepeatsList import AllRepeatsList
import BasicViews

import Globals

def today():
	return datetime.date.today().isoformat()

class MainFrame(wx.Frame):
	def __init__(self, parent, title):
		super(MainFrame, self).__init__(parent, title=title)

		self.model = Model.CalendarModel()

		Globals.updateViewFunc = self.updateView

		Globals.updateTaskFunc = self.updateTask
		Globals.removeTaskFunc = self.removeTask
		Globals.addTaskFunc = self.addTask

		Globals.updateRepeatFunc = self.updateRepeat
		Globals.removeRepeatFunc = self.removeRepeat
		Globals.addRepeatFunc = self.addRepeat

		self.makeMenu()
		self.makeView()
		self.updateView()

		self.Bind(wx.EVT_CLOSE, self.closeEvent)

		if len(sys.argv) > 1:
			self.loadFromFile(sys.argv[1])
		self.Layout()

	def makeMenu(self):
		menubar = wx.MenuBar()
		menu = wx.Menu()
		save = menu.Append(-1, text="&Save", help="Save to file")
		load = menu.Append(-1, text="&Load", help="Load from file")
		exit = menu.Append(wx.ID_EXIT, text="E&xit", help="Exit program")
		self.Bind(wx.EVT_MENU, self.saveEvent, save)
		self.Bind(wx.EVT_MENU, self.loadEvent, load)
		self.Bind(wx.EVT_MENU, self.closeEvent, exit)
		menubar.Append(menu, "&File")

		self.SetMenuBar(menubar)

	def makeView(self):
		self.panel = wx.Panel(self)
		self.box = wx.BoxSizer(orient=wx.HORIZONTAL)
		self.calendarView = CalendarView(self.panel, self.model)
		self.availableTasks = BasicViews.TaskViewer(self.panel, self.model.getAvailableTasks(today()), "Available tasks", False, True)
		self.allTasks = AllTasksList(self.panel, self.model)
		self.allRepeats = AllRepeatsList(self.panel, self.model)
		self.box.Add(self.availableTasks)
		self.box.Add(self.allTasks)
		self.box.Add(self.calendarView)
		self.box.Add(self.allRepeats)
		self.updateView()

	def addTaskEvent(self, event):
		self.addTask()

	def addRepeatEvent(self, event):
		self.addRepeat()

	def showRepeatEvent(self, event):
		repeats = BasicViews.RepeatViewer(self, self.model.repeatTaskContainer.repeats, "All repeats")
		repeats.Show()

	def removeTask(self, task):
		self.model.removeTask(task)
		self.updateView()

	def updateTask(self, task, name, startDate, endDate, priority, description):
		self.model.updateTask(task, name, startDate, endDate, priority, description)
		self.updateView()

	def addTask(self):
		BasicViews.TaskDetails(self.model.add(today(), today(), "", 0)).Show()
		self.updateView()

	def removeRepeat(self, repeat):
		self.model.removeRepeat(repeat)
		self.updateView()

	def updateRepeat(self, repeat, name, firstRepeat, repeatCondition, taskLength, taskName, taskPriority, description, taskDescription):
		self.model.updateRepeat(repeat, name, firstRepeat, repeatCondition, taskLength, taskName, taskPriority, description, taskDescription)
		self.updateView()

	def addRepeat(self):
		BasicViews.RepeatDetails(self.model.addRepeat("", today(), Model.weekly, 7, "")).Show()
		self.updateView()

	def doToFile(self, function):
		filedialog = wx.FileDialog(self)
		if filedialog.ShowModal() == wx.ID_OK:
			function(os.path.join(filedialog.GetDirectory(), filedialog.GetFilename()))
		filedialog.Destroy()

	def saveEvent(self, event):
		self.doToFile(self.saveToFile)
	def loadEvent(self, event):
		self.doToFile(self.loadFromFile)
	def saveToFile(self, fileName):
		print "save", fileName
		self.model.save(fileName)
	def loadFromFile(self, fileName):
		print "load", fileName
		self.model = Model.CalendarModel.load(fileName)
		self.model.newDay(today())
		self.updateView()

	def close(self):
		print "close"
		if len(sys.argv) > 1:
			self.saveToFile(sys.argv[1])
		self.Destroy()

	def closeEvent(self, event):
		self.close()

	def refreshEvent(self, event):
		self.updateView()

	def updateView(self):
		self.calendarView.updateModel(self.model)
		self.availableTasks.update(self.model.getAvailableTasks(today()))
		self.allTasks.update(self.model)
		self.allRepeats.update(self.model)
		self.panel.SetSizerAndFit(self.box)
		self.panel.Layout()
		self.panel.Fit()
		self.panel.Refresh()
		self.Fit()


class CalendarApp(wx.App):

    def OnInit(self):
        frame = MainFrame(None, "Calendar app")
        Globals.mainWindow = frame
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

print sys.argv
app = CalendarApp(0)
app.MainLoop()