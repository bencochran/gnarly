from mod_python import apache
import sys
import MySQLdb
sys.path.append('/home/reldnahcire/nonPublicDir/') #put the database connection info somewhere.py
import dbConstants

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

def CarletonBuildings(req, lat='0',long='0',maxLandmarks='10'):
	"""If values aren't numbers, assumes 10, a number we discussed
	and that you are in Memorial Hall, since you can't pass decent GPS
	coordinates"""

	try:
		maxLandmarks = int(maxLandmarks)
	except ValueError:
		maxLandmarks = 10
	try:
		lat = float(lat)
	except ValueError:
		lat = 44.4600348119 
	try:
		long = float(long)
	except:
		long = -93.1517833713
	
	query = "SELECT landmarkTable.*, GeoDistMi(landmarkTable.latitude, landmarkTable.longitude, %f, %f) as distance, CarletonBuildings.landmarkID, landmarkTable.name FROM landmarkTable JOIN CarletonBuildings IN landmarkTable.id = CarletonBuildings.landmarkID ORDER BY distance ASC LIMIT %d" % (lat, long, maxLandmarks)

	
	
	return "This is the query: \n" + query


def CarletonBuildingsCall(database, latitude, longitude, maxlandmarks):
	pass

if __name__ == '__main__':
	db = getConnection()
	answer = gps(db, 'Sayles-Hill')
	print answer
