import json
from datetime import date, time, datetime
#import myUtils
import os
import inspect
import traceback

#rich imports
import rich
from rich import print, align
from rich.columns import Columns
from rich.console import Console
from rich.theme import Theme

theme = Theme({
    "info": "cyan",
    "warn": "yellow",
    "error": "bold red"
})

console = Console(theme=theme)

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

# global vars, make settings file at some point - json maybe

currentFilePath = os.path.join(os.path.abspath(__file__), 'reports')
currentDir = os.path.dirname(currentFilePath)
parentDir = os.path.dirname(currentDir)
expenseFilesDir = os.path.join(parentDir, 'reports')

validAgrees = ['y', 'yes']

maxRetries = 2

# functions

def funcErrorOutput(errortype, rawError, comments='No comments provided.'):
	tbList = traceback.extract_tb(rawError.__traceback__)
	fName, lineNum, funcName, text = tbList[-1]
	print('\n') # newline for clarity
	console.print(f'[error]{inspect.currentframe().f_back.f_code.co_name}: {errortype}[/error]\n  Passed comments: {comments}\n  Line: {lineNum}\n  Raw error: {rawError}')

def funcWarnOutput(warnType, rawWarn=None, comments='No comments provided.'):
	if rawWarn != None:
		tbList = traceback.extract_tb(rawWarn.__traceback__)
		fName, lineNum, funcName, text = tbList[-1]
	print('\n') # newline for clarity
	console.print(f'[warn]{inspect.currentframe().f_back.f_code.co_name}: {warnType}[/warn]\n  Passed comments: {comments}\n  Line: {lineNum if rawWarn != None else 'N/A'}\n  Raw error: {rawWarn if rawWarn != None else 'N/A'}')

def saveToFile(file, data): # Add error handling
	with open(file, mode='w', encoding='utf-8') as f:
		json.dump(data, f, indent=2)

def loadFromFile(file): # Add error handling
	with open(file, mode='r', encoding='utf-8') as f:
		data = json.load(f)
		return data

def checkCatPresense(data, category, rePrompt=True):
	if category in data['categories'].keys():
		if rePrompt == True:
			change = input(f'A category matching the name provided ({category}) already exists in the current file. Would you like to enter a different name? y/n\n')
			if change in validAgrees:
				category = input('Name of category: ')
				return category
			else:
				return True
		elif rePrompt == True:
			return True
	elif category not in data['categories'].keys():
		if rePrompt == False:
			return False
		elif rePrompt == False:
			change = input(f'A category matching the name provided ({category}) could not be found in the current file. Would you like to ender a different name? y/n\n')
			if change in validAgrees:
				category = input('Name of category: ')
				return category

def checkForFile(file, path):
	try:
		for (root, dirs, files) in os.walk(path, topdown=True):
			if file in files:
				return True, os.path.join(root, file)
	except Exception as e:
		pass
	return False, file, path

def getFileCharCount(path):
	try:
		with open(path, 'r') as file:
			content = file.read()
			return len(content)
	except Exception as e:
		pass

# menus

def mainMenu():
	print(align.Align('[white bold]Main Menu[/white bold]', align='center'))
	print('1. Open file')
	print('2. Settings')
	print('3. Help')
	print('4. Exit')

def settingsMenu(file):
	pass

# commands

def addExpense(file): # add error handling
	
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
	except ValueError as ve: # add general exception clause
		funcErrorOutput('ValueError', ve, f'Error during conversion of expenseVal to float, expenseVal: {expenseVal}')
		print('Aborting command due to error.')
		return

	dataFromFile = loadFromFile(file)
	print(f'datafromfile:{dataFromFile}')

	# invalid input error handling when i get around to it
	
	dataFromFile['categories'][expenseCat][expenseName] = {'Amount' : expenseVal, 'Date': expenseDate} # throw in try/except and add error handling
	saveToFile(file, dataFromFile)
	print('Expense added to file.')

def removeExpense(file): # add error handling
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
	except Exception as e: # add more specific errors
		funcErrorOutput('General exception', e, 'general fault for trying to delete expense after passing checkExpensePresense')

def addCategory(file): # add error handling
	category = input('Name of the category to add: ')

	data = loadFromFile(file)

	# input validation and checking
	timesChecked = 0

	while timesChecked <= maxRetries:
		timesChecked+=1
		out = checkCatPresense(data, category)
		if out == True:
			break
		elif out == False:
			print('Aborting command')
			return
		else:
			category = out
		if timesChecked == maxRetries:
			print(f'Aborting command due to invalid category input.')
			return
	data['categories'][category] = {}
	saveToFile(file, data)
	print('Category added successfully.')

def removeCategory(file): # add error handling
	category = input('Name of the category to remove: ')

	data = loadFromFile(file)

	# input validation and checking
	timesChecked = 0

	while timesChecked <= maxRetries:
		timesChecked+=1
		out = checkCatPresense(data, category)
		print(f'out: {out}')
		if out == True:
			break
		elif out == False:
			print('Aborting command')
			return
		else:
			category = out

		if timesChecked == maxRetries:
			print(f'Aborting command due to invalid category input.')
			return
	
	choice = input(f'Are you sure you want to delete {category}? y/n\n')

	if choice in validAgrees:
		data['categories'].pop(category) # add try/except wrapper
		saveToFile(file, data)
		print('Category removed successfully.')

# command mapping
commandsDict = {
	('addexpense', 'add expense', 'add-expense', 'add_expense', 'ae') : addExpense
}

mainOpsDict = {
	('openfile', 'open file', 'open_file', 'open-file', 'of', '1') : None # fix when function made
}

# settings

settingsTemplate = {
	'settings': {
		'reportDir': expenseFilesDir,
		'reportIndent': 2,
		'encoding': 'utf-8',
		'commands': {
			#read in commands from commandsDict ig for defaults, maybe add custom command support?
		},
		'styles':{
			"info": "dim cyan",
		    "warning": "yellow",
		    "error": "bold red"
		}
	}
}

currentSettings = None

def readSettings(name, dir):
	# add input validation for name and director
	
	filePres = checkForFile(name, dir)
	if filePres[0] == True:
		try:
			if getFileCharCount(filePres[1]) <= 2:
				funcWarnOutput('File does not meet minimum length requirements', rawWarn=None, comments='settings file character count was less than the minimum required characters for proper syntax.')
				return None
			data =  loadFromFile(filePres[1])
			return data
		except json.decoder.JSONDecodeError as jde:
			size = os.path.getsize(filePres[1])
			fileEmpty = 'The file is empty'
			backup = 'The file may have syntax errors inside.'
			funcErrorOutput('JSON Decode Error', jde, f'Error when attempting to parse settings.json file. {fileEmpty if size==0 else backup}, creating new settings file from defaults.')
			choice = input('Would you like to save the current settings file for manual review? y/n\n')
			if choice in validAgrees:
				try:
					os.rename(filePres[1], 'settingsOld.json')
				except PermissionError as pe:
					funcErrorOutput('PermissionError', pe, f'Permission error when attempting to rename settings file in path {os.path.join(dir,name)}')
				
				#create new file
				try:
					with open(os.path.join(dir, name), 'w+', encoding=settingsTemplate['settings']['encoding']) as file:
						saveToFile(file, settingsTemplate)
				except PermissionError as pe:
					funcErrorOutput('PermissionError', pe, f'Permission error when attempting to create new settings file in path {os.path.join(dir, name)}')

	elif filePres[0] == False:
		console.print(f'[warn]WARNING: File Not Found[/warn]\nNo file was found, [info]file name provided: {filePres[1]} path provided: {filePres[2]}[/info]')
		choice = input('Would you like to create a new settings file from the default settings? y/n\n')
		if choice in validAgrees:
			try:
				with open(os.path.join(dir, name), 'w+', encoding=settingsTemplate['settings']['encoding']) as file:
					saveToFile(file, settingsTemplate)
			except PermissionError as pe:
				funcErrorOutput('PermissionError', pe, f'Permission error when attempting to create new settings file in path {os.path.join(dir, name)}')

currentSettings = readSettings('settings.json', parentDir)


#main global vars
inMainMenu = False
currentFile = None

# testing
#os.path.join(expenseFilesDir, 'test.json')
#removeCategory(os.path.join(expenseFilesDir, 'test.json'))

# main program loop
""" def main():
	mainMenu()
	inMainMenu = True
	chosenOperation = input()
	for key in mainOpsDict.keys():
		if chosenOperation.lower == key():
			pass
if __name__ == '__main__':
		while True:
			try:
				main()
			except KeyboardInterrupt:
				print('Returning to main menu.')
			except Exception as e: """