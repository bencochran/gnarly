"""
	serverFunctions.py
	
	Contents:
		A. Database Inserts and Updates 
				DBUpdate
				landmarkTableInsert
				voteDBUpdate
		B. MySQL Query Builders
				insertQueryBuilder
				updateQueryBuilder
		C. Getter Functions (Database Info) 
				getImageURL
				getUserNumber
		D. Database Record Existence Checks
				newRecordCheck
				checkForVote
		E. Image Storage Handling Functions  
				imgUpload
				imageUpdateHandler
				nullImgCheck
				checkImageLocation
				imgPathFromURL
		F. Output Formatters 
				imageLinkHTML
				returnPage
		G. Other
				getConnection
		H. Layer Information Functions (Work In Progress)
				layerInfoQuery
				processQuery

"""
import os
import sys
import MySQLdb
import glob
import time
import datetime
sys.path.append('/home/reldnahcire/nonPublicDir/') #put the database connection info somewhere.py
import dbConstants
import json

############################################################
#              A. Database Inserts and Updates             #
############################################################


"""
	Summary:	Inserts or updates the database when a new location is added also adds a vote for the update and insert. 
				Builds three different types of queries:
					1. Insert a new landmark and a new record into a specified layer table that uses the new landmark.
					2. Insert a new record into a specified layer table that uses an landmark that already exists.
					3. Update a record in a specified layer table the that already exists.
	Parameters:	tableName-String, name of the layer table to be updated.
				layerDict-A dictionary, contains an key-value pair for each field in the record to be updated/inserted.
							Keys are field names and values are entry data.
				landmarkDict-A dictionary, contains an key-value pair for each field in the landmarkTable record, aside from id, to be inserted.
								Takes the form: {'name': nameVar, 'latitude': latVar, 'longitude': lonVar}
								'name', 'latitude', and'longitude' are fields in the table.
								nameVar, latVar, and lonVar are strings holding the values to insert.
				UDID-String, device identifier of the device inserting/updating.
	Returns:	
	Issues: 	-Needs to be cleaned up and in-line commented
				-Maybe add an "all went well" return
				-Maybe return the imageURL from the database of the record. 
					This is because if you update a record without uploading a picture the "upload good" page links to the "no picture" picture.
				-The code that checks for and removes old images if the image is updated might need to be put in a seperate function.
	Note:		This is a mess here to allow for the code for each new layer added to be very simple and generic. This used to be three different
				functions. 
"""		
def DBUpdate(tableName, layerDict, landmarkDict, UDID):

	landmarkID = str(layerDict['landmarkID'])

	newRecord = newRecordCheck(tableName, "landmarkID", layerDict['landmarkID'])
	newLandmark = (landmarkID == "0")
	
	isOnlyVote = False
	
	
	if (newRecord and newLandmark):							# New record and new landmark
		newLandmarkID = landmarkTableInsert(landmarkDict)
		layerDict['landmarkID'] = newLandmarkID
		query = insertQueryBuilder(tableName, layerDict)
	
	elif(newRecord and (not newLandmark)):					# New record and existing landmark
		query = insertQueryBuilder(tableName, layerDict)
		
	elif(not newRecord): 									# Existing record and existing landmark
		layerDict = imageUpdateHandler(tableName, layerDict)
		query = updateQueryBuilder(tableName, layerDict)
		isOnlyVote = (len(layerDict)==1)
			
	database = getConnection()
	
	if(not isOnlyVote):
		database.query(query)
	
	
	voteDBUpdate(tableName, layerDict['landmarkID'], UDID)
	
	return layerDict['landmarkID']
#	return query

"""
	Summary:	Inserts a new record into the landmark table.
	Parameters:	landmarkDict-A dictionary, takes the form: {'name': nameVar, 'latitude': latVar, 'longitude': lonVar}
								'name', 'latitude', and'longitude' are fields in the table.
								nameVar, latVar, and lonVar are strings holding the values to insert.
	Returns:	A string containing the landmarkID of the new record.
	Issues: 	-The building of the query string can probabally be cleaned up some.
"""		
def landmarkTableInsert(landmarkDict):

	tableName = "landmarkTable"

	query = "INSERT INTO %s (" % tableName
	for key in landmarkDict.keys():
		cleanKey = MySQLdb.escape_string(key)
		query = query+cleanKey+", "
	query = query[0:-2]+") VALUES ("
	for value in landmarkDict.values():
		cleanValue = MySQLdb.escape_string(value)
		query = query+"\""+cleanValue+"\", "
	query = query[0:-2]+")"
	
	database = getConnection()
	database.query(query)
	
	newLandmarkID = database.insert_id()
	
	return str(newLandmarkID)

	
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

############################################################
#                B. MySQL Query Builders                   #
############################################################

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
		query = query+"\"%s\", "% (cleanValue)
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
	query = query[0:-2]+" WHERE landmarkID = \"%s\"" % MySQLdb.escape_string(layerDict['landmarkID'])
	
	return query



	
############################################################
#         C. Getter Functions (Database Info)              #
############################################################


"""
	Summary:	Retreives an imageURL from the database given a the name of the table and the landmarkID of
				the record.	
	Parameters:	layerName-The name of the table to query
				landmarkID-The landmarkID of the record we are looking for.
	Returns:	A string containing the URL of the image.
	Issues: 	-layerName is not a great name, should be tableName.
				-Will crash if the table does not have a field named imageURL
"""
def getImageURL(layerName, landmarkID):

	database = getConnection()
	
	imgURLQuery = "SELECT imageURL From %s WHERE landmarkID=%s" % (layerName, landmarkID)	
	database.query(imgURLQuery)
	
	result = database.store_result()
	
	imgURL = result.fetch_row()
	imgURL = imgURL[0][0]
	
	return imgURL

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

	
###########################################################
#          D. Database Record Existence Checks            #
###########################################################

"""
	Summary:	Checks see if a certain table contains one or more records with a certain field and value pair.
	Parameters:	table-A string, name of table to check.
				keyName-A string, name of field to check
				keyValue-A string, value to check in field
	Returns:	A boolean, true if there are any occurences of the value in the field in the table.
	Issues: 	
"""	
def newRecordCheck(table, keyName, keyValue):

	database = getConnection()
	countQuery = "SELECT COUNT(*) From %s WHERE %s=\"%s\"" % (table, keyName, keyValue)
	database.query(countQuery)
	countResult = database.store_result()
	valueCount = countResult.fetch_row()
	
	return (valueCount[0][0] == 0)

	
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

############################################################
#        E. Image Storage Handling Functions               #
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
				-Figure out what data type mod_python/apache is actually passing for imageUpload.
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
	
"""
	Summary:	Checks if the record being updated has an imageURL field. 
				If so, it checks if a newImage has been uploaded.
				If there is a newImage, it removes the old image from the server. 
				If is not a newImage it changes the update information so that old picture doesn't get overwritten in the database by the "no picture" URL. 
	Parameters:	tableName-String, name of the layer table to be updated.
				layerDict-A dictionary, contains an key-value pair for each field in the record to be updated/inserted.
							Keys are field names and values are entry data.
	Returns:	A dictionary of the updated layer data
	Issues: 	-Thinking about changing the way this works so the whole layerDict isn't passed only the URL
"""		
def imageUpdateHandler(tableName, layerDict):

	landmarkID = str(layerDict['landmarkID'])
	

	if ('imageURL' in layerDict):
		newImageURL = layerDict['imageURL']
		oldImageURL = getImageURL(tableName, landmarkID)
		isLocal = checkImageLocation(oldImageURL)
	else:
		return layerDict
		
	newImgNull = nullImgCheck(newImageURL)
	oldImgNull = nullImgCheck(oldImageURL)
	
	if (not newImgNull):
		if ((not oldImgNull) and isLocal):
			oldImagePath = imgPathFromURL(oldImageURL)
			os.remove(oldImagePath)
	else:
		layerDict['imageURL']=oldImageURL
		
		
	if (oldImageURL == None):
		del layerDict['imageURL']
			
	return layerDict


"""
	Summary:	Checks to see if the imageURL points to the "Null image" jpeg
	Parameters:	imageURL-The imageURL to check
	Returns:	True if imageURL points to the null image
	Issues: 	
"""		
def nullImgCheck(imageURL):

	nullImgURL = "http://dev.gnar.us/uploads/0.jpg"

	return ( imageURL == nullImgURL)
	
	
"""
	Summary:	Checks to see if an image url points to a local image. Neccessary for proper updating in the event 
				we have a nonlocal URL. Should not be an issue unless the url was put in the database by hand.
	Parameters:	imageURL-The imageURL to check
	Returns:	True if the isLocal is True
	Issues: 	-Logic can probably be cleaned up. 
"""			
def checkImageLocation(imageURL):
	if (type(imageURL)==str):
		localStringIndex= imageURL.find("http://dev.gnar.us/uploads")
		isLocal = (not (localStringIndex == -1))
	else:
		return False

	if(isLocal):
		return True
	else:
		return False
	
	
"""
	Summary:	Finds the local path to an image given the URL of an image stored locally.
	Parameters:	imageURL-The imageURL to build a path for.
	Returns:	A string of the path to the image.
	Issues: 	
"""	
def imgPathFromURL(imageURL):

	imageURL = imageURL.split("/")
	
	imgName= imageURL[-1]
	
	imgFolder = imageURL[-2]
	
	
	if (imgFolder != "uploads"):
		return "/var/www/uploads/%s/%s" % (imgFolder,imgName)
	else:
		return "/var/www/uploads/%s" % (imgName)		
		
	
############################################################
#             F. Output Formatters                         #
############################################################


"""
	Summary:	Used for testing to to generate a the html for the page displayed after an upload/update.
				The page contains a hyperlink to the URL passed in as imageURL.
	Parameters:	imageURL	- A string of the URL to link.
	Returns:	A string of the html for a page with a hyperlink to the URL passed in as imageURL.
	Issues: 	-Would be nice to make this page contain more info about the upload.
				-This has been supplanted by return page in the current iteration
"""	
def imageLinkHTML(imageURL):
	

	return '''
	<html><head>
	<title>Upload Good</title>
	</head>
	<body><a href="%s">Upload Good</a>
	</body>
	</html>''' % (imageURL)
	
def returnPage(tableName, landmarkID):

	database = getConnection()
	
	databaseCurs = database.cursor()
	
	
	query= "SELECT * From %s WHERE landmarkID=\"%s\"" % (tableName, landmarkID)
	databaseCurs.execute(query)
	descriptionTuple = databaseCurs.description
	
	database.query(query)
	result = database.store_result()
	result = result.fetch_row()
	
	newUploadDict = {}
	
	for i in range(len(descriptionTuple)):
		newUploadDict[descriptionTuple[i][0]]=result[0][i]
		
	returnVal = '''
	<html><head>
	<title>Upload Good</title>
	</head>
	<body><a href="%s">Upload Good</a></br>
	<p>
	'''%newUploadDict['imageURL']
	
	for key in newUploadDict.keys():
		returnVal+='''%s: %s</br>
		'''% (key, newUploadDict[key])
		
	returnVal+='''
	</body>
	</html>'''
	
	return returnVal
	
############################################################
#                       G. Other                           #
############################################################	
			
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
		

############################################################
#             H. Layer Information Functions               #
#                   (Work in progress)                     #
############################################################

# Will eventually return all info needed for the phone to make layers on the fly.
def layerInfoQuery():

	database = getConnection()
	
	query= "SELECT layerAndtableName, iconURL, fieldNames From layerInfo"
	result = processQuery(database,query)
	
	for layer in result:
		for item in layer:
			# if (item == 'fieldNames'):
				# layer['fieldNames']=json.loads(layer['fieldNames'])
			item = MySQLdb.escape_string(item)

	return result
	
#Will format the retun from layerInfoQuery into json to be sent to the phone.
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
