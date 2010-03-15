import os
import sys
import MySQLdb
import glob
import time
import datetime
sys.path.append('/home/reldnahcire/nonPublicDir/') #put the database connection info somewhere.py
import dbConstants

class Upload:

	def __init__(self, tableName, hasImage, UDID, landmarkDict, layerDict, image):
		self.tableName = tableName
		self.uploadFolder = tableName[0].lower()+tableName[1:]
		if (type(hasImage) == str):
			self.hasImage = (hasImage=="True")
		else:
			self.hasImage = hasImage
		self.database = getConnection()
		self.landmarkDict = landmarkDict
		self.layerDict = layerDict
		self.image = image
		self.UDID = UDID
		self.landmarkID = str(layerDict['landmarkID'])
		
	def DBUpdate(self):
	
		if (self.hasImage):
			self.layerDict['imageURL'] = imgUpload(self.image, self.uploadFolder)
			returnPage = self.imageLinkHTML(self.layerDict['imageURL'])
		else:
			returnPage = self.noImageReturnPage()
			
		newRecord = self.checkForNewRecord()
		newLandmark = (self.landmarkID=="0")
		
		if(newRecord and newLandmark):
			newLandmarkID = landmarkTableInsert(self.landmarkDict, self.database)
			self.layerDict['landmarkID'] = newLandmarkID
			query = insertQueryBuilder(self.tableName, self.layerDict)
		elif(newRecord and (not newLandmark)):
			query = insertQueryBuilder(self.tableName, self.layerDict)
		elif(not newRecord):
			if(self.hasImage):
				returnPage = self.imageReplacement(self.layerDict['imageURL'])
			query = updateQueryBuilder(self.tableName, self.layerDict)
			
		self.database.query(query)
	
		voteDBUpdate(self.tableName, self.landmarkID, self.UDID)
		
		return returnPage
		
	def checkForNewRecord(self):
		
		countQuery = "SELECT COUNT(*) From %s WHERE landmarkID=\"%s\"" % (self.tableName, self.landmarkID)
		self.database.query(countQuery)
		countResult = self.database.store_result()
		valueCount = countResult.fetch_row()
	
		return (valueCount[0][0] == 0)
		
	def imageReplacement(self, newImageURL): 

		oldImageURL = self.getImageURL(self.tableName, self.landmarkID)
		newImgNull = nullImgCheck(newImageURL)
		
		if (newImageNull):	
			del self.layerDict['imageURL']
			return imageLinkHTML(oldImageURL)
		else:
			oldImgNull = nullImgCheck(oldImageURL)
			if (not oldImgNull):
				oldImagePath = imgPathFromURL(oldImageURL)
				os.remove(oldImagePath)
			return self.imageLinkHTML(newImageURL)
	
	def getImageURL(self):
	
		imgURLQuery = "SELECT imageURL From %s WHERE landmarkID=%s" % (self.tableName, self.landmarkID)	
		self.database.query(imgURLQuery)
	
		result = self.database.store_result()
	
		imgURL = result.fetch_row()
		imgURL = imgURL[0][0]
	
		return imgURL
		
	def imageLinkHTML(self, imageURL):
	

		return '''
		<html><head>
		<title>Upload Good</title>
		</head>
		<body><a href="%s">Upload Good</a>
		</body>
		</html>''' % (imageURL)
	
	def noImageReturnPage(self):
		
		return '''
		<html><head>
		<title>Upload Good</title>
		</head>
		<body><h1>Upload Good</h1></a>
		</body>
		</html>'''
		
def landmarkTableInsert(landmarkDict, database):
	
		query = "INSERT INTO landmarkTable ("
		for key in landmarkDict.keys():
			cleanKey = MySQLdb.escape_string(key)
			query = query+cleanKey+", "
		query = query[0:-2]+") VALUES ("
		for value in landmarkDict.values():
			cleanValue = MySQLdb.escape_string(value)
			query = query+"\""+cleanValue+"\", "
		query = query[0:-2]+")"
	
		database.query(query)
	
		newLandmarkID = database.insert_id()
	
		return str(newLandmarkID)
		
				
	# def imageUpload():
	
		# uploadFolder = tableName[0].lower()+tableName[1:]
		
		# if(type(imageUpload)!=str):
	
			# try:
				# uploadPathName = '/var/www/uploads/%s' % (uploadType)
				
				# image = image.file
				# now = datetime.datetime.now()
				# timeString = now.strftime("%Y-%m-%d-%H%M%S")
				
				# imagename = '%s.jpg' % (timeString)
			
				# fout = file(os.path.join(uploadPathName, imagename), 'wb')
				# while True:
					# chunk = image.read()
					# if not chunk: break
					# fout.write(chunk)
				# fout.close
				
				# layerDict['imageURL'] = '''http://dev.gnar.us/uploads/%s/%s''' % (uploadType, imagename)
			
			# except Exception, e:
				# return 'Exception: %s' % (e)
	
		# else:
			# layerDict['imageURL'] = '''http://dev.gnar.us/uploads/0.jpg'''

	

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
		

"""
	Summary:	Retreives a userNumber from the database given a UDID. If
				the UDID does not exist in the userTable it creates a new record.
	Parameters:	UDID-A string of the UDID for a phone.
	Returns:	A string of the userNumber for that UDID.
	Issues: 	-Might want to seperate into two functions add and get.
"""		
def getUserNumber(UDID):

	UDID = MySQLdb.escape_string(UDID)
	
	database = getConnection()
	
	userIDCountQuery = "SELECT COUNT(*) From userTable WHERE udid=\"%s\"" % (UDID)
	database.query(userIDCountQuery)
	countResult = database.store_result()
	userIDCount = countResult.fetch_row()
	
	if(userIDCount[0][0] == 0):
		
		insertUserQuery = "INSERT INTO userTable (udid) VALUES (\"%s\")" % UDID
		database.query(insertUserQuery)
		
	userIDQuery = "SELECT id From userTable WHERE udid=\"%s\"" % (UDID)
	database.query(userIDQuery)
	idResult = database.store_result()
	userID = idResult.fetch_row()
	userID = userID[0][0]
	return userID




"""
	Deprecated Remove after robustness of new DBUpdate is tested. (2/22/2010)
	
	Summary:	Checks to see if an image url matches the "no image" image.
	Parameters:	imageURL	- A string, the URL of the image.
	Returns:	A boolean, false for a match to the no image, true for all others.
	Issues: 	-Maybe rename checking for a new image is what it is used for, but not what it does.
				-Only used twice, only a seperate function because DBUpdate is really messy already
				-Maybe expand to do all the new image handling needed in DBUpdate.
				
"""	
def newImageCheck(imageURL):
	
	return (not imageURL == "http://dev.gnar.us/uploads/0.jpg")
	
def nullImgCheck(imageURL):

	nullImgURL = "http://dev.gnar.us/uploads/0.jpg"

	return ( imageURL == nullImgURL)

"""
	Summary:	Checks see if a certain table contains one or more records with a certain field and value pair.
	Parameters:	table-A string, name of table to check.
				keyName-A string, name of field to check
				keyValue-A string, value to check in field
	Returns:	A boolean, true if there are any occurences of the value in the field in the table.
	Issues: 	
"""	
def checkForExistence(table, keyName, keyValue):

	database = getConnection()
	countQuery = "SELECT COUNT(*) From %s WHERE %s=\"%s\"" % (table, keyName, keyValue)
	database.query(countQuery)
	countResult = database.store_result()
	valueCount = countResult.fetch_row()
	
	return (valueCount[0][0] > 0)

	
"""
	Summary:	Checks see if a user has already voted for a given landmark.
	Parameters:	tableName-A string, name of vote table to check.
				LandmarkID-A string, landmarkID to check.
				userNumber-A string, userID to check.
	Returns:	A boolean, true if there the user has already voted for record associated with the landmarkID.
	Issues: 	-Kind of just a special case of check for existence maybe should be combined
				-Perhaps make tableName be the table associated with the vote table
"""	
def checkForVote(tableName, landmarkID, userNumber):

	database = getConnection()
	countQuery = "SELECT COUNT(*) From %s WHERE landmarkID=\"%s\" AND userID=\"%s\"" % (tableName, landmarkID, userNumber)
	database.query(countQuery)
	countResult = database.store_result()
	valueCount = countResult.fetch_row()
	
	return (valueCount[0][0] > 0)

	
"""
	Summary:	Inserts a new vote into a vote table.
	Parameters:	layerName-String, table name corresponding to the vote table to update.
				landmarkID-String, landmarkID of the record being voted for.
				UDID-String, device identifier of the device voting.
	Returns:	
	Issues: 	-Might want to have it return something to say "Hey this worked!"
"""		
def voteDBUpdate(layerName, landmarkID, UDID):


	layerName = layerName+"Votes"
	
	userNumber = getUserNumber(UDID)
	
	layerName = MySQLdb.escape_string(layerName)
	landmarkID = MySQLdb.escape_string(landmarkID)
	
	voteAlreadyExists = checkForVote(layerName, landmarkID, userNumber)
	
	if (not voteAlreadyExists):
	
		database = getConnection()
		
		voteQuery = "INSERT INTO %s (userID, landmarkID) VALUES (\"%s\",\"%s\")" % (layerName, userNumber, landmarkID)
		database.query(voteQuery)

	

	
def imgPathFromURL(imageURL):

	imageURL = imageURL.split("/")
	
	imgName= imageURL[-1]
	
	imgFolder = imageURL[-2]
	
	
	if (imgFolder != "uploads"):
		return "/var/www/uploads/%s/%s" % (imgFolder,imgName)
	else:
		return "/var/www/uploads/%s" % (imgName)
	
	
"""
	Summary:	Builds the query to insert new record into a table.
	Parameters:	tableName-String, name of the layer table that is the target of the insert.
				layerDict-A dictionary, contains an key-value pair for each field in the record to be inserted.
							Keys are field names and values are entry data.
	Returns:	The query as a string.
	Issues: 	-Change so string slicing is not needed. (If that makes it cleaner.)
"""	
def insertQueryBuilder(tableName, layerDict):

	query = "INSERT INTO %s (" % tableName
	for key in layerDict.keys():
		cleanKey = MySQLdb.escape_string(key)
		query = query+cleanKey+", "
	query = query[0:-2]+") VALUES ("
	for value in layerDict.values():
		cleanValue = MySQLdb.escape_string(value)
		query = query+"\""+cleanValue+"\", "
	query = query[0:-2]+")"
	
	return query

	
"""
	Summary:	Builds the query to update an existing record.
	Parameters:	tableName-String, name of the layer table to be updated.
				layerDict-A dictionary, contains an key-value pair for each field in the record to be inserted.
							Keys are field names and values are entry data.
	Returns:	The query as a string.
	Issues: 	-Change so string slicing is not needed. (If that makes it cleaner.)
"""	
def updateQueryBuilder(tableName, layerDict):

	query = "UPDATE %s SET " % tableName
	for key in layerDict.keys():
		if (key != "landmarkID"):
			cleanKey = MySQLdb.escape_string(key)
			cleanValue = MySQLdb.escape_string(layerDict[key])
			query = query+key+"=\"%s\", " % cleanValue
	query = query[0:-2]+" WHERE landmarkID = %s;" % MySQLdb.escape_string(layerDict['landmarkID'])
	
	return query
	
	
############################################################
#             E. Other Upload Functions                    #
############################################################		
		
	
"""
	Summary:	Function handles image uploading to the server. 
				Uploaded images are renamed with the time and date they were uploaded.
				Example: 2010-02-21-182922.jpg = image uploaded Feb. 21, 2010 at 6:29:22PM
	Parameters:	imageUpload-The image file passed in from apache on http post.
				uploadType-	The name of the folder to which the image is to be uploaded.
							The folder name coresponds to the layer/table name, but with a lowercase first letter.
	Return:		Returns the URL of the uploaded image. 
				If no image is uploaded it returns the URL of the "No Image" image		
	Issues: 	-Rework server so that the folders and layers/table names are identical
				-Figure out what type mod_python/apache is actually passing for imageUpload.
"""
def imgUpload(imageUpload, uploadType):

	
		if(type(imageUpload)!=str):
		
			try:
				uploadPathName = '/var/www/uploads/%s' % (uploadType)
				
				image = imageUpload.file
				now = datetime.datetime.now()
				timeString = now.strftime("%Y-%m-%d-%H%M%S")
				
				imagename = '%s.jpg' % (timeString)
			
				fout = file(os.path.join(uploadPathName, imagename), 'wb')
				while True:
					chunk = image.read()
					if not chunk: break
					fout.write(chunk)
				fout.close
				
				return '''http://dev.gnar.us/uploads/%s/%s''' % (uploadType, imagename)
				
			except Exception, e:
				return 'Exception: %s' % (e)
		else:
			return '''http://dev.gnar.us/uploads/0.jpg'''
