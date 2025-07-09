import json
from datetime import date, time, datetime
import myUtils
import os
import inspect
import traceback

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

def funcErrorOutput(errortype, rawError, comments='No comments provided'):
	tbList = traceback.extract_tb(rawError.__traceback__)
	fName, lineNum, funcName, text = tbList[-1]
	print('\n') # newline for clarity
	print(f'{inspect.currentframe().f_back.f_code.co_name} {errortype}\nPassed comments: {comments}\nLine: {lineNum}\nRaw error:\n{rawError}')


# commands

# global command settings

maxRetries = 2

def addExpense(file):
	
	stuffNotFound = [] # hold list of what wasn't correct so i can use a for loop and look super cool

	#args
	expenseName = input('Name of expense: ')
	expenseCat = input('Category of expense: ')
	expenseVal = input('Cost of expense: ')
	if input('Would you like to add a date? \n') in validAgrees:
		expenseDate = input('Date of expense: ')
	else:
		currDate = datetime.now()
		expenseDate = f'{currDate.month}/{currDate.day}/{currDate.year}'

	# formatting
	try:
		expenseVal = float(expenseVal)
	except ValueError as ve:
		funcErrorOutput('ValueError', ve)
		print('Aborting command due to error.')
		return

	dataFromFile = loadFromFile(file)
	print(f'datafromfile:{dataFromFile}')

	# invalid input error handling when i get around to it
	
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

	def checkExpensePresense(operation): # make more universal and reusable
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
				if expenseDate not in dataFromFile['categories'][expenseCat][expenseName]['Date']:
					change = input(f'The expense you are trying to {operation} ({expenseName}) could not be found with a matching date, would you like to change the date? y/n\n')
					if change in validAgrees:
						expenseDate = input('Date of expense: ')
						checkExpensePresense(operation)
					else:
						print('Aborting command.')
						return False
				elif expenseVal not in dataFromFile['categories'][expenseCat][expenseName]['Amount']:
					change = input(f'The expense you are trying to {operation} ({expenseName}) could not be found with a matching amount, would you like to change the amount? y/n\n')
					if change in validAgrees:
						expenseVal = input('Amount of expense: ')
						checkExpensePresense(operation)
					else:
						print('Aborting command.')
						return False
			elif expenseName not in dataFromFile['categories'][expenseCat].keys():
				change = input(f'The expense you are trying to {operation} ({expenseName}) has not been found by, would you like to change the name? y/n\n')
				if change in validAgrees:
					expenseName = input('Name of expense: ')
					checkExpensePresense(operation)
				else:
					print('Aborting command.')
					return False

	if checkExpensePresense('remove') == False:
		return

	# find and remove expense
	try:
		expense = dataFromFile['categories'][expenseCat][expenseName]
		if expense != None:
			if expenseDate != None:
				if expense['Date'] == expenseDate:
					yn = input(f'Are you sure you want to delete the following expense?\nName: {expenseName}\nCategory: {expenseCat}\nAmount: {expense['Amount']}\nDate: {expenseDate}\n y/n?')
					if yn in validAgrees:
						dataFromFile['categories'][expenseCat].pop(expenseName)
						saveToFile(file, dataFromFile)
						print('Expense removed from file.')
			elif expenseVal != None:
				if expense['Amount'] == expenseVal:
					yn = input(f'Are you sure you want to delete the following expense?\nName: {expenseName}\nCategory: {expenseCat}\nAmount: {expense['Amount']}\nDate: {expense['Date']}\n y/n?')
					if yn in validAgrees:
						dataFromFile['categories'][expenseCat].pop(expenseName)
						saveToFile(file, dataFromFile)
						print('Expense removed from file.')
	except Exception as e:
		funcErrorOutput('General exception', e, 'general fault for trying to delete expense after passing checkExpensePresense')


# testing
#os.path.join(expenseFilesDir, 'test.json')
addExpense(os.path.join(expenseFilesDir, 'test.json'))

# main