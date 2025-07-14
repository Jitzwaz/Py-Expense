import os
from tqdm.rich import tqdm_rich
from rich.progress import (BarColumn, MofNCompleteColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn)
import json

customProgressColumns = (
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("[cyan]|[/cyan]"),
        TimeElapsedColumn(),
        TextColumn("[cyan]|[/cyan]"),
        TimeRemainingColumn(),
    )

def loadFromFile(file:str): # Add error handling
	'''
	Loads data from a JSON file to python (still in JSON format so nothing has been converted)

	Args:
		file: a valid path to the file
	
	Actions performed: 
		Encoded JSON data that was extracted from a file

	Returns:
		Extracted JSON data
	'''
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


loadFromFile('G:\programming stuff\practice stuff\python\CLI-Expense-Tracker\settings.json')