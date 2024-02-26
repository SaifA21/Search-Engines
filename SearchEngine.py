# Name: Saif Abuosba 
# File Name: SearchEngine.py

# import libraries
import math 
import json
import os
import sys
import re 
import time 

# Read lexicon into memory and return as a dictionary
def constructLexicon (directoryPath):
    lexiconFile = open (directoryPath+"/lexicon.txt")
    lexicon = json.loads(lexiconFile.read())
    return lexicon

# Read inverted index into memory and return as a dictionary
def contructInverseIndex (directoryPath):
    invIndexFile = open (directoryPath+"/inv-index.txt")
    inverseIndex = json.loads(invIndexFile.read())
    return inverseIndex


# reads qury file and returns contents in a list 
# one index for query number and another for query 
def indexQueries(queriesPath):
    queriesList = []
    queries = open(queriesPath, "r")

    for line in queries:
        queriesList.append(str(line))
        
    return (queriesList)


# reads doc-length file and returns average docLength, 
# total number of docs and a list of the docLengths
def indexDocLengths(docLengthFilePath):
    sum = 0
    count = 0 
    lengthList = []
    
    lengths = open(docLengthFilePath, "r")

    for length in lengths:
        sum += int(length)
        count += 1
        lengthList.append(length.strip())
        
    return (sum/count), count, lengthList



# Tokenizer that takes a query and returns a list of terms/tokens 
def tokenize (query):

    # Lowercase the query 
    query = query.lower()

    # define list to store tokens  
    tokens = []
    
    # create pointers to determine start and end of a token 
    start = 0
    pointer = 0
    
    # loop through query 
    for i in range (0, len(query)):
        
        # capture the current character 
        c = query[i]
        
        # check if character is alphanumaric 
        if not c.isalnum():
            # if it is not alpahnumaric, check if we are building a token
            if start != i:
                # capture token 
                token = query[start:i] 
                    
                if (token in lexicon.keys()):
                    # if it is add to list, otherwise omit from query 
                    tokens.append(token)
                       
           
            # no start of token identified 
            start = i+1
        
        # Move to next character       
        pointer += 1
    
    # Capture the very last token (if applicable)
    if (start != pointer):
        token = query[start:pointer]
                    
        if (token in lexicon.keys()):
            # if it is add to list, otherwise omit from query 
            tokens.append(token)


    return tokens


# Method to compute K score for a given docID
def computeK (docLength, averageDocLength, k1, b):
    k = k1 * (1-b) + b * (docLength/averageDocLength)
    return k 

# Method to compute partial BM25 score for a given docID
def computePartialBM25Score (k, fi, N, ni):
    return fi/(k+fi) * math.log((N-ni+0.5)/(ni+0.5))


def getDoc(userInput, rankToDocNo, directoryPath):
    
    docFileName = rankToDocNo[userInput]
    #metadataFileName = docFileName + '-metadata'
                
    mm = docFileName[2:4]
    dd = docFileName[4:6]
    yy = docFileName[6:8]

    document = open (directoryPath+"/"+yy+"/"+mm+"/"+dd+"/"+docFileName+'.txt', "r")

    print(document.read())


# Method to extract text from a given document
def extractText(docno, directoryPath):
    # Extract filepath from docno
    mm = docno[2:4]
    dd = docno[4:6]
    yy = docno[6:8]

    # Open document and read contents
    document = open (directoryPath+"/"+yy+"/"+mm+"/"+dd+"/"+docno+'.txt', "r")

    # Define text variable to store text
    text = ''
    # Define boolean to determine if we should add text to text variable
    add = False
    
    # Loop through each line in the document
    for line in document:
        
        # Check if we should add the line to the text variable
        if (line.strip() == "<GRAPHIC>" or line.strip() == "<TEXT>"):
            add = True

        # Check if we should stop adding lines to the text variable
        if (line.strip() == "</GRAPHIC>" or line.strip() == "</TEXT>"):
            add = True

        # If we should add the line to the text variable, add it
        if (add):
            text += " " + line  

    # Remove HTML tags from text
    cleanText = re.sub('<.*?>', '', text).strip().replace('\n', '')


    return (cleanText)


# Method to create sentences from a given text
def createSentences (text):
    
    # define list to store sentences  
    sentences = []
    
    # create pointers to determine start and end of a sentence 
    start = 0
    pointer = 0
    
    # loop through text 
    for i in range (0, len(text)):
        
        # capture the current character 
        c = text[i]
        
        # check if character is ! or ? or . 
        if c in ['!', '?', '.']:
            
            # if it is not alpahnumaric, check if we are building a sentence
            if start != i:
                
                # capture sentence  
                sentence = text[start:i+1] 
                sentences.append(sentence.strip())
                       
            # no start of sentence identified 
            start = i+1
        
        # Move to next character       
        pointer += 1
    
    # Capture the very last sentnece (if applicable)
    if (start != pointer):
        sentence = text[start:pointer+1]
        sentences.append(sentence.strip())

    return (sentences)


# Method to score a given sentence
def scoreSentence(tokenizedSentence, tokenizedQuery, position):

    # Initialize variables 
    l = 0
    c = 0
    d = 0
    k = 0

    # Define list to store distinct terms
    distinct = []

    # Define variable to store contiguous count
    contiguous = 0


    # Compute l score
    if position == 0:
        l = 2
    if position == 1:
        l = 1


    # Compute c, d, and k scores
    for word in tokenizedSentence:
        
        # Compute c score and contiguous count
        if word in tokenizedQuery:
            c += 1
            contiguous += 1
            
            # Check if contiguous count is greater than k
            if contiguous > k:
                k = contiguous
        
        # Reset contiguous count
        else:
            contiguous = 0


        # Compute d score
        if word in tokenizedQuery and word not in distinct:
            distinct.append(word)
            d += 1

    # Compute result score
    v = l + c + d + k

    # Return result score
    return (v)



# Method to create a summary for a given document and query
def createSummary(docno, tokenizedQuery, directoryPath):

    # Extract text from document    
    text = extractText(docno, directoryPath)
    
    # Create sentences from text
    sentences = createSentences(text)

    # List to store tokenized sentences
    tokenizedSentences = []

    # Loop through sentences and tokenize
    for sentence in sentences:
        tokenizedSentences.append(tokenize(sentence))

    # Define dictionary to store scored sentences
    scoredSentences = {}
    
    # Initialize index
    index = 0
    
    # Loop through tokenized sentences and score
    for sentence in tokenizedSentences:
        # Score sentence
        score = scoreSentence(sentence, tokenizedQuery, index)
        # Add score to dictionary
        scoredSentences[index] = score
        # Increment index
        index += 1

    # Sort scored sentences in descending order
    sortedScores = dict(sorted(scoredSentences.items(), key=lambda item: item[1], reverse=True))

    # Define summary variable
    summary = ''
    
    # Initialize counter
    counter = 0 

    # Loop through sorted scores and add to summary
    for index in sortedScores:
        
        # Add sentence to summary
        summary += sentences[index] + " "
        # Increment counter
        counter += 1
        
        # Check if we have added 3 sentences
        if (counter == 3):
            break
    
    # Return summary
    return (summary)


# Method to retrieve headline and date for a given docno
def getHeadlineDate(docno):
    
    # Define metadata file name
    metadataFileName = docno + '-metadata'

    # Extract filepath from docno
    mm = docno[2:4]
    dd = docno[4:6]
    yy = docno[6:8]

    # Open metadata file and read contents
    metadata = open (directoryPath+"/"+yy+"/"+mm+"/"+dd+"/"+metadataFileName+'.txt', "r")
    lines = metadata.readlines()
    
    # Extract headline and date
    headline = lines[3]
    date = lines[2][6:]

    # Return headline and date
    return headline, date




# /////////////////////////// MAIN /////////////////////////////////////////

# Check if 3 arguments have been provided (filename + 3 arguments) 
if (len(sys.argv) == 2):
        
    # Define dictionaries for mapping between internal id and docno
    idToDocNo = {}
    docNoToId = {}

    # Define dicitonaries for lexicon and inverted index
    lexicon = {}
    inverseIndex = {}

    # Define lists for doc lengths and output of results 
    docLength = []
    outputList = []

    # Define file paths from command line arguments
    directoryPath = str(sys.argv[1])

    # Check if output file exists
    if os.path.exists(directoryPath):
        
        # Construct the lexicon and inverseIndex
        lexicon = constructLexicon(directoryPath)
        inverseIndex = contructInverseIndex(directoryPath)
        
        # Contruct id to docno mapping
        idToDocNoFile = open (directoryPath+'/idToDocNo.txt')
        idToDocNo = json.loads(idToDocNoFile.read())

        # Retrieve average doc length, number of docs and list of doc lengths from doc-lengths.txt
        averageDocLength, numberOfDocs, listOfLengths = indexDocLengths(directoryPath+'/doc-lengths.txt')
        
        # While loop to allow user to enter queries
        while True:
            
            # Prompt user for query
            userInput = input("Please enter a query or 'q' to quit: ")

            # Check if user wants to quit
            if userInput == 'q':
                exit()

            # Start timer
            start = time.time()

            # Tokenize query
            tokenizedQuery = tokenize(userInput)

            # Store associated id for each term by retrieving from lexicon
            termIDs = []

            # Define dictionary for BM25 scores
            BM25Scores = {}

            # Define list for termIDs
            termIDs = []
                                
            # Store associated id for each term by retrieving from lexicon 
            for token in tokenizedQuery:
                termIDs.append(lexicon[token])

            # Define list for result
            result = []

            # Loop through each term in the query
            for termID in termIDs:
                
                # Retrieve posting list for term
                postingList = inverseIndex[str(termID)]
                
                # Loop through posting list and add docIDs to result list
                for x in range (0,len(postingList), 2):
                    
                    # Store docID and count
                    docID = postingList[x]
                    count = postingList[x+1]

                    # Compute K score for docID
                    k = computeK(float(listOfLengths[docID]), averageDocLength, 1.2, 0.75)

                    # Compute partial BM25 score for docID and add to BM25Scores dictionary
                    if docID in BM25Scores.keys():
                        BM25Scores[docID] += computePartialBM25Score(k, count, numberOfDocs, len(postingList)/2)
                    else:
                        BM25Scores[docID] = computePartialBM25Score(k, count, numberOfDocs, len(postingList)/2)
        
            # Sort BM25 scores in descending order
            sortedBM25Scores = dict(sorted(BM25Scores.items(), key=lambda item: item[1], reverse=True))
            
            # Intialize counter and runTag
            counter = 1

            # Define dictionary to map rank to docno
            rankToDocNo = {}
            

            # Loop through sorted BM25 scores and add to output list
            for doc in sortedBM25Scores:

                # Retrieve docno from idToDocNo dictionary
                docno = idToDocNo[str(doc)]

                # Retrieve headline and date for docno
                headline, date = getHeadlineDate(docno)
                
                # Map rank to docno
                rankToDocNo[str(counter)] = docno

                # Create summary
                summary = createSummary(docno, tokenizedQuery, directoryPath)

                # Check if headline is N/A
                if (headline.strip() == "headline: N/A"):
                    # If it is, use first 50 characters of summary
                    headline = summary[0:50] + ("...")
                
                # Otherwise, remove "headline: " from headline
                else:
                    headline = headline[9:]


                print()

                # Print result
                print (str(counter) + ". " + headline.strip() + " (" + date.strip() + ") \n" +
                       summary + " (" + idToDocNo[str(doc)] + ") \n" )
                
                # Increment counter
                counter += 1
    
                # Check if we have printed 10 results
                if (counter == 11):
                    break

            
            # End timer
            end = time.time()

            # Print time taken to retrieve results
            print('Retrieval took: ' + str(round(end-start,2)) + ' seconds.')
            

            # While loop to allow user to view documents
            while True:
                
                # Prompt user for input
                userInput = input("Enter doc rank number to view the document, enter 'n' to enter a new query, or enter 'q' to quit the program: ")
                
                # Check if user wants to virw one of the 10 results
                if(userInput in ['1','2','3','4','5','6','7','8','9','10']):

                    # Retrieve and print document
                    getDoc(userInput, rankToDocNo, directoryPath)

                # check if user wants to quit     
                elif userInput.lower() == 'q':
                    exit()

                # Check if user wants to enter a new query  
                elif userInput.lower() == 'n':
                    break
                
                # Otherwise, prompt user to enter valid input
                else:
                    print("Error: Invalid input. Please try again.")
                    continue

    # If output file does not exist, show error message             
    else:
        print("Error: Path to indexed files does not exist!")

# If less than or more than 1 argument is provided, show program description             
else:
    print("SearchEngine.py allows the user to view the top 10 results using BM25 retrival for a query provided.\n" +
          "The program requires that a single argument be passed through the CLI: \n\n" +
          "1. Path to the output produced by indexEngine.py\n\n" +
          "Please run program again with the appropriate arguments.\n")
