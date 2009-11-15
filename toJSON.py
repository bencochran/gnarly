#!/usr/bin/python
'''
Wade Gobel and Chris Peck
'''
import json

def dataToJSON(landmarkID, summaryString, imageURL, description, yearBuilt):
    return json.dumps({'ID': landmarkID, 'summary': summaryString,
                       'imageURL': imageURL, 'description': description,
                       'yearBuilt': yearBuilt})
