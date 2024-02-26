# Name: Saif Abuosba 
# File Name: BooleanAND.py

# Import libraries
import sys
import os
import json

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

# reads query file and returns contents in a list 
# one index for query number and another for query 
def indexQueries(queriesPath):
    queriesList = []
    queries = open(queriesPath, "r")

    for line in queries:
        queriesList.append(str(line))
        
    return (queriesList)


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
                # check if term in query exists in any document 
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

        # check if term in query exists in any document 
        if (token in lexicon.keys()):
            # if it is add to list, otherwise omit from query 
            tokens.append(token)

    return tokens

# Method that finds the list of docids in both postings lists
def intersect (list1, list2):
    
    # Define ist for intersect of the 2 lists 
    results = []

    # Define pointers for the two lists 
    i = 0
    j = 0

    # loop with stop condition of reaching the end of either list
    while i != len(list1) and j != len(list2):
        
        # document id in both lists
        if list1[i] == list2[j]:
            
            # add to the results list 
            results.append(list1[i])

            # increment pointers
            j = j+2 # List2 has docIDs and term counts
            i = i+1 # List1 has only docIDs
        
        # if the current docid in list1 is smaller than in list2
        elif list1[i] < list2[j]:
            i = i+1 
        
        # if the current docid in list2 is smaller than in list1
        else:
            j = j+2
    

    return results


# Method to write final results to file
def output(outputList):
    
    outputWriter = open(outputFileName, "a")
    
    # Write the list of results to the output file 
    for i in range (0, len(outputList)):
        # Logic to ensure there is no empty line at the end of file
        if i != len(outputList)-1:
            outputWriter.write(outputList[i] + '\n')
        else:
            outputWriter.write(outputList[i])
    
    outputWriter.close()

# ******************* Main *****************************

# Check if 3 arguments have been provided (filename + 3 arguments) 
if (len(sys.argv) == 4):
        
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
    queriesPath = str(sys.argv[2])
    outputFileName= str(sys.argv[3])


    # Check if output file exists
    if not os.path.exists(outputFileName):
        if os.path.exists(directoryPath):
            if os.path.exists(queriesPath):
            
                # Create a list containing pairs of indicies with query id followed by query 
                queryList = indexQueries(queriesPath)
                
                # Construct the lexicon and inverseIndex
                lexicon = constructLexicon(directoryPath)
                inverseIndex = contructInverseIndex(directoryPath)
                
                # Contruct id to docno mapping
                idToDocNoFile = open (directoryPath+'/idToDocNo.txt')
                idToDocNo = json.loads(idToDocNoFile.read())


                # loop through queries (second index for query terms) 
                for i in range (0,len(queryList), 2) :

                    # Define list for termIDs
                    termIDs = []
                    
                    # Store current query number 
                    queryNumber = queryList[i]
                    
                    # Store current query terms 
                    query = queryList[i+1]

                    # Send to tokenizer 
                    tokenizedQuery = tokenize(query)
                
                    # Store associated id for each term by retrieving from lexicon 
                    for token in tokenizedQuery:
                        termIDs.append(lexicon[token])
                    
                    # Define list 'result' to store intersections 
                    result = []

                    # Counter to represent either first term in query or not 
                    counter =  1

                    # Loop through term ids to complete intersections  
                    for id in termIDs:
                    
                        # Get posting list of current term id 
                        postingList = inverseIndex[str(id)]
                        
                        # if this is the first term, set result to doc ids of current posting list
                        if counter == 1:
                            # append doc ids of current postings list (filter out term counts)
                            for x in range (0,len(postingList), 2):
                                result.append(postingList[x])                

                        # if this is the second or more term, intersect with current result list 
                        else:
                            result = intersect(result,postingList) 
                            
                        # add one to counter to indicate which term we are on 
                        counter += 1

                    # Format output for each document returned for current query
                    # Format: QUERY_NUMBER Q0 DOCNO RANK SCORE sabuosbaAND  
                    for i in range (0, len(result)):
                        outputList.append(queryNumber.strip() + " Q0 " + idToDocNo[str(result[i])] + " " + 
                                    str(i+1) + " " + str(1) + " sabuosbaAND")          
                    
                # Send list to document writer     
                output(outputList) 
                print("Program complete!")

            else:
                print("Error: Path to queries file does not exist!")

        else:
            print("Error: Path to indexed files does not exist!")



    # If output directory already exists, print error message
    else:
        print("Error: Output file already exists! Delete and try again.")


# If less than or more than 3 arguments are provided, show program description             
else:
    print("\nBooleanAND.py allows you to retrieve all documents that contain all terms in your query.\n" +
          "It uses the lexicon, inverted index and metadata store produced by indexEngine.py to retrieve the DOCNOs.\n" +
          "The program requires that 3 arguments be passed through the CLI: \n\n" +
          "1. Path to the output produced by indexEngine.py\n" +
          "2. Path to the txt file containing your queries.\n" +
          "3. File name where you would like the results to be stored (i.e. documents matching your query). \n\n" +
          "Please run program again with the appropriate arguments.\n")

