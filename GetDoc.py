# Name: Saif Abuosba 
# File Name: GetDoc.py

# Import libraries
import sys
import json

# Initialize variables for command line arguments
directoryPath = ""
idType = ""
id = ""

# Initialize variables for file names 
docFileName = ""
metadataFileName = ""

# Initialize dictionary for mapping between internal id and docno
idToDocNo = {}

try:
    # Check if 3 arguments have been provided (3 + filename) 
    if (len(sys.argv) == 4):

        directoryPath = str(sys.argv[1]) # Path to directory containing index files
        idType = str(sys.argv[2]) # 'docno' or 'id'
        id = str(sys.argv[3]) # value of docno or id
        
        # if id is provided get idToDocNo mapping and map to doc no 
        if (idType == 'id'):
            idToDocNoFile = open (directoryPath+'/idToDocNo.txt')
            idToDocNo = json.loads(idToDocNoFile.read())
            docFileName = idToDocNo[id] # set file name to mapped docNo
        
        # if docNo is provided, use docNo as file name 
        else:
            docFileName = id
        
        
        # Formulate metadata file name (DOCNO + '-metadata')
        metadataFileName = docFileName + '-metadata'

        # Define day, month and year for directory structure
        mm = docFileName[2:4]
        dd = docFileName[4:6]
        yy = docFileName[6:8]

        # Open document and metadata files 
        document = open (directoryPath+"/"+yy+"/"+mm+"/"+dd+"/"+docFileName+'.txt', "r")
        metadata = open (directoryPath+"/"+yy+"/"+mm+"/"+dd+"/"+metadataFileName+'.txt', "r")

        # Output the metadata
        for x in metadata:
            print (x, end="")

        print("raw document:")

        # Output the raw document
        for i in document:
            print(i, end="")

    # If the three are not provided, output message explaining what the program does
    else:
        print("\nThis program is designed to output the metadata and raw contents of a document " + 
          "provided 3 arguments in the command line.\n 1: path to the directory storing indexed files, "+
          "\n 2: the id type 'docno' or 'id', \n 3: value of integer id or DOCNO. \n\n" +
          "Please run program again with the appropriate arguments.\n")

# If the 3 arguments are not correct, request user to check arguments and rerun 
except:
    print("Error: Please verify that the arguments provided are valid and accurate! \n")
