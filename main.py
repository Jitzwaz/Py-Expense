import json
from datetime import date, time, datetime
import os
import sys
import inspect
import traceback

# sweet ass styling stuff
import pyfiglet
from rich import print, align
from rich.columns import Columns
from rich.console import Console
from rich.theme import Theme
from tqdm.rich import tqdm_rich
from rich.progress import (BarColumn, MofNCompleteColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn)
import requests

theme = Theme({ # move and read from settings or something
	'label' : 'cyan',
	'text': 'white',
    'info': 'cyan',
    'warn': 'yellow',
    'error': 'bold red'
})

customProgressColumns = (
        TextColumn('[progress.percentage]{task.percentage:>3.0f}%'),
		TextColumn('Reading file.'),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn('[cyan]| Time Elapsed: [/cyan]'),
        TimeElapsedColumn(),
        TextColumn('[cyan]| Time remaining: [/cyan]'),
        TimeRemainingColumn(),
    )

console = Console(theme=theme)
# just for data structure reference
# template = {
# 	'categories': {
# 		'category': {
# 			'expense': {
# 				'Amount': 12,
# 				'Date': '10/12/25'
# 			}
# 		}
# 	}
# }

# global vars

version = '1.0.0'
versionList = version.split('.')
versionKeywords = ['security', 'high', 'medium', 'low']

# move to settings
catIndent = 0
expenseIndent = 2
expenseSutffIndent = 4

states = {
	'menus' : {
		'inMainMenu' : False,
		'inSettingsMenu' : False,
		'inHelpMenu' : False
	},
	'currentFile' : None,
	'startup' : True
}


# path shit to get current path to reports dir, add error handling incase it doesn't exist
# move to after settings to do only on first startup?
currentFilePath = None
currentDir = None
parentDir = None
expenseFilesDir = None

validAgrees = ['y', 'yes'] # basic valid agrees, probably could incorporate into settings

validEmptySettings = [None, '', 'None']

maxRetries = 2 # incorporate into settings maybe?

currentSettings = None # here for funtion use

# functions

def checkVersion(): # add error handling for http errors n other stuff
	response  = requests.get('https://api.github.com/repos/Jitzwaz/Py-Expense/releases/latest')

	data = response.json()

	verNum = data['name']
	relBody = data['body']

	posDict = {
		'0' : 'major',
		'1' : 'minor',
		'2' : 'patch'
	}

	msgsDict = {
		'high' : 'high urgency',
		'medium' : 'medium urgency',
		'low' : 'low urgency',
		'security' : 'security'
	}

	msg = 'There is a(n) '

	for keyword in versionKeywords:
		if keyword in relBody.lower():
			msg+=f'{msgsDict[keyword]} '

	verNumList = verNum[1::].split('.')
	for i, curVerNum in enumerate(versionList):
		if int(curVerNum) < int(verNumList[i]):
			msg+=posDict[str(i)]
			if i != 2:
				msg+=' update available.'
			elif i == 2:
				msg+= ' available.'
	console.print(f'[info]{msg}[/info]')
	console.print(f'[info]Currently installed version: {version}, Latest available version: {verNum}[/info]')

def funcErrorOutput(errortype: str, rawError: Exception, comments:str='No comments provided.', funcArgs:tuple=None) -> None:  # add logging in future update
	'''
	Prints an error with the name of the function that called it, the type of error, 
	the raw error information, the line it occured on, and any passed comments.	

	Args:
		errortype (string): The name of the error
		rawError: the exception (exception as e)
		comments: Optional but a string that is provided
	
	Actions performed:
		Console print
	
	Returns:
		None
	'''
	tbList = traceback.extract_tb(rawError.__traceback__)
	fName, lineNum, funcName, text = tbList[-1]
	print('\n') # newline for clarity
	console.print(f'[error]{inspect.currentframe().f_back.f_code.co_name}: {errortype}[/error]\n  Passed comments: {comments}\n  Line: {lineNum}\n  Raw error: {rawError}')

def funcWarnOutput(warnType: str, rawWarn=None, comments='No comments provided.', funcArgs:tuple=None):
	'''
	Actions performed a warning with the name of the function that called it, the type of warning, 
	the raw exception information, the line it occured on, and any passed comments.	

	Args:
		warnType: string containing the name of the warning
		rawWarn: the exception (exception as e) (OPTIONAL)
		comments: Optional but a string that is provided
	
	Actions performed:
		Console print
	
	Returns:
		None
	'''
	if rawWarn != None:
		tbList = traceback.extract_tb(rawWarn.__traceback__)
		fName, lineNum, funcName, text = tbList[-1]
	print('\n') # newline for clarity
	console.print(f'[warn]{inspect.currentframe().f_back.f_code.co_name}: {warnType}[/warn]\n  Passed comments: {comments}\n  Line: {lineNum if rawWarn != None else 'N/A'}\n  Raw error: {rawWarn if rawWarn != None else 'N/A'}')

# make some kind of standardization to determine whats a set, tuple, etc when extracted and when saved

def saveToFile(file:str, data:dict):
	'''
	Saves data to a JSON file in JSON format.

	Args:
		file: a valid path to the file
		data: any data to be encoded into JSON format
	
	Actions performed:
		Encoded json data that's written to a file.
	
	Returns:
		None
	'''
	try:
		with open(file, mode='w', encoding='utf-8') as f:
			json.dump(data, f, indent=currentSettings['settings']['reportIndent'])
	except PermissionError as pe:
		funcErrorOutput('Permission Error', pe, f'Permission error when attempting to save data to file ({file})')
		# test below before implementing
		#console.print('[info]Dumping provided data to dump.json[/info]')
		#with open(os.path.join(parentDir, 'dump.json'), mode='a', encoding='utf-8') as file:
		#	json.dump(data, file, indent=currentSettings['settings']['reportIndent'])

def loadFromFile(file:str):
	'''
	Loads data from a JSON file to python (still in JSON format so nothing has been converted)

	Args:
		file: a valid path to the file
	
	Actions performed: 
		Encoded JSON data that was extracted from a file

	Returns:
		Extracted JSON data
	'''
	try:
		with open(file, mode='rb') as f:
			extractedData = b''
			sizeOfFile = os.path.getsize(file)
			with tqdm_rich(total=sizeOfFile, unit='B', unit_scale=True, desc='Reading file', progress=customProgressColumns) as pBar:
				while True:
					chunk = f.read(1024)
					extractedData +=chunk
					if not chunk:
						break
					pBar.update(len(chunk))
			extractedData = extractedData.decode('utf-8')
			data = json.loads(extractedData)
			return data
	except PermissionError as pe:
		funcErrorOutput('Permission Error', pe, 'Permission error occured while attempting to load file.')
	except json.JSONDecodeError as JDE:
		funcErrorOutput('Json Decode Error', JDE, 'JSON Decode Error when attempting to load file.')

def checkCatPresense(data:dict, category:str, rePrompt=True): # remove re-prompt and leave it up to the function in future update
	'''
	Checks the presense of a category from provided JSON data.

	Args:
		data (dict): The extracted JSON data.
		category (string): The name of the category.
		rePrompt (bool): Determines if the user should be reprompted for a category name if it's already found	.
	
	Actions performed:
		Checks provided JSON data for the presence of the provided category.

	Returns:
		Bool, denoting the presense if rePrompt is disabled.\n
		String, containing the name of the category if rePrompt is enabled.
	'''
	try:
		if category in data['categories'].keys():
			if rePrompt == True:
				change = input(f'A category matching the name provided ({category}) already exists in the current file. Would you like to enter a different name (Y/N)?\n')
				if change in validAgrees:
					category = input('Name of category: ')
					return category
				else:
					return True
			elif rePrompt == False:
				return True
		elif category not in data['categories'].keys():
			if rePrompt == False:
				return False
			elif rePrompt == False:
				change = input(f'A category matching the name provided ({category}) could not be found in the current file. Would you like to ender a different name(Y/N)?\n')
				if change in validAgrees:
					category = input('Name of category: ')
					return category
	except Exception as e: # idk what could go wrong witht his one
		funcErrorOutput('General Exception', e, f'Unknown general exception. args provided:\ndata: {data}\ncategory: {category}\nrePrompt: {rePrompt}')
		return None

def checkForFile(file:str, path:str):
	'''
	Checks if a file exists

	Args:
		file (string): Name of the file
		path (string): Path to the driectory to search
	Actions performed:

	Returns:
		True, fullPath to file (if sucessfully found)
		False, file, path (if unsucessfully found)
	'''
	try:
		for (root, dirs, files) in os.walk(path, topdown=True):
			if file in files:
				return True, os.path.join(root, file)
	except Exception as e:
		funcErrorOutput('General exception', e, 'idk man')
	return False, file, path

def getFileCharCount(path):
	try:
		with open(path, 'r') as file:
			content = file.read()
			return len(content)
	except PermissionError as pe:
		funcErrorOutput('Permission Error', pe, f'Unable to access file({file}) due to a permission error.')
		return None
	except FileNotFoundError as FNF:
		funcErrorOutput('File Not Found Error', FNF, f'File ({file}) was unable to be found to read char count.')
		return None

def asciiPrint(text, style, color, alignment='left', width=50):
	f = pyfiglet.Figlet(font=style)
	asciiText = pyfiglet.figlet_format(text, font=style, width=width)
	print(align.Align(f'[{color}]{asciiText}[/{color}]', align=alignment))

def getDirs(getExpenseDir=True):
	'''
	Gets the path params that all the functions use (parentDir, expenseFilesDir, etc)

	Args:
		getExpenseDir (bool): Determines whether to get the expense files directory
	
	Returns:
		True (tuple): (currentFilePath, parentDir, expenseFilesDir)\n
		False (tuple): (currentFIlePath, parentDir)\n
	'''
	try:
		if getExpenseDir == True:
			currentFilePath = os.path.abspath(__file__)
			parentDir = os.path.dirname(currentFilePath)
			expenseFilesDir = os.path.join(parentDir, 'reports')
			return (currentFilePath, parentDir, expenseFilesDir)
		else:
			currentFilePath = os.path.abspath(__file__)
			parentDir = os.path.dirname(currentFilePath)
			return (currentFilePath, parentDir)
	except Exception as e: # idk what else could happen tbh
		funcErrorOutput('General exception', e)

#def checkExpensePresense(expenseName, expenseCat, expenseVal, expenseDate, operation):
	


def addExpense(file):
	
	stuffNotFound = [] # hold list of what wasn't correct so i can use a for loop later and look super cool

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
		console.print('[info]Aborting command due to error.[/info]')
		return

	try:
		dataFromFile = loadFromFile(file)
	except json.JSONDecodeError as JDE:
		funcErrorOutput('Json Decode Error', JDE, f'JDE when trying to read data from the provided file ({file})')

	
	# invalid input handling
	# input validation

	# actual adding
	try:
		try:
			dataFromFile['categories'][expenseCat][expenseName] = {'Amount' : expenseVal, 'Date': expenseDate} # throw in try/except and add error handling
		except KeyError as ke:
			funcErrorOutput('Key Error', ke, f'Key error when attempting to add expense to {expenseCat}.')
		saveToFile(file, dataFromFile)
		console.print('[text]Expense added to file.[/text]')
	except PermissionError as pe:
		funcErrorOutput('Permission Error', pe, 'Permission error when attempting to save expense to file.')
	except Exception as e:
		funcErrorOutput('Unexpected Exception', e, f'Unexpected error. File provided: {file}')

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
				if expenseDate != None:
					if expenseDate != dataFromFile['categories'][expenseCat][expenseName]['Date']:
						change = input(f'The expense you are trying to {operation} ({expenseName}) could not be found with a matching date, would you like to change the date (Y/N)?\n')
						if change in validAgrees:
							expenseDate = input('Date of expense: ')
							checkExpensePresense(operation)
						else:
							print('Aborting command.')
							return False
				elif expenseVal != dataFromFile['categories'][expenseCat][expenseName]['Amount']:
					change = input(f'The expense you are trying to {operation} ({expenseName}) could not be found with a matching amount, would you like to change the amount (Y/N)?\n')
					if change in validAgrees:
						expenseVal = input('Amount of expense: ')
						checkExpensePresense(operation)
					else:
						print('Aborting command.')
						return False
			elif expenseName not in dataFromFile['categories'][expenseCat].keys():
				change = input(f'The expense you are trying to {operation} ({expenseName}) has not been found by, would you like to change the name (Y/N)?\n')
				if change in validAgrees:
					expenseName = input('Name of expense: ')
					checkExpensePresense(operation)
				else:
					print('Aborting command.')
					return False

	if checkExpensePresense('remove') == False: # couldn't find
		return

	# find and remove expense
	try:
		expense = dataFromFile['categories'][expenseCat][expenseName]
		if expense != None:
			if expenseDate != None:
				if expense['Date'] == expenseDate:
					yn = input(f'Are you sure you want to delete the following expense?\nName: {expenseName}\nCategory: {expenseCat}\nAmount: {expense['Amount']}\nDate: {expenseDate} (Y/N)?\n')
					if yn in validAgrees:
						dataFromFile['categories'][expenseCat].pop(expenseName)
						saveToFile(file, dataFromFile)
						print('Expense removed from file.')
			elif expenseVal != None:
				if expense['Amount'] == expenseVal:
					yn = input(f'Are you sure you want to delete the following expense?\nName: {expenseName}\nCategory: {expenseCat}\nAmount: {expense['Amount']}\nDate: {expense['Date']} (Y/N)\n')
					if yn in validAgrees:
						dataFromFile['categories'][expenseCat].pop(expenseName)
						saveToFile(file, dataFromFile)
						print('Expense removed from file.')
	except PermissionError as pe:
		funcErrorOutput('Permission Error', pe, f'Permission error when attempting to save changes to "{file}"')
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
		if out == None:
			funcWarnOutput('Category was unable to be checked', comments=f'None was returned when attempting to check for "{category}".')
		if out == False: # it exists wooohooo
			break
		elif out == True:
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
	
	choice = input(f'Are you sure you want to delete {category} (Y/N)?\n')

	if choice in validAgrees:
		data['categories'].pop(category) # add try/except wrapper
		saveToFile(file, data)
		print('Category removed successfully.')

def viewAllExpenses(file):
	data = loadFromFile(file)
	for cat in data['categories'].keys():
		print(f'{cat}:')
		for expense in data['categories'][cat].keys():
			printOut = ''+(' '*expenseIndent)
			printOut+=f'{expense}:'
			print(printOut)
			for key, val in data['categories'][cat][expense].items():
				printOut = ''+(' '*expenseSutffIndent)
				printOut+=f'{key} : {val}'
				print(printOut)
			print()

def totalExpenses(file):
	pass

# Main operations

def openFile(): # add input validation and error handling
	fileName = input('What expense file would you like to open?\n ')
	filePres = checkForFile(fileName+'.json', currentSettings['settings']['reportDir'])
	if filePres[0] == True: # file found
		states['menus']['inMainMenu'] = False
		states['currentFile'] = filePres[1]
		console.print('[info]File successfully opened.[/info]')

def closeFile(): # add input validation and error handling
	choice =  input('Are you sure you want to close the current file (Y/N)? ')
	if choice in validAgrees:
		states['currentFile'] = None

def close():
	choice = input('Are you sure you want to close the program (Y/N)? ')
	if choice in validAgrees:
		print('Closing.')
		sys.exit()

# command mapping
commandsDict = {
	'addExpense' : {
		'calls' : ('addexpense', 'add expense', 'add-expense', 'add_expense', 'ae'),
		'function' : addExpense,
		'helpMenu' : 'As the name suggests addExpense adds an expense to the currently open file.\n'
	},
	'removeExpense' : {
		'calls' : ('removeexpense', 'remove expense', 'remove-expense', 'remove_expense', 're'),
		'function' : removeExpense,
		'helpMenu' : 'removeExpense help!!!'
	},
	'addCategory' : {
		'calls' : ('addcategory', 'add category', 'add_category', 'add-category', 'ac'),
		'function' : addCategory,
		'helpMenu' : ''
	},
	'removeCategory' : {
		'calls' : ('removecategory', 'remove category', 'remove_category', 'remove-category', 'rc'),
		'function' : removeCategory,
		'helpMenu' : ''
	},
	'openFile' : {
		'calls' : ('openfile', 'open file', 'open_file', 'open-file', 'of'),
		'function' : openFile,
		'helpMenu' : ''
	},
	'closeFile' : {
		'calls' : ('closefile', 'close file', 'close_file', 'close-file', 'cf'),
		'function' : closeFile,
		'helpMenu' : ''
	},
	'viewAllExpenses' : {
		'calls' : ('viewallexpenses', 'view all expenses', 'view_all_expenses', 'view-all-expenses', 'vae'),
		'function' : viewAllExpenses,
		'helpMenu' : ''
	}
}

# settings - add editing but loading n stuff is fine probably, run validation tests also add customizeable command calls eventually

settingsName = 'settings.json'
minSettingsCharCount = 2

settingsTemplate = {
	'settings': {
		'reportDir': None,
		'reportIndent': 2,
		'encoding': 'utf-8',
		'styles':{
			'info': 'dim cyan',
		    'warning': 'yellow',
		    'error': 'bold red'
		}
	}
}

def writeSettings(name:str, dir:str, save:bool, settings=None):
	filePres = checkForFile(name, dir)
	if filePres[0] == True:
		if save == True:
			try:
				os.rename(filePres[1], os.path.join(dir, 'settingsOld.json'))
			except PermissionError as pe:
				funcErrorOutput('PermissionError', pe, f'Permission error when attempting to rename settings file in path {os.path.join(dir,name)}')
		
		# create new file from template
		if settings == None:
			try:
				with open(os.path.join(dir, name), 'w+', encoding=settingsTemplate['settings']['encoding']) as file:
					saveToFile(os.path.join(dir, name), settingsTemplate)
			except PermissionError as pe:
				funcErrorOutput('PermissionError', pe, f'Permission error when attempting to create new settings file in path {os.path.join(dir, name)}')
		# update settings
		elif settings != None:
			try:
				with open(os.path.join(dir, name), 'w', encoding=settingsTemplate['settings']['encoding']) as f:
					saveToFile(os.path.join(dir,name), settings)
			except PermissionError as pe:
				funcErrorOutput('PermissionError', pe, f'Permission error when attempting to update settings file in path {os.path.join(dir, name)}')

def readSettings(name, dir):
	# add input validation for name and directory
	
	filePres = checkForFile(name, dir)
	if filePres[0] == True:
		try:
			if getFileCharCount(filePres[1]) <= minSettingsCharCount:
				funcWarnOutput('File does not meet minimum length requirements', rawWarn=None, comments=f'settings file character count was less than the minimum required characters ({minSettingsCharCount}).')
				print() # newline for beauty
				choice = input('Would you like to save the old settings file?')
				if choice in validAgrees:
					writeSettings(name, dir, True)
				else:
					writeSettings(name, dir, False)
				data = loadFromFile(filePres[1])
				return data
			elif getFileCharCount(filePres[1]) == None:
				funcWarnOutput('File characters could not be counted.', comments='Check for error from getFileCharCount above for more details.')
				return None
			data =  loadFromFile(filePres[1])
			return data
		except json.decoder.JSONDecodeError as jde:
			size = os.path.getsize(filePres[1])
			fileEmpty = 'The file is empty'
			backup = 'The file may have syntax errors inside.'
			funcErrorOutput('JSON Decode Error', jde, f'Error when attempting to parse settings.json file. {fileEmpty if size==0 else backup}, creating new settings file from defaults.')
			choice = input('Would you like to save the current settings file for manual review (Y/N)?\n')
			if choice in validAgrees:
				writeSettings(name, dir, True, settingsTemplate)
			else:
				writeSettings(name, dir, False)
			data = loadFromFile(filePres[1])
			return data

	elif filePres[0] == False:
		console.print(f'[warn]WARNING: File Not Found[/warn]\nNo file was found, [info]file name provided: {filePres[1]} path provided: {filePres[2]}[/info]')
		choice = input('Would you like to create a new settings file from the default settings (Y/N)?\n')
		if choice in validAgrees:
			try:
				with open(os.path.join(dir, name), 'w+', encoding=settingsTemplate['settings']['encoding']) as file:
					saveToFile(filePres[1], settingsTemplate)
					data = loadFromFile(filePres[1])
					return data
			except PermissionError as pe:
				funcErrorOutput('PermissionError', pe, f'Permission error when attempting to create new settings file in path {os.path.join(dir, name)}')

def repairSettings(name, dir): # read old settings data that has proper syntax?
	pass

currentFilePath, parentDir = getDirs(False)

currentSettings = readSettings('settings.json', parentDir)

if currentSettings == None:
	console.print(f'[error]CRITICAL ERROR: The settings file located in {parentDir} could not be read. See above errors/warnings for more information[/error]')

# check if expensedir in settings:
if currentSettings['settings']['reportDir'] == None:
	curFPath, parenDir, expenseDir = getDirs(True)
	currentSettings['settings']['reportDir'] = expenseDir
	writeSettings('settings.json', parenDir, False, currentSettings)


# menus

def mainMenu():
	try:
		states['menus']['inMainMenu'] = True
		states['startup'] = False
		asciiPrint('Main menu', 'slant', currentSettings['settings']['styles']['label'], 'center', 100)
		if states['currentFile'] != None:
			console.print(f'[info]Currently open file: {os.path.basename(states['currentFile']).split('.')[0]}[/info]\n')
		
		console.print(f'[cyan]Py-Expense v{version} by Jitzwaz[/cyan]')
		print()
		#checkVersion()
		#print()
		console.print('[label]1.[/label] [text]Open file[/text]')
		console.print('[label]2.[/label] [text]Close file[/text]')
		console.print('[label]3.[/label] [text]Help[/text]')
		console.print('[label]4.[/label] [text]Exit[/text]')
	except Exception as e: # incase some mystical exception breaks in
		funcErrorOutput('General Exception', e)

def settingsMenu(file): # add later
	pass

def helpMenu():
	try:
		states['menus']['inHelpMenu'] = True
		print('[text]1. Commands[/text]')
		print('[text]2. How to change the settings[/text]')
		print()
		choice = input('>>> ')
		if choice.lower() in ['1', 'commands']:
			for key in commandsDict.keys():
				console.print(f'[text]{key}[/text]\n')
		while True:
			choice2 = input('>>> ')
			for key in commandsDict.keys():
				if choice2.lower() in commandsDict[key]['calls']:
					console.print(f'[label]{key}[/label]\n')
					console.print(f'[text]  Valid calls: {commandsDict[key]["calls"]}[/text]\n')
					console.print(f'[text]  {commandsDict[key]["helpMenu"]}[/text]')
	except Exception as e: # idk what could go wrong here tbh
		funcErrorOutput('General Exception', e)

# main ops stuff, holds menus too
mainOpsDict = {
	'openFile' : {
		'calls' : ('openfile', 'open file', 'open_file', 'open-file', 'of', '1'),
		'function' : openFile
	},
	'close' : {
		'calls' : ('exit', '4'),
		'function' : close
	},
	'help' : {
		'calls' : ('help', '3'),
		'function' : helpMenu
	}
}

#viewAllExpenses(os.path.join(expenseFilesDir, 'test.json'))

runningMainloop = True

# main program loop
if runningMainloop == True:
	def main():
		try:
			
			if states['startup'] == True:
				mainMenu()
			if states['currentFile'] != None and states['menus']['inMainMenu'] == False:
				print()
				console.print(f'[info]Currently open file: {os.path.basename(states['currentFile']).split('.')[0]}[/info]\n')
			chosenOperation = input('>>> ')
			if states['menus']['inMainMenu'] == True:
				for key in mainOpsDict.keys():
					if chosenOperation.lower() in mainOpsDict[key]['calls']:
						func = mainOpsDict[key]['function']
						func()
				if states['currentFile'] != None:
					states['menus']['inMainMenu'] = False
			elif states['menus']['inMainMenu'] == False:
				for key in commandsDict.keys():
					if chosenOperation.lower() in commandsDict[key]['calls']:
						func = commandsDict[key]['function']
						func(states['currentFile'])
		except KeyboardInterrupt:
			print()
			mainMenu()

	if __name__ == '__main__':
			while True:
				try:
					main()
				except KeyboardInterrupt:
					mainMenu
				#except Exception as e:
				#	funcErrorOutput('Exception', e, 'General exception from main loop.')