import pickle

import datetime

def daysSinceToday(ISO):
	today = datetime.datetime.now().date()
	otherDate = datetime.datetime.strptime(ISO, '%Y-%m-%d').date()
	difference = (otherDate-today).days
	return difference

def ISOtodate(ISO):
	splitted = ISO.split('-')
	year = splitted[0]
	month = splitted[1]
	day = splitted[2]
	return datetime.date(year, month, day)

def dayPlus(ISO, days):
	return (ISOtodate(ISO)+datetime.timedelta(days)).isoformat()

def weekly(last):
	return dayPlus(last, 7)

class CalendarModel(object):
	def __init__(self):
		self.taskContainer = TaskContainer()

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
		return found

class TaskContainer(object):
	def __init__(self):
		self.tasks = []
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
		self.taskIteration = 0
		self.nextRepeat = firstRepeat
	def calcNextGen(self):
		self.nextRepeat = self.repeatCondition(self.nextRepeat)
	def genTask(self, currentDate):
		if currentDate != nextRepeat:
			return None
		self.taskIteration += 1
		startDate = currentDate
		endDate = dayPlus(currentDate, taskLength)
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
