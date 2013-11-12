import wx
import wx.calendar

import os

import datetime

from Model import CalendarModel
from CalendarView import CalendarView
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
		self.makeMenu()
		self.makeView()
		self.model.add(today(), today(), "test", 2)
		self.model.add(today(), today(), "test", 3)
		self.model.add(today(), today(), "test", 1)
		self.updateView()

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
		self.bigsplit = wx.SplitterWindow(self)
		self.calendarView = CalendarView(self.bigsplit, self.model)
		self.littlesplit = wx.SplitterWindow(self.bigsplit)
		self.availableTasks = BasicViews.TaskViewer(self.littlesplit, self.model.getAvailableTasks(today()), "Available tasks")
		self.allTasks = BasicViews.TaskViewer(self.littlesplit, self.model.getAllTasks(), "All tasks")
		self.littlesplit.SplitVertically(self.availableTasks, self.allTasks)
		self.bigsplit.SplitVertically(self.littlesplit, self.calendarView)
		self.bigsplit.Show()

	def addTaskEvent(self, event):
		BasicViews.TaskDetails(self.model.add(today(), today(), "", 0)).Show()
		self.updateView()

	def saveEvent(self, event):
		filedialog = wx.FileDialog(self)
		if filedialog.ShowModal() == wx.ID_OK:
			self.model.save(os.path.join(filedialog.GetDirectory(), filedialog.GetFilename()))
		filedialog.Destroy()
	def loadEvent(self, event):
		filedialog = wx.FileDialog(self)
		if filedialog.ShowModal() == wx.ID_OK:
			self.model = CalendarModel.load(os.path.join(filedialog.GetDirectory(), filedialog.GetFilename()))
		filedialog.Destroy()
		self.updateView()

	def closeEvent(self, event):
		self.Close()

	def updateView(self):
		print "update view"
		self.calendarView.updateModel(self.model)
		self.availableTasks.update(self.model.getAvailableTasks(today()), "Available tasks")
		self.allTasks.update(self.model.getAllTasks(), "All tasks")


class CalendarApp(wx.App):

    def OnInit(self):
        frame = MainFrame(None, "Calendar app")
        Globals.mainWindow = frame
        frame.Show(True)
        self.SetTopWindow(frame)
        return True


app = CalendarApp(0)
app.MainLoop()