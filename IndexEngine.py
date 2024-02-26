# Name: Saif Abuosba 
# File Name: IndexEngine.py

# Import libraries
import gzip
import sys
import os
import xml.etree.ElementTree as ET
import calendar
import json
import PorterStemmer

# Initialize stemmer
ps = PorterStemmer.PorterStemmer()

# Function to index the file
def index(file):
    
    # Initialize variables for document and id
    doc = ""
    id = 0

    # Open file and read line by line
    with gzip.open(file,'rt') as documents:
        # For each line in the file loop through the lines and form documents
        for line in documents:
            doc += line # Add line to doc
            # If end of document is reached, extract metadata and save document
            if (line.strip() == "</DOC>"): 
                extractMetaDataAndSave(doc, id)
                buildRevesreIndex(doc, id)
                # Reset doc
                doc = ""
                # Increment id
                id += 1
                
                

# Function to extract metadata and save document and metadata to files
# takes in document of type String and an integer id assigned to document 
def extractMetaDataAndSave(doc, id):
   
    # Parse XML document
    parsedXML = ET.fromstring(doc)

    # Initialize variables for metadata
    headlineText = ""
    date = ""
    
    # Define variables for id and docno
    internalID = id
    docNo = parsedXML.find('DOCNO').text.strip()

    # Add id and docNo to dictionaries for later mapping
    idToDocNo[internalID] = docNo
    docNoToId[docNo] = internalID
    
    # Define day, month and year for directory structure
    mm = docNo[2:4]
    dd = docNo[4:6]
    yy = docNo[6:8]

    # Extract headline from parsed XML
    try:
        headlineTag = parsedXML.find('HEADLINE').findall('P')
        for p in headlineTag:
            headlineText = headlineText + ' ' + p.text.strip()
        
    except:
        headlineText = "N/A"

        
    # Formulate date for metadata file based on encoded date in DOCNO
    date = calendar.month_name[int(mm)] + ' ' + str(int(dd)) + ', 19' + yy 

    # Create year directory if it does not exist already
    if not os.path.exists(directoryPath+"/"+yy):
        os.mkdir(directoryPath+"/"+yy)

    # Create month directory if it does not exist already
    if not os.path.exists(directoryPath+"/"+yy+"/"+mm):
        os.mkdir(directoryPath+"/"+yy+"/"+mm)

    # Create day directory if it does not exist already
    if not os.path.exists(directoryPath+"/"+yy+"/"+mm+"/"+dd):
        os.mkdir(directoryPath+"/"+yy+"/"+mm+"/"+dd)

    # Write document to file in the appropriate directory
    documentWriter = open(directoryPath+"/"+yy+"/"+mm+"/"+dd+"/"+docNo+'.txt', "w")
    documentWriter.write(doc)
    documentWriter.close()

    # Write metadata to a separate metadata file in the appropriate directory
    metadataWriter = open(directoryPath+"/"+yy+"/"+mm+"/"+dd+"/"+docNo+'-metadata.txt', "w")
    metadataWriter.write("docno: " + docNo + "\n")
    metadataWriter.write("internal id: " + str(internalID) + "\n")  
    metadataWriter.write("date: " + date + "\n")
    metadataWriter.write("headline: " + headlineText + "\n")
    metadataWriter.close()

   

def buildRevesreIndex(doc, docID):

    # Parse XML document
    parsedXML = ET.fromstring(doc)

    # Initialize variables for tokenizing
    headlineText = "" 
    graphicText = ""
    text = ""

    # Extract headline from parsed XML
    try:
        headlineTag = parsedXML.find('HEADLINE').findall('P')
        for p in headlineTag:
            headlineText = headlineText + ' ' + p.text.strip()
    
    # No HEADLINE tag     
    except:
        headlineText = ""

    # Extract graphic text from parsed XML
    try:
        graphicTag = parsedXML.find('GRAPHIC').findall('P')
        for p in graphicTag:
            graphicText = graphicText + ' ' + p.text.strip()
    
    # No GRAPHIC tag    
    except:
        graphicText = ""

    # Extract text from textTag from parsed XML
    try:
        textTag = parsedXML.find('TEXT').findall('P')
        for p in textTag:
            text = text + ' ' + p.text.strip()

    # No TEXT tag    
    except:
        text = ""

    
    # Concatenate all retrieved text from document
    textToTokenize = headlineText + " " + graphicText + " " + text

    # Send text to tokenizer 
    tokens = tokenize(textToTokenize, stem)
    
    # Convert tokens to term IDs
    tokenIDs = convertTokensToIDs(tokens, lexicon)
    
    # Determine counts for each term in document 
    wordCounts = countWords(tokenIDs) 
    
    # add the counts to approriate postings list 
    addToPostings (wordCounts, docID)

    # add the doc length of current document to docLength list
    docLength.append(len(tokens))


# Write lexicon to txt file 
def storeLexicon(): 
    
    lexiconWriter = open(directoryPath+"/lexicon.txt", "w")
    lexiconWriter.write(json.dumps(lexicon))
    lexiconWriter.close()

# Write inverted index to txt file 
def storeInvertedIndex(): 
    
    invertedIndexWriter = open(directoryPath+"/inv-index.txt", "w")
    invertedIndexWriter.write(json.dumps(inverseIndex))
    invertedIndexWriter.close()

# method to add counts of terms to appropriate postings list 
def addToPostings (wordCounts, docID):

    # loop through term ids in wordcounts 
    for termID in wordCounts:

        # capture the count for current term id 
        count = wordCounts[termID]

        # create a postings list if one does not already exist
        if (termID not in inverseIndex):
            inverseIndex[termID] = []
        
        # Get postings list
        postings = inverseIndex[termID]
        
        # add the doc id 
        postings.append(docID)
        
        # add the count for the term in current doc 
        postings.append(count)

# Takes list of tokenIDs and 
# returns a dictionary of termIDs as key and counts as values
def countWords(tokenIDs):
    
    # Define dictonary for word counts 
    wordCounts = {}

    # Loop through tokenIDs 
    for id in tokenIDs:
        
        # if the id has already been seen, add one to count
        if id in wordCounts:
            wordCounts[id] += 1
        
        # otherwise add the if and assign a count of one 
        else:
            wordCounts[id] = 1
    
    return wordCounts

# Tokenizer that takes a query and returns a list of terms/tokens 
def tokenize (textToTokenize, stem):

    # Lowercase all characters in text 
    textToTokenize = textToTokenize.lower()

    # define list to store tokens  
    tokens = []

    # create pointers to determine start and end of a token 
    start = 0
    pointer = 0

    # loop through text
    for i in range (0, len(textToTokenize)):
        
        # capture the current character 
        c = textToTokenize[i]
        
        # check if character is alphanumaric 
        if not c.isalnum():
            # if it is not alpahnumaric, check if we are building a token
            if start != i:
                # capture token 
                token = textToTokenize[start:i]
                
                if (stem == 1):
                    tokens.append(ps.stem(token,0, len(token)-1))

                else:
                    tokens.append(token) 

            # no start of token identified 
            start = i+1

        # Move to next character       
        pointer += 1
    
    # Capture the very last token (if applicable)
    if (start != pointer):
        token = textToTokenize[start:pointer]
        
        # Stem token if stem is enabled
        if (stem == 1):
            tokens.append(ps.stem(token,0, len(token)-1))

        # Otherwise add token as is
        else:
            tokens.append(token) 


    return tokens

# Writes current doc length to file 
def storeDocLength ():
    # Append docLength to file
    docLengthWriter = open(directoryPath+"/doc-lengths.txt", "a")
    for i in docLength:
        docLengthWriter.write(str(i) + '\n')
    docLengthWriter.close()

# This method takes a list of tokens and returns a list of term IDs
def convertTokensToIDs(tokens, lexicon):
    tokenIDs = []

    for token in tokens:
        if token in lexicon.keys():
            tokenIDs.append(lexicon[token])
        
        # assign an id and adds term to id mapping to lexicon if it does not already exist
        else:
            termID = len(lexicon)
            lexicon[token] = termID 
            tokenIDs.append(lexicon[token])

    return tokenIDs



# ******************* Main *****************************

# Check if 3 arguments have been provided (3 + filename) 
if (len(sys.argv) == 4):
        
    # Define dictionaries for mapping between internal id and docno
    idToDocNo = {}
    docNoToId = {}
    
    # Define dicitonaries for lexicon and inverted index
    lexicon = {}
    inverseIndex = {}

    # Define list for doc lengths 
    docLength = []

    # Define file paths from command line arguments
    filePath = str(sys.argv[1])
    directoryPath = str(sys.argv[2])

    stem = int(sys.argv[3])

    # Check if output directory exists and create it if it does not
    if not os.path.exists(directoryPath):
        if stem == 0 or stem == 1:
            os.mkdir(directoryPath)
                
            # Call index function with path to latimes.gz file
            index(filePath)

            # Write idToDocNo dictionary to file
            idToDocNoWriter = open(directoryPath+"/idToDocNo.txt", "w")
            idToDocNoWriter.write(json.dumps(idToDocNo))
            idToDocNoWriter.close()

            # Write docNoToId dictionary to file
            docNOToIDWriter = open(directoryPath+"/docNoToId.txt", "w")
            docNOToIDWriter.write(json.dumps(docNoToId))
            docNOToIDWriter.close()

            # Save lexicon to txt file in output path 
            storeLexicon()
            # Save inverted index to file in output path
            storeInvertedIndex()
            # Save the doc lengths to txt file in output path
            storeDocLength()

            print("Indexing complete!")

        else:
            print("Error: Specify last argument as 0 to disable stemming or 1 to enable stemming.")

    # If output directory already exists, print error message
    else:
        print("Error: Output directory already exists! Delete and try again.")

# If less than or more than 2 arguments are provided, show program description             
else:
    print("\nThis program is designed to index the latimes.gz file. " +
            "It will store each document in a separate txt file and metadata " +
            "such as the HEADLINE, DATE, and DOCNO are stored in a separate txt file as well." + 
            "\nThe files are stored in a directory hierarchy, in a YY --> MM --> DD folder structure. " + 
            "It will also tokenize text in the TEXT, GRAPHIC and HEADLINE tags creating a lexicon and inverted index. \n" +
            "The program requires 3 arguments to be provided through the command line:\n\n" +
            "1: Path to the latimes.gz file.\n" +
            "2: Path to where you want the indexed files to be stored. (ensure folder is not already created) \n"+
            "3: 0 or 1 argument: 0 to disable stemming or 1 to enable stemming\n\n" +
            "Please run program again with the appropriate arguments.\n")


