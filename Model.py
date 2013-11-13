import pickle

import datetime

def daysSinceToday(ISO):
	today = datetime.datetime.now().date()
	otherDate = datetime.datetime.strptime(ISO, '%Y-%m-%d').date()
	difference = (otherDate-today).days
	return difference

def ISOtodate(ISO):
	splitted = ISO.split('-')
	year = int(splitted[0])
	month = int(splitted[1])
	day = int(splitted[2])
	return datetime.date(year, month, day)

def dayPlus(ISO, days):
	return (ISOtodate(ISO)+datetime.timedelta(days)).isoformat()

def weekly(last):
	return dayPlus(last, 7)

def monthly(last):
	date = ISOtodate(last)
	newMonth = date.month+1
	newYear = date.year
	if newMonth > 12:
		newMonth -= 12
		newYear += 1
	newDate = date.date(newYear, newMonth, date.day)
	return newDate.isoformat()

def repeatName(func):
	if func is weekly:
		return "Weekly"
	if func is monthly:
		return "Monthly"
	return "Unknown repetition type"

def repeatFunc(name):
	if name == "Weekly":
		return weekly
	if name == "Monthly":
		return monthly
	return lambda iso: dayPlus(iso, 1)

repeatNames = ["Weekly", "Monthly"]

class CalendarModel(object):
	def __init__(self):
		self.taskContainer = TaskContainer()
		self.repeatTaskContainer = RepeatTaskContainer()
		self.lastDayDone = datetime.date.today().isoformat()

	def getAllRepeats(self):
		return self.repeatTaskContainer.getAllRepeats()

	def addRepeat(self, name, firstRepeat, repeatCondition, taskLength, taskName, taskPriority=1):
		return self.repeatTaskContainer.add(name, firstRepeat, repeatCondition, taskLength, taskName, taskPriority)

	def updateRepeat(self, repeat, name, firstRepeat, repeatCondition, taskLength, taskName, taskPriority, description, taskDescription):
		self.repeatTaskContainer.updateRepeat(repeat, name, firstRepeat, repeatCondition, taskLength, taskName, taskPriority, description, taskDescription)

	def removeRepeat(self, repeat):
		self.repeatTaskContainer.removeRepeat(repeat)

	def newDay(self, date):
		if ISOtodate(self.lastDayDone) >= ISOtodate(date):
			return
		start = ISOtodate(self.lastDayDone)
		end = ISOtodate(date)
		days = (end-start).days+1
		#lastDayDone aka start has already been done
		for n in range(1, days):
			day = start+datetime.timedelta(n)
			self.doDay(day.isoformat())
		self.lastDayDone = date

	def doDay(self, day):
		print "doing day", day
		newTasks = self.repeatTaskContainer.getNewTasks(day)
		self.taskContainer.addBatch(newTasks)

	def add(self, startDate, endDate, name, priority=1):
		return self.taskContainer.add(startDate, endDate, name, priority)

	def removeTask(self, task):
		self.taskContainer.removeTask(task)

	def updateTask(self, task, name, startDate, endDate, priority, description):
		self.taskContainer.updateTask(task, name, startDate, endDate, priority, description)

	def getAllTasks(self):
		return self.taskContainer.getAllTasks()

	def getTasksExactEndDay(self, date):
		return self.taskContainer.getTasksExactEndDay(date)

	def getAvailableTasks(self, date):
		return self.taskContainer.getAvailableTasks(date)

	def getTasksEndBetween(self, startDate, endDate):
		return self.taskContainer.getTasksEndBetween(startDate, endDate)

	def getTasksPriority(self, priority):
		return self.taskContainer.getTasksPriority(priority)

	def save(self, filename):
		with open(filename, 'w') as f:
			pickle.dump(self, f)

	@staticmethod
	def load(filename):
		with open(filename, 'r') as f:
			found = pickle.load(f)
		if not hasattr(found, 'taskContainer'):
			found.taskContainer = TaskContainer()
		if not hasattr(found, 'repeatTaskContainer'):
			found.repeatTaskContainer = RepeatTaskContainer()
		if not hasattr(found, 'lastDayDone'):
			found.lastDayDone = "2013-11-11" #OOPS! this will cause bugs in the future
		return found

class RepeatTaskContainer(object):
	def __init__(self):
		self.repeats = []

	def getAllRepeats(self):
		return self.repeats

	def add(self, name, nextRepeat, repeatCondition, taskLength, taskName, taskPriority=1):
		newRepeat = RepeatTask(name, nextRepeat, repeatCondition, taskLength, taskName, taskPriority)
		self.repeats.append(newRepeat)
		return newRepeat

	def updateRepeat(self, repeat, name, nextRepeat, repeatCondition, taskLength, taskName, taskPriority, description, taskDescription):
		repeat.name = name
		repeat.nextRepeat = nextRepeat
		repeat.repeatCondition = repeatCondition
		repeat.taskLength = taskLength
		repeat.taskName = taskName
		repeat.taskPriority = taskPriority
		repeat.description = description
		repeat.taskDescription = taskDescription

	def removeRepeat(self, repeat):
		del self.repeats[self.repeats.index(repeat)]

	def getNewTasks(self, date):
		newTasks = []
		for r in self.repeats:
			newTask = r.genTask(date)
			if newTask is not None:
				newTasks.append(newTask)
		return newTasks

class TaskContainer(object):
	def __init__(self):
		self.tasks = []

	def addBatch(self, tasks):
		self.tasks += tasks

	def add(self, startDate, endDate, name, priority):
		newTask = Task(startDate, endDate, name, priority)
		self.tasks.append(newTask)
		return newTask

	def updateTask(self, task, name, startDate, endDate, priority, description):
		task.name = name
		task.startDate = startDate
		task.endDate = endDate
		task.priority = priority
		task.description = description

	def removeTask(self, task):
		del self.tasks[self.tasks.index(task)]

	def getAllTasks(self):
		return self.tasks

	def getTasksExactEndDay(self, date):
		ret = []
		for e in self.tasks:
			if e.endDate == date:
				ret.append(e)
		return ret

	def getAvailableTasks(self, date):
		ret = []
		for e in self.tasks:
			if e.startDate <= date and date <= e.endDate:
				ret.append(e)
		return ret

	def getTasksEndBetween(self, startDate, endDate):
		ret = []
		for e in self.tasks:
			if startDate <= e.endDate and e.endDate <= endDate:
				ret.append(e)
		return ret

	def getTasksPriority(self, priority):
		ret = []
		for e in self.tasks:
			if e.priority >= priority:
				ret.append(e)
		return ret

class RepeatTask(object):
	def __init__(self, name, firstRepeat, repeatCondition, taskLength, taskName, taskPriority=1):
		self.name = name
		self.repeatCondition = repeatCondition
		self.taskLength = taskLength
		self.taskPriority = taskPriority
		self.taskName = taskName
		self.nextRepeat = firstRepeat
		self.description = ""
		self.taskDescription = ""
		self.taskIteration = 0
	def calcNextGen(self):
		self.nextRepeat = self.repeatCondition(self.nextRepeat)
	def genTask(self, currentDate):
		if currentDate != self.nextRepeat:
			return None
		self.taskIteration += 1
		startDate = currentDate
		endDate = dayPlus(currentDate, self.taskLength)
		name = self.taskName+str(self.taskIteration)
		priority = self.taskPriority
		self.calcNextGen()
		return Task(startDate, endDate, name, priority)


class Task(object):
	def __init__(self, startDate, endDate, name, priority=1):
		self.startDate = startDate
		self.endDate = endDate
		self.name = name
		self.priority = priority
		self.description = ""

	def urgency(self):
		days = daysSinceToday(self.endDate)
		if (days > 0):
			result = float(self.priority)/days
		else:
			result = float(self.priority)
		return result
