import json

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

# functions

def saveToFile(file, data):
	with open(file, mode='a', encoding='utf-8') as f:
		json.dump(data, f, indent=2)

def loadFromFile(file):
	with open(file, mode='r', encoding='utf-8') as f:
		data = json.load(f)
		return data
