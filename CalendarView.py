import wx
import wx.calendar

from BasicViews import TaskViewer

import Globals

class CalendarContainer(wx.Panel):
	def __init__(self, parent, dayChangeCallback, model):
		super(CalendarContainer, self).__init__(parent)
		self.dayChangeCallback = dayChangeCallback
		self.box = wx.BoxSizer(orient=wx.VERTICAL)
		style = wx.calendar.CAL_MONDAY_FIRST|wx.calendar.CAL_SHOW_HOLIDAYS|wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION
		self.auxiliary = wx.calendar.CalendarCtrl(self, style=style)
		self.calendar = wx.calendar.CalendarCtrl(self, style=style)
		self.calendar.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.dayChanged)
		self.auxiliary.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.hideAuxiliarySelection)
		self.calendar.Bind(wx.calendar.EVT_CALENDAR_MONTH, self.monthChanged)
		self.box.Add(self.calendar)
		self.box.Add(self.auxiliary)
		self.SetSizerAndFit(self.box)
		self.fixAuxiliaryCalendar()
		self.updateModel(model)

	def hideAuxiliarySelection(self, event):
		day = self.auxiliary.GetDate().GetDay()
		fg = wx.Color(0, 0, 0, 0)
		bg = wx.Color(255, 255, 255, 0)
		attr = self.auxiliary.GetAttr(day)
		if attr is not None and attr.IsHoliday():
			fg = self.auxiliary.GetHolidayColourFg()
			bg = self.auxiliary.GetHolidayColourBg()
		self.auxiliary.SetHighlightColours(fg, bg)

	def fixAuxiliaryCalendar(self):
		newAuxiliaryDate = self.calendar.GetDate()
		newMonth = newAuxiliaryDate.GetMonth()+1
		newYear = newAuxiliaryDate.GetYear()
		newDay = 1
		if newMonth >= 12:
			newMonth -= 12
			newYear += 1
		newAuxiliaryDate.SetDay(newDay)
		newAuxiliaryDate.SetMonth(newMonth)
		newAuxiliaryDate.SetYear(newYear)
		self.auxiliary.SetDate(newAuxiliaryDate)
		self.hideAuxiliarySelection(None)

	def dayChanged(self, event):
		self.fixAuxiliaryCalendar()
		self.dayChangeCallback(event)

	def updateModel(self, model):
		self.model = model
		self.highlightDeadlines()
		self.fixAuxiliaryCalendar()

	def highlightDeadlinesOnCalendar(self, calendar):
		for i in range(1, calendar.GetDate().GetLastMonthDay().GetDay()+1):
			calendar.ResetAttr(i)
		for t in self.model.getAllTasks():
			if int(t.endDate.split('-')[1]) == calendar.GetDate().GetMonth()+1:
				calendar.SetHoliday(int(t.endDate.split('-')[2]))

	def highlightDeadlines(self):
		self.highlightDeadlinesOnCalendar(self.calendar)
		self.highlightDeadlinesOnCalendar(self.auxiliary)

	def monthChanged(self, event):
		self.highlightDeadlines()
		self.fixAuxiliaryCalendar()

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



