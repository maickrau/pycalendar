import pickle

class CalendarModel(object):
	def __init__(self):
		self.tasks = []

	def add(self, startDate, endDate, name, priority=1):
		newTask = Task(startDate, endDate, name, priority)
		self.tasks.append(newTask)
		return newTask

	def removeTask(self, task):
		del self.tasks[self.tasks.index(task)]

	def updateTask(self, task, name, startDate, endDate, priority):
		print "task update model"
		task.name = name
		task.startDate = startDate
		task.endDate = endDate
		task.priority = priority

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

	def save(self, filename):
		with open(filename, 'w') as f:
			pickle.dump(self, f)

	@staticmethod
	def load(filename):
		with open(filename, 'r') as f:
			found = pickle.load(f)
		return found

class Task(object):
	def __init__(self, startDate, endDate, name, priority=1):
		self.startDate = startDate
		self.endDate = endDate
		self.name = name
		self.priority = priority

