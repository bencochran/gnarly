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
        
def variableSetup(latitude, longitude, maxLandmarks):
	try:
		maxLandmarks = int(maxLandmarks)
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

	return latitude, longitude, maxLandmarks

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
	
def gps(req, buildingName='Sayles-Hill'):
	"""A method to hopefully get information out of the sql database and print it on screen.
	"""
	database = getConnection()
	buildingName = MySQLdb.escape_string(buildingName)
	query = "SELECT * FROM landmarkTable WHERE name = '%s'" % buildingName
	database.query(query)
	result = database.store_result()
	rowSet = result.fetch_row(maxrows=0, how=1)
	lat = 0
	long = 0
	lat = rowSet[0]['latitude']
	long = rowSet[0]['longitude']
	return "The building you asked for, %s, is at latitude %f and longitude %f" % (buildingName, lat, long)

def SportingArenas(req, lat='0', lon='0', maxLandmarks='10'):
	"""If values aren't numbers, assumes 10, a number we discused
        and that you are in Memorial Hall, since you can't pass decent GPS
        coordinates"""
	database = getConnection()
	lat, lon, maxLandmarks = variableSetup(lat, lon, maxLandmarks)
	query = "SELECT SportingArenas.summaryString, SportingArenas.scheduleURL, SportingArenas.usedBy, landmarkTable.ID, landmarkTable.name, GeoDistM(landmarkTable.latitude, landmarkTable.longitude, %f, %f) as distance, landmarkTable.latitude, landmarkTable.longitude FROM landmarkTable JOIN SportingArenas ON landmarkTable.ID = SportingArenas.landmarkID ORDER BY distance ASC Limit %d" % (lat, lon, maxLandmarks)
	answer = processQuery(database, query)
	return answer

def Carleton(req, lat='0',lon='0',maxLandmarks='10'):
	"""If values aren't numbers, assumes 10, a number we discussed
	and that you are in Memorial Hall, since you can't pass decent GPS
	coordinates"""
	database = getConnection() 
	lat, lon, maxLandmarks = variableSetup(lat, lon, maxLandmarks)
	query = "SELECT Carleton.summary, Carleton.imageURL, Carleton.description, Carleton.yearBuilt, landmarkTable.ID, landmarkTable.name, GeoDistM(landmarkTable.latitude, landmarkTable.longitude, %f, %f) as distance, landmarkTable.latitude, landmarkTable.longitude FROM landmarkTable JOIN Carleton ON landmarkTable.ID = Carleton.landmarkID ORDER BY distance ASC LIMIT %d" % (lat, lon, maxLandmarks)
	answer = processQuery(database, query)
	return answer
	
def Food(req, lat='0', lon='0', maxLandmarks='10'):
	"""If values aren't numbers, assumes 10 for the value of maxLandmarks and assumes
	 you are in memorial since you can't get decent gps there"""
	database = getConnection()
	lat, lon, maxLandmarks = variableSetup(lat, lon, maxLandmarks)
	query = "SELECT Food.summary, Food.menu, Food.description, Food.imageURL, landmarkTable.name, landmarkTable.ID, GeoDistM(Food.latitude, Food.longitude, %f, %f) as distance, Food.latitude, Food.longitude From Food ORDER BY distance ASC LIMIT %d" % (lat, lon, maxLandmarks)
	answer = processQuery(database, query)
	return answer
