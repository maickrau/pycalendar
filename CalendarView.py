import wx
import wx.calendar

from BasicViews import TaskViewer

import Globals

class CalendarContainer(wx.Panel):
	def __init__(self, parent, dayChangeCallback, model):
		super(CalendarContainer, self).__init__(parent)
		self.box = wx.BoxSizer(orient=wx.VERTICAL)
		self.calendar = wx.calendar.CalendarCtrl(self, style=wx.calendar.CAL_MONDAY_FIRST|wx.calendar.CAL_SHOW_HOLIDAYS)
		self.calendar.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, dayChangeCallback)
		self.calendar.Bind(wx.calendar.EVT_CALENDAR_MONTH, self.monthChanged)
		self.box.Add(self.calendar)
		self.SetSizerAndFit(self.box)
		self.updateModel(model)

	def updateModel(self, model):
		self.model = model
		self.highlightDeadlines()

	def highlightDeadlines(self):
		for i in range(1, self.calendar.GetDate().GetLastMonthDay().GetDay()+1):
			self.calendar.ResetAttr(i)
		for t in self.model.getAllTasks():
			if int(t.endDate.split('-')[1]) == self.calendar.GetDate().GetMonth()+1:
				self.calendar.SetHoliday(int(t.endDate.split('-')[2]))

	def monthChanged(self, event):
		self.highlightDeadlines()

	def getDate(self):
		return self.calendar.GetDate().FormatISODate()

class CalendarView(wx.SplitterWindow):
	def __init__(self, parent, model):
		super(CalendarView, self).__init__(parent)
		self.model = model
		self.calendar = CalendarContainer(self, self.selectDayEvent, model)
		self.tasks = TaskViewer(self, [], "Tasks on " + self.calendar.getDate(), False, False, False)
		self.SplitHorizontally(self.calendar, self.tasks)
		self.selectDay(self.calendar.getDate())

	def selectDayEvent(self, event):
		self.selectDay(self.calendar.getDate())
		Globals.updateViewFunc()

	def selectDay(self, date):
		if not self.IsSplit():
			self.SplitHorizontally(self.calendar, self.tasks)
		self.tasks.update(self.model.getTasksExactEndDay(date), "Tasks on " + self.calendar.getDate())

	def updateModel(self, model):
		self.model = model
		self.calendar.updateModel(model)
		self.selectDay(self.calendar.getDate())
		self.Layout()



