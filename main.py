import json
from datetime import date, time, datetime
import myUtils
import os
import inspect

# just for data structure reference
# template = {
# 	'categories': {
# 		'food': {
# 			'burger': {
# 				'Amount': 12,
# 				'Date': '10/12/25'
# 			}
# 		}
# 	}
# }

# vars

currentFilePath = os.path.join(os.path.abspath(__file__), 'reports')
currentDir = os.path.dirname(currentFilePath)
parentDir = os.path.dirname(currentDir)
expenseFilesDir = os.path.join(parentDir, 'reports')

commandsDict = {

}

validAgrees = ['y', 'yes']

# functions

def saveToFile(file, data):
	with open(file, mode='w', encoding='utf-8') as f:
		json.dump(data, f, indent=2)

def loadFromFile(file):
	with open(file, mode='r', encoding='utf-8') as f:
		data = json.load(f)
		return data

def funcErrorOutput(errortype, rawError):
	print(f'{inspect.currentframe().f_back.f_code.co_name} {errortype} when attempting to convert expenseVal to float. \n Raw error: \n {rawError}')


# commands

# global command settings

maxRetries = 2

def addExpense(file):
	
	#args
	expenseName = input('Name of expense: ')
	expenseCat = input('Category of expense: ')
	expenseVal = input('Cost of expense: ')
	if input('Would you like to add a date? \n') in validAgrees:
		expenseDate = input('Date of expense: ')
	else:
		currDate = datetime.now()
		expenseDate = f'{currDate.month}/{currDate.day}/{currDate.year}'
	# add value checks and error catching

	# formatting
	try:
		expenseVal = float(expenseVal)
	except TypeError as te:
		funcErrorOutput('TypeError', te)

	dataFromFile = loadFromFile(file)
	print(f'datafromfile:{dataFromFile}')
	# value checking/invalid input handling
	timesChecked = 0

	def checkExpensePresense(): # make more universal
		nonlocal expenseName
		nonlocal expenseCat
		nonlocal expenseVal
		nonlocal expenseDate
		nonlocal timesChecked
		if timesChecked >= maxRetries:
			print('You have reached the maximum number of allowed retries.')
			return
		
		timesChecked += 1
		if expenseCat in dataFromFile['categories']:
			if expenseName in dataFromFile['categories'][expenseCat].keys():
				if expenseDate in dataFromFile['categories'][expenseCat][expenseName].values():
					change = input(f'The expense you are trying to log ({expenseName}) has already been logged, would you like to change the name? \n')
					if change in validAgrees:
						expenseName = input('Name of expense: ')
						checkExpensePresense()
					else:
						print('Aborting command.')
						return
	checkExpensePresense()

	dataFromFile['categories'][expenseCat][expenseName] = {'Amount' : expenseVal, 'Date': expenseDate}
	saveToFile(file, dataFromFile)
	print('Expense added to file.')

def removeExpense(file):
	expenseName = input('Name of expense: ')
	expenseCat = input('Category of expense: ')
	cOrD = input('Cost or date of expense: ')
	expenseVal = None
	expenseDate = None

	if '/' in cOrD: # cost or date determining
		expenseDate = cOrD
	elif '/' not in cOrD:
		expenseVal = cOrD
		try:
			expenseVal = float(expenseVal)
		except ValueError as ve:
			funcErrorOutput('ValueError', ve)

	dataFromFile = loadFromFile(file)

	# input validation
	timesChecked = 0

	def checkExpensePresense(): # make more universal
		nonlocal expenseName
		nonlocal expenseCat
		nonlocal expenseVal
		nonlocal expenseDate
		nonlocal timesChecked
		if timesChecked >= maxRetries:
			print('You have reached the maximum number of allowed retries.')
			return
		
		timesChecked += 1
		if expenseCat in dataFromFile['categories']:
			if expenseName in dataFromFile['categories'][expenseCat].keys():
				if expenseDate not in dataFromFile['categories'][expenseCat][expenseName].values():
					change = input(f'The expense you are trying to remove ({expenseName}) has not been found, would you like to change the name? \n')
					if change in validAgrees:
						expenseName = input('Name of expense: ')
						checkExpensePresense()
					else:
						print('Aborting command.')
						return
	checkExpensePresense()

	# find and remove expense
	try:
		expense = dataFromFile['categories'][expenseCat][expenseName]
		if expense != None:
			if expenseDate != None:
				if expense['Date']
	except Exception as e:
		funcErrorOutput('General exception', e)


# testing
#os.path.join(expenseFilesDir, 'test.json')
removeExpense(os.path.join(expenseFilesDir, 'test.json'))

# main