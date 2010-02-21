from mod_python import apache
import sys
import MySQLdb
sys.path.append('/home/reldnahcire/nonPublicDir/') #put the database connection info somewhere.py
import dbConstants
import json

def getConnection():
	db = MySQLdb.connect(host = dbConstants.host,
		user = dbConstants.user, passwd = dbConstants.pw,
		db = dbConstants.database)
	db.set_character_set('utf8')
        cursor = db.cursor()
        cursor.execute('SET NAMES utf8')
        cursor.execute('SET CHARACTER SET utf8')
        cursor.execute('SET character_set_connection=utf8')
        return db
        
def processQuery(db, query):
	resultsList = []
	db.query(query)
	result = db.store_result()
	rowSet = result.fetch_row(maxrows=0, how=1)
	currentLandmark = {}
	for dict in rowSet:
		for key in dict:
			currentLandmark[key] = dict[key]
		resultsList.append(currentLandmark)
		currentLandmark = {}
	answer = json.dumps(resultsList)
	return answer
	
def processVariables(latitude, longitude, threshold):
	try:
		threshold = int(threshold)
	except ValueError:
		threshold = int(10000)
	try:
		latitude = float(latitude)
	except ValueError:
		latitude = 44.4600348119
	try:
		longitude = float(longitude)
	except ValueError:
		longitude = -93.1517833713
	return latitude, longitude, threshold

def processVariablesWithUDID(udid, latitude, longitude, threshold):
    
	#Process the udid to sanatize for the DB and confirm 40
	#character length
	if len(udid) != 40:
		udid = '1111111111111111111111111111111111111111'
	udid = MySQLdb.escape_string(udid)
	udid = '\'+udid+\''
	
	try:
		threshold = int(threshold)
	except ValueError:
		maxLandmarks = 10
	try:
		latitude = float(latitude)
	except ValueError:
		latitude = 44.4600348119
	try:
		longitude = float(longitude)
	except ValueError:
		longitude = -93.1517833713
	return udid, latitude, longitude, threshold