#!/usr/bin/python
'''
Wade Gobel and Chris Peck
A sample function that takes layer-relevant information,
places it in a Python dictionary, and returns an appropriately
formatted JSON string representing that dictionary.
'''
import json

def dataToJSON(landmarkID, summaryString, imageURL, description, yearBuilt):
    return json.dumps({'ID': landmarkID, 'summary': summaryString,
                       'imageURL': imageURL, 'description': description,
                       'yearBuilt': yearBuilt})
