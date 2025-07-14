import requests

version = '1.0.0'
versionList = version.split('.')

versionKeywords = ['security', 'high', 'medium', 'low']

def checkVersion():
	response  = requests.get('https://api.github.com/repos/Jitzwaz/Py-Expense/releases/latest')

	data = response.json()

	verNum = data['name']
	relBody =data['body']

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
	print(msg)
	print(f'Currently installed version: {version}, Latest available version: {verNum}')

checkVersion()