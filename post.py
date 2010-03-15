from mod_python import apache
import os
from serverFunctions import *
from serverFuncOO import *
import json
	
# vote update form

def voteForm(req):

	return '''
    <html>
    <head><title>voteForm</title></head>
    <body>
    
    <form method="POST" enctype="multipart/form-data" action="http://dev.gnar.us/post.py/vote">
    tableName:
	<select name="tableName">
	<option value="Food">Food</option>
	<option value="Carleton">Carleton</option>
	<option value="SportingArenas">Sporting Arenas</option>
	</select> </br>
    landmarkID: <input type="text" name="landmarkID" /></br>
	UDID: <input type="text" name="UDID" /></br>
    <input type="submit" />
    </form>
    
    </body>
    </html>
    '''

def vote(req, tableName, landmarkID, UDID):
	
	try:
		voteDBUpdate(tableName,landmarkID, UDID)
		return "Vote Counted"
	except Exception, e:
		return 'Exception: %s ' % (e)
		

	
# Code for food layer
# (Replaced by generalLayer)

def foodForm(req):
    
    return '''
    <html>
    <head><title>FoodForm</title></head>
    <body>
    
    <form method="POST" enctype="multipart/form-data" action="http://dev.gnar.us/post.py/food">
	Landmark ID: <input type="text" name="landmarkID" /></br>
	UDID: <input type="text" name="UDID" /></br>
    lat: <input type="text" name="lat" /></br>
    lng: <input type="text" name="lon" /></br>
    name: <input type="text" name="name" /></br>
    hours: <input type="text" name="hours" /></br>
	summary: <input type="text" name="summary" /></br>
    description: <input type="text" name="description" /></br>
	menu: <input type="text" name="menu" /></br>
    image: <input type="file" name="image" /></br>
    <input type="submit" value="Send" /><input type="reset">
    </form>
    
    </body>
    </html>
    '''

	
def food(req, landmarkID, UDID, lat, lon, name, hours, summary, description, menu, image):

		tableName = "Food"
		uploadFolder = "food"
		
		imageURL = imgUpload(image, uploadFolder)
		
		landmarkDict = {'name': name, 'latitude': lat, 'longitude': lon}
		layerDict = {'landmarkID': landmarkID, 'hours': hours, 'summary': summary, 'description': description, 'menu': menu, 'imageURL': imageURL}
			
		try:
			landmarkID = DBUpdate(tableName, layerDict, landmarkDict, UDID)
			return returnPage(tableName,landmarkID)
		except Exception, e:
			return 'Exception: %s' % (e)

	
#Code for Carleton layer
# (Replaced by generalLayer)

def carletonForm(req):
    
    return '''
    <html>
    <head><title>what the upload?</title></head>
    <body>
    
    <form method="POST" enctype="multipart/form-data" action="http://dev.gnar.us/post.py/carleton">
	Landmark ID: <input type="text" name="landmarkID" /></br>
	UDID: <input type="text" name="UDID" /></br>
    lat: <input type="text" name="lat" /></br>
    lng: <input type="text" name="lon" /></br>
    name: <input type="text" name="name" /></br>
	summary: <input type="text" name="summary" /></br>
    description: <input type="text" name="description" /></br>
	year built: <input type="text" name="yearBuilt" /></br>
    image: <input type="file" name="image" /></br>
    <input type="submit" />
    </form>
    
    </body>
    </html>
    '''

def carleton(req, landmarkID, UDID, lat, lon, name, summary, description, yearBuilt, image):
	
		tableName = "Carleton"
		uploadFolder = "carleton"
		
		imageURL = imgUpload(image, uploadFolder)
		
		landmarkDict = {'name': name, 'latitude': lat, 'longitude': lon}
		layerDict = {'landmarkID': landmarkID,'summary': summary, 'description': description, 'yearBuilt': yearBuilt, 'imageURL': imageURL}
			
		try:
			landmarkID = DBUpdate(tableName, layerDict, landmarkDict, UDID)
			return returnPage(tableName,landmarkID)
		except Exception, e:
			return 'Exception: %s' % (e)
			
# SportingArenas Layer
# (Replaced by generalLayer)
			
def sportingArenasForm(req):
    
    return '''
    <html>
    <head><title>what the upload?</title></head>
    <body>
    
    <form method="POST" enctype="multipart/form-data" action="http://dev.gnar.us/post.py/sportingArenas">
	Landmark ID: <input type="text" name="landmarkID" /></br>
	UDID: <input type="text" name="UDID" /></br>
    lat: <input type="text" name="lat" /></br>
    lng: <input type="text" name="lon" /></br>
    name: <input type="text" name="name" /></br>
	summary: <input type="text" name="summary" /></br>
    scheduleURL: <input type="text" name="scheduleURL" /></br>
	usedBy: <input type="text" name="usedBy" /></br>
    image: <input type="file" name="image" /></br>	
    <input type="submit" />
    </form>
    
    </body>
    </html>
    '''

def sportingArenas(req, landmarkID, UDID, lat, lon, name, summary, scheduleURL, usedBy, image):
		
		tableName = "SportingArenas"
		uploadFolder = "sportingArenas"
		
		imageURL = imgUpload(image, uploadFolder)
		
		landmarkDict = {'name': name, 'latitude': lat, 'longitude': lon}
		layerDict = {'landmarkID': landmarkID,'summary': summary, 'scheduleURL': scheduleURL, 'usedBy': usedBy, 'imageURL': imageURL}
			
		try:
			landmarkID = DBUpdate(tableName, layerDict, landmarkDict, UDID)
			return returnPage(tableName,landmarkID)
#			return "Upload Good"
		except Exception, e:
			return 'Exception: %s' % (e)			

# Generalized layer upload form
# This should have replaced all other layer upload forms.
# Other forms have been left just in case.

def generalLayerForm(req):
    
    return '''
    <html>
    <head><title>FoodForm</title></head>
    <body>
    
    <form method="POST" enctype="multipart/form-data" action="http://dev.gnar.us/post.py/generalLayer">
	LayerName: <input type="text" name="tableName" /></br>
	<form>
	UDID: <input type="text" name="UDID" /></br>
	<form>
	Layer uses an Image?: </br>
	<input type="radio" name="hasImage" value="True" /> Yes
	</br>
	<input type="radio" name="hasImage" value="False" /> No 
	</br>
	landmarkDict: </br>
	<textarea name="landmarkDict" COLS=80 ROWS=6></TEXTAREA></br>
	layerDict: </br>
	<textarea name="layerDict" COLS=80 ROWS=6></TEXTAREA></br>
    image: <input type="file" name="image" /></br>
    <input type="submit" value="Send" /><input type="reset">
    </form>
    
    </body>
    </html>
    '''
	
			
def generalLayer(req, tableName, hasImage, UDID, landmarkDict, layerDict, image = ""):
		
		try:
		
			if(type(hasImage) == str ):
				hasImage = (hasImage == "True")
			
			uploadFolder = tableName[0].lower()+tableName[1:]
		
			imageURL = imgUpload(image, uploadFolder)
		
			landmarkDict = json.loads(landmarkDict)
			layerDict = json.loads(layerDict)
			
			if(hasImage):
				layerDict["imageURL"]=imageURL
				
#			DBUpdate(tableName, layerDict, landmarkDict, UDID)
			
			landmarkID = DBUpdate(tableName, layerDict, landmarkDict, UDID)
			return returnPage(tableName,landmarkID)
#			return query
			#return imageLinkHTML(imageURL)
#			return "Upload Good"
#			return "LandmarkID Type: %s" % (type(layerDict['landmarkID']))
		except Exception, e:
			return 'Exception: %s LandmarkID Type: %s ' % (e, type(layerDict['landmarkID']))					

	
			
