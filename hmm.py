import wx
import wx.calendar

import os

import pickle

class CalendarModel(object):
	def __init__(self):
		self.dayManager = DayManager()
	def save(self, filename):
		with open(filename, 'w') as f:
			pickle.dump(self, f)
	@staticmethod
	def load(filename):
		with open(filename, 'r') as f:
			found = pickle.load(f)
		return found

class Task(object):
	def __init__(self, date, name):
		self.date = date
		self.name = name

class DayManager(object):
	def __init__(self):
		self.events = []
	def add(self, date, name):
		self.events.append(Task(date, name))

class CalendarContainer(wx.Panel):
	def __init__(self, parent, dayChangeCallback):
		super(CalendarContainer, self).__init__(parent)
		self.box = wx.BoxSizer()
		self.calendar = wx.calendar.CalendarCtrl(self, style=wx.calendar.CAL_MONDAY_FIRST)
		self.calendar.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, dayChangeCallback)
		self.box.Add(self.calendar)
		self.SetSizerAndFit(self.box)
	def getDate(self):
		return self.calendar.GetDate().FormatISODate()

class TaskList(wx.Panel):
	def __init__(self, parent, addCallback):
		super(TaskList, self).__init__(parent)
		self.box = wx.BoxSizer(orient=wx.VERTICAL)
		self.taskField = []
		self.addButton = wx.Button(self, label="add")
		self.addButton.Bind(wx.EVT_BUTTON, addCallback)
	def update(self, model, date):
		self.addButton.Hide()
		self.unmake()
		self.box.Clear()
		self.taskField = []
		for e in model.dayManager.events:
			if date == e.date:
				newThing = TaskField(e, self)
				self.taskField.append(newThing)
				self.box.Add(newThing)
		self.box.Add(self.addButton)
		self.addButton.Show()
		self.SetSizerAndFit(self.box)
	def unmake(self):
		for f in self.taskField:
			f.unmake()

class TaskField(wx.BoxSizer):
	def __init__(self, thing, parent):
		super(TaskField, self).__init__(orient=wx.HORIZONTAL)
		self.thing = thing
		self.nameField = wx.TextCtrl(parent, value=self.thing.name)
		self.nameField.Bind(wx.EVT_TEXT, self.changeName)
		self.infoButton = wx.Button(parent, label="details")
		self.infoButton.Bind(wx.EVT_BUTTON, self.giveDetails)
		self.Add(self.nameField)
		self.Add(self.infoButton)
	def changeName(self, event):
		self.thing.name = event.GetEventObject().GetLineText(0)
	def giveDetails(self, event):
		print "details about stuff"
	def unmake(self):
		self.nameField.Destroy()
		self.infoButton.Destroy()

class MainFrame(wx.Frame):
	def __init__(self, parent, title):
		super(MainFrame, self).__init__(parent, title=title)

		self.model = CalendarModel()
		self.makeMenu()
		self.makeView()

	def makeMenu(self):
		menubar = wx.MenuBar()
		menu = wx.Menu()
		save = menu.Append(-1, text="&Save", help="Save to file")
		load = menu.Append(-1, text="&Load", help="Load from file")
		exit = menu.Append(wx.ID_EXIT, "E&xit", "Exit program")
		self.Bind(wx.EVT_MENU, self.save, save)
		self.Bind(wx.EVT_MENU, self.load, load)
		self.Bind(wx.EVT_MENU, self.close, exit)
		menubar.Append(menu, "&File")
		self.SetMenuBar(menubar)

	def makeView(self):
		self.splitter = wx.SplitterWindow(self)
		self.calendar = CalendarContainer(self.splitter, self.dayChanged)
		self.thinglist = TaskList(self.splitter, self.addButtonPressed)
		self.splitter.SplitHorizontally(self.calendar, self.thinglist)

		self.updateView()

	def save(self, event):
		filedialog = wx.FileDialog(self)
		if filedialog.ShowModal() == wx.ID_OK:
			self.model.save(os.path.join(filedialog.GetDirectory(), filedialog.GetFilename()))
		filedialog.Destroy()
	def load(self, event):
		filedialog = wx.FileDialog(self)
		if filedialog.ShowModal() == wx.ID_OK:
			self.model = CalendarModel.load(os.path.join(filedialog.GetDirectory(), filedialog.GetFilename()))
		filedialog.Destroy()
		self.updateView()
	def close(self, event):
		self.Close()

	def addButtonPressed(self, event):
		self.model.dayManager.add(self.calendar.getDate(), "test")
		self.updateView()

	def dayChanged(self, event):
		self.updateView()

	def updateView(self):
		self.thinglist.update(self.model, self.calendar.getDate())

		if not self.splitter.IsSplit():
			self.splitter.SplitHorizontally(self.calendar, self.thinglist)


class CalendarApp(wx.App):

    def OnInit(self):
        frame = MainFrame(None, "Calendar app")
        frame.Show(True)
        self.SetTopWindow(frame)
        return True


app = CalendarApp(0)
app.MainLoop()