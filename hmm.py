import wx
import wx.calendar

import os
import sys

import datetime

from Model import CalendarModel
from CalendarView import CalendarView
from AllTasksList import AllTasksList
import BasicViews

import Globals

def today():
	times = datetime.datetime.now()
	return str(times.year)+"-"+str(times.month)+"-"+str(times.day)

class MainFrame(wx.Frame):
	def __init__(self, parent, title):
		super(MainFrame, self).__init__(parent, title=title)

		self.model = CalendarModel()
		Globals.updateTaskFunc = self.updateTask
		Globals.removeTaskFunc = self.removeTask
		Globals.addTaskFunc = self.addTask
		Globals.updateViewFunc = self.updateView
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
		newtask = menu.Append(-1, text="&New task", help="New task")
		save = menu.Append(-1, text="&Save", help="Save to file")
		load = menu.Append(-1, text="&Load", help="Load from file")
		exit = menu.Append(wx.ID_EXIT, text="E&xit", help="Exit program")
		self.Bind(wx.EVT_MENU, self.addTaskEvent, newtask)
		self.Bind(wx.EVT_MENU, self.saveEvent, save)
		self.Bind(wx.EVT_MENU, self.loadEvent, load)
		self.Bind(wx.EVT_MENU, self.closeEvent, exit)
		menubar.Append(menu, "&File")
		self.SetMenuBar(menubar)

	def removeTask(self, task):
		self.model.removeTask(task)
		self.updateView()

	def updateTask(self, task, name, startDate, endDate, priority):
		print "task update hmm"
		self.model.updateTask(task, name, startDate, endDate, priority)
		self.updateView()

	def makeView(self):
		self.panel = wx.Panel(self)
		self.box = wx.BoxSizer(orient=wx.HORIZONTAL)
		self.calendarView = CalendarView(self.panel, self.model)
		self.availableTasks = BasicViews.TaskViewer(self.panel, self.model.getAvailableTasks(today()), "Available tasks")
		self.allTasks = AllTasksList(self.panel, self.model)
		self.box.Add(self.availableTasks)
		self.box.Add(self.allTasks)
		self.box.Add(self.calendarView)
		self.updateView()

	def addTaskEvent(self, event):
		self.addTask()

	def addTask(self):
		BasicViews.TaskDetails(self.model.add(today(), today(), "", 0)).Show()
		self.updateView()

	def saveEvent(self, event):
		filedialog = wx.FileDialog(self)
		if filedialog.ShowModal() == wx.ID_OK:
			self.saveToFile(os.path.join(filedialog.GetDirectory(), filedialog.GetFilename()))
		filedialog.Destroy()
	def loadEvent(self, event):
		filedialog = wx.FileDialog(self)
		if filedialog.ShowModal() == wx.ID_OK:
			self.loadFromFile(os.path.join(filedialog.GetDirectory(), filedialog.GetFilename()))
		filedialog.Destroy()
	def saveToFile(self, fileName):
		print "save", fileName
		self.model.save(fileName)
	def loadFromFile(self, fileName):
		print "load", fileName
		self.model = CalendarModel.load(fileName)
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
		print "update view"
		self.calendarView.updateModel(self.model)
		self.availableTasks.update(self.model.getAvailableTasks(today()))
		self.allTasks.update(self.model)
		self.panel.SetSizerAndFit(self.box)
		self.panel.Layout()
		self.panel.Fit()
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