from mod_python import apache
import sys
import MySQLdb
sys.path.append('/home/reldnahcire/nonPublicDir/') #put the database connection info somewhere.py
import dbConstants
import json


def getConnection():
	"""getConnection accesses the information necesary to connect to the Gnarus DB from a secure location"""
	db = MySQLdb.connect(host = dbConstants.host,
		user = dbConstants.user, passwd = dbConstants.pw,
		db = dbConstants.database)
	db.set_character_set('utf8')
        cursor = db.cursor()
        cursor.execute('SET NAMES utf8')
        cursor.execute('SET CHARACTER SET utf8')
        cursor.execute('SET character_set_connection=utf8')
        return db
        		
def variableSetup(udid, latitude, longitude, maxLandmarks):
	"""Converts variables to the right type.  If any of these fail has
	default values"""

	#This checks the UDID of the phone and was disabled for testing the simulator
	#if len(udid) != 40:
	#    udid = 'd94954ea4c18630447be1bd357922ffe1b52a0e2'
	
	udid = MySQLdb.escape_string(udid)
	udid = "\'"+udid+"\'"
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

	return udid, latitude, longitude, maxLandmarks

def processQuery(db, query):
	"""This function takes a database and a SQL query and returns the results
	as a JSON formatted dictionary"""
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
	"""A method to hopefully get information out of the sql database and print it on screen."""
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

def SportingArenas(req, udid, lat='0', lon='0', maxLandmarks='10'):
	"""Returns landmarks that have been validated or voted 
	on by the current user for the Sporting Arenas layer.
	If values aren't numbers, assumes 10, a number we discused
        and that you are in Memorial Hall, since you can't pass decent GPS
        coordinates"""
	database = getConnection()
	udid, lat, lon, maxLandmarks = variableSetup(udid, lat, lon, maxLandmarks)
	query = "SELECT SportingArenas.summary, SportingArenas.imageURL, SportingArenas.scheduleURL, SportingArenas.usedBy, landmarkTable.id, landmarkTable.name, GeoDistM(landmarkTable.latitude, landmarkTable.longitude, %f, %f) as distance, landmarkTable.latitude, landmarkTable.longitude FROM landmarkTable JOIN SportingArenas ON landmarkTable.id = SportingArenas.landmarkID AND (SportingArenas.landmarkID in (SELECT landmarkID FROM SportingArenasVotes Group By landmarkID HAVING COUNT(*) >2 UNION DISTINCT SELECT landmarkID FROM SportingArenasVotes where userID in (SELECT userTable.id from userTable where userTable.udid = %s))) ORDER BY distance ASC LIMIT %d" % (lat, lon, udid, maxLandmarks)
	answer = processQuery(database, query)
	return answer

def Carleton(req, udid = None, lat='0',lon='0',maxLandmarks='10'):
	""""Returns landmarks that have been validated or voted
         on by the current user for the Carleton layer.
	If values aren't numbers, assumes 10, a number we discussed
	and that you are in Memorial Hall, since you can't pass decent GPS
	coordinates"""
	database = getConnection() 
	udid, lat, lon, maxLandmarks = variableSetup(udid, lat, lon, maxLandmarks)
	query = "SELECT Carleton.summary, Carleton.imageURL, Carleton.description, Carleton.yearBuilt, landmarkTable.id, landmarkTable.name, GeoDistM(landmarkTable.latitude, landmarkTable.longitude, %f, %f) as distance, landmarkTable.latitude, landmarkTable.longitude FROM landmarkTable JOIN Carleton where landmarkTable.id = Carleton.landmarkID AND (Carleton.landmarkID in (SELECT landmarkID FROM CarletonVotes Group By landmarkID HAVING COUNT(*) >2 UNION DISTINCT SELECT landmarkID FROM CarletonVotes where userID in (SELECT userTable.id from userTable where userTable.udid = %s)) OR landmarkTable.id < 94) ORDER BY distance ASC LIMIT %d" % (lat, lon, udid, maxLandmarks)
	answer = processQuery(database, query)
	return answer
	
def Food(req, udid, lat='0', lon='0', maxLandmarks='10'):
	""""Returns landmarks that have been validated or voted 
        on by the current user for the Food ayer.
	If values aren't numbers, assumes 10 for the value of maxLandmarks and assumes
	 you are in memorial since you can't get decent gps there"""
	database = getConnection()
	udid, lat, lon, maxLandmarks = variableSetup(udid, lat, lon, maxLandmarks)
	query = "SELECT Food.summary, Food.hours, Food.menu, Food.description, Food.imageURL, landmarkTable.name, landmarkTable.id, GeoDistM(landmarkTable.latitude, landmarkTable.longitude, %f, %f) as distance, landmarkTable.latitude, landmarkTable.longitude From landmarkTable JOIN Food ON landmarkTable.id = Food.landmarkID AND (Food.landmarkID in (SELECT landmarkID FROM FoodVotes Group By landmarkID HAVING COUNT(*) >2 UNION DISTINCT SELECT landmarkID FROM FoodVotes where userID in (SELECT userTable.id from userTable where userTable.udid = %s))) ORDER BY distance ASC LIMIT %d" % (lat, lon, udid, maxLandmarks)
	answer = processQuery(database, query)
	return answer
