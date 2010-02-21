from mod_python import apache
import sys
import MySQLdb
import json
import gnarusServer


def AddingToFood(req, lat='0', lon='0', maxDistance='10000'):
    db = gnarusServer.getConnection()
    lat, lon, maxDistance = gnarusServer.processVariables(lat, lon, maxDistance)
    query = "SELECT landmarkTable.id, landmarkTable.name, landmarkTable.latitude, landmarkTable.longitude, GeoDistM(landmarkTable.latitude, landmarkTable.longitude, %f, %f) as distance, Food.summary, Food.menu, Food.hours, Food.description, Food.imageURL From landmarkTable JOIN Food where landmarkTable.id = Food.landmarkID GROUP BY landmarkTable.id HAVING distance <=%d ORDER BY distance ASC" %(lat, lon, maxDistance)
    answer = gnarusServer.processQuery(db, query)
    return answer
    
def AddingToCarleton(req, lat='0', lon='0', maxDistance='10000'):
    db = gnarusServer.getConnection()
    lat, lon, maxDistance = gnarusServer.processVariables(lat, lon, maxDistance)
    query = "SELECT landmarkTable.id, landmarkTable.name, landmarkTable.latitude, landmarkTable.longitude, GeoDistM(landmarkTable.latitude, landmarkTable.longitude, %f, %f) as distance, Carleton.summary, Carleton.yearBuilt, Carleton.description, Carleton.imageURL From landmarkTable JOIN Carleton where landmarkTable.id = Carleton.landmarkID GROUP BY landmarkTable.id HAVING distance <=%d ORDER BY distance ASC" %(lat, lon, maxDistance)
    answer = gnarusServer.processQuery(db, query)
    return answer
    
def AddingToSportingArenas(req, lat='0', lon='0', maxDistance='10000'):
    db = gnarusServer.getConnection()
    lat, lon, maxDistance = gnarusServer.processVariables(lat, lon, maxDistance)
    query = "SELECT landmarkTable.id, landmarkTable.name, landmarkTable.latitude, landmarkTable.longitude, GeoDistM(landmarkTable.latitude, landmarkTable.longitude, %f, %f) as distance, SportingArenas.summary, SportingArenas.scheduleURL, SportingArenas.usedBy From landmarkTable JOIN SportingArenas where landmarkTable.id = SportingArenas.landmarkID GROUP BY landmarkTable.id HAVING distance <=%d ORDER BY distance ASC" %(lat, lon, maxDistance)
    answer = gnarusServer.processQuery(db, query)
    return answer
