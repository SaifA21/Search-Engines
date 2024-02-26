# Name: Saif Abuosba 
# File Name: ComputeEvaluationScores.py

# Import libraries
import sys
import os
import csv
import math

# Initialize variables for command line arguments
qrelsPath = ""
resultsPath = ""


# Method to extract judments from QRELS file 
def extractJudgements(qrelsPath):
    
    # Map to store judgments for each topic 
    judgements = {}

    # Map to store # of relevant docs for each topic 
    relevantCounts = {}
    
    # Open QRELS file 
    with open(qrelsPath) as f:
        
        # Loop and store judgments in map
        for line in f:
            
            # Split line into list of strings
            line = line.strip().split()

            # Extract topic, docno, and judgement from line
            topic = int(line[0])
            docno = line[2]
            judgement = int(line[3])

            # Add judgment if the topic exists in map
            if topic in judgements.keys():
                judgements[topic].append(docno)
                judgements[topic].append(judgement) 

            # Add topic and judment to map if first time seeing topic 
            else:
                judgements[topic] = [docno, judgement]


            # Check if topic exists in relevantCounts map
            if int(topic) in relevantCounts.keys():
                # Add relevant doc to count if judgement is > 0
                if judgement > 0:
                    relevantCounts[topic] += 1
            
            # Add topic to relevantCounts map if first time seeing topic
            else:
                relevantCounts[topic] = 0

    # Return map of judgements and map of relevant doc counts
    return judgements, relevantCounts


# Method to extract results from results file
def extractResults(resultsPath):
    
    # try to open results file assuming format is correct
    try:
        
        # Map to store results for each topic
        results = {}

        # Open results file
        with open(resultsPath) as f:

            # Loop through each line in results file
            for line in f:
                
                # Split line into list of strings
                line = line.strip().split() 
                
                # Extract topic, qColumn, docno, rank, score, and runID from line
                topic = int(line[0])
                qColumn = line[1]
                docno = str(line[2]).upper()
                rank = int(line[3])
                score = float(line[4])
                runID = str(line[5])

                # Add result to map if topic exists in map
                if topic in results.keys():
                    results[topic].append([topic, qColumn, docno, rank, float(score), runID])
                
                # Add topic and result to map if first time seeing topic
                else:
                    results[topic] = [[topic, qColumn, docno, rank, float(score), runID]]

        # Return map of results
        return results
    
    # If results file is not in correct format, print error message and exit program
    except:
        print('bad format')
        sys.exit()



# Method to sort results by score (desccending)
def sortResults (results):

    # loop through each topic in results
    for result in results.keys():
        
        # Sort results by score (descending)
        results[result] = sorted(results[result], key=lambda x: x[4], reverse=True)

    # Return sorted results
    return results
    

# Method to compute precision at 10
def computePrecisionAt10(sortedResults, judgements):

    # Initialize list to store precision at 10 for each topic
    precisionResults = []
   
    # Initialize precision
    precision = 0.0

    # Initialize runID
    runID = ''

    # Loop through each topic in sortedResults
    for topic in sortedResults:
        
        # Initialize variables
        countOfRelevant = 0
        counter = 0

        # Loop through each result in topic
        for result in sortedResults[topic]:

            # Extract runID from result
            runID = result[5]

            # Extract docno from result
            docno = result[2]
            
            # Check if docno is in judgements
            if docno in judgements[topic]:
                
                # Extract judgement index from judgements
                judgementIndex = judgements[topic].index(docno)+1

                # Check if judgement is > 0
                if judgements[topic][judgementIndex] > 0: 
                    
                    # Increment count of relevant docs
                    countOfRelevant += 1
            
            # Increment counter
            counter += 1
            
            # Break loop if counter reaches 10
            if counter == 10:
              break

        # Compute precision at 10 for topic to 3 decimal places
        precision = "{:.4f}".format(countOfRelevant/counter)

        # Add precision at 10 to precisionResults
        precisionResults.append(['P_10', topic, precision])
    
    # Return precisionResults
    return precisionResults, runID
    

# Method to compute average precision 
def computeAveragePrecision(sortedResults, relevantCounts):
    
    # Initialize list to store average precisions for each topic
    averagePrecisions = []
    
    # Loop through each topic in sortedResults
    for topic in sortedResults:
        
        # Initialize lists to store precisions and relevance for each rank
        precisions = []
        relevance = []

        # Initialize counter and count of relevant docs
        countOfRelevant = 0
        counter = 1

        # Initialize average precision
        averagePrecision = 0.0


        # Loop through each result in topic
        for result in sortedResults[topic]:

            # Extract docno from result
            docno = result[2]
            
            # Check if docno is in judgements
            if docno in judgements[topic]:
                
                # Extract judgement index from judgements
                judgementIndex = judgements[topic].index(docno)+1

                # Check if judgement is > 0
                if judgements[topic][judgementIndex] > 0: 

                    # Add 1 to relevance list
                    relevance.append(1)
                    
                    # Increment count of relevant docs
                    countOfRelevant += 1

                # If judgement is 0, add 0 to relevance list
                else:
                    relevance.append(0)
            
                # Add precision to precisions list
                precisions.append(countOfRelevant/counter)


            # If docno is not in judgements, add 0 to relevance list and precision to precisions list
            else:
                precisions.append(countOfRelevant/counter)
                relevance.append(0)
            
            # Increment counter
            counter += 1


        # Compute average precision for topic
        for i in range (len(precisions)):
            averagePrecision += (precisions[i] * relevance[i])

        
        # Compute average precision for topic to 4 decimal places
        averagePrecision = ("{:.4f}".format(averagePrecision/relevantCounts[topic]))

        # Add average precision to averagePrecisions list
        averagePrecisions.append(['ap', topic, averagePrecision])

    # Return averagePrecisions
    return averagePrecisions


# Method to compute NDCG
def computeNDCG(results, relevantCounts, judgements, rank):
    
    # Initialize list to store NDCG for each topic
    ndcg = []

    # Loop through each topic in results
    for topic in results:

        # Initialize stop condition
        stopConditon = rank 

        # Initialize idcg and dcg
        idcg = 0.0
        dcg = 0.0

        # Check if rank is greater than the number of results for topic
        if len(results[topic]) < rank:
            # Set stop condition to the number of results for topic
            stopConditon = len(results[topic])

        # Compute idcg for topic
        for i in range(min(relevantCounts[topic], rank)):
            # Add relevance to idcg (i+2 since i starts at 0)
            idcg += 1/(math.log2((i+2)))


        # Compute dcg for topic
        for i in range (stopConditon):
            
            # Extract result from results
            dcgResult = results[topic][i]

            # Extract docno from result
            docNoDCG = dcgResult[2]

            # Check if docno is in judgements
            if docNoDCG in judgements[topic]:

                # Extract judgement index from judgements
                judgmentIndexForDCG = judgements[topic].index(docNoDCG)+1

                # Extract judgement from judgements
                judgmentDCG = judgements[topic][judgmentIndexForDCG]

                # Check if result is relevant
                if judgmentDCG > 0:
                    # Add relevance to dcg (i+2 since i starts at 0)
                    dcg += (1/(math.log2(i+2)))


        # Compute NDCG for topic to 4 decimal places
        ndcgValue = ("{:.4f}".format(dcg/idcg))

        # Add NDCG of topic to ndcg list 
        ndcg.append([('ndcg_cut_' + str(rank)), topic, ndcgValue])

    # Return ndcg list
    return ndcg



# Method to create output file  
def createOutputFile(precisionAt10, averagePrecision, ndcgAt10, ndcgAt1000, runID):

    # Create filename for output file
    filename = runID + "-measures.csv"

    # Check if output file already exists
    if not os.path.exists(filename):
    
        # Open output file and write measures to file
        with open(filename, 'w', newline="") as csvFile:
      
            # Create csv writer
            csvWriter = csv.writer(csvFile)
            
            # Write precisionAt10, averagePrecision, ndcgAt10, and ndcgAt1000 to file
            csvWriter.writerows(averagePrecision)
            csvWriter.writerows(ndcgAt10)
            csvWriter.writerows(ndcgAt1000)
            csvWriter.writerows(precisionAt10)
            
        # Print success message
        print('Success: ' + filename + ' created!')

    # Print error message
    else:
        print('Error: ' + filename + ' already exists, please delete and run program again!')
        print()
        sys.exit()




# MAIN /////////////////////////////////////////////////////////////////////////////////////////////

# Check if 2 arguments have been provided (2 + filename) 
if (len(sys.argv) == 3):

    qrelsPath = str(sys.argv[1]) # Path to QRELS file
    resultsPath = str(sys.argv[2]) # Path to results file
    
    # Check that the QRELS file exists
    if os.path.exists(qrelsPath):
        # Check that the results file exists
        if  os.path.exists(resultsPath):
            
            # Extract judgements from QRELS file 
            judgements, relevantCounts = extractJudgements(qrelsPath)

            # Extract results from results file
            results = extractResults(resultsPath)
            
            # Sort results by score (descending)
            sortedResults = sortResults(results)

            # Compute precision at 10 for each topic 
            precisionAt10, runID = computePrecisionAt10(sortedResults, judgements) 

            # Compute average precision for each topic
            averagePrecision = computeAveragePrecision(sortedResults, relevantCounts)
            
            # Compute NDCG at rank 10 for each topic
            ndcgAt10 = computeNDCG(sortedResults, relevantCounts, judgements, 10)

            # Compute NDCG at rank 1000 for each topic
            ndcgAt1000 = computeNDCG(sortedResults, relevantCounts, judgements, 1000)

            # Create output file 
            createOutputFile(precisionAt10, averagePrecision, ndcgAt10, ndcgAt1000, runID)


        # If results file does not exist, print error message
        else:
            print('Error: Path to result file does not exist!')

    # If QRELS file does not exist, print error message        
    else:
        print('Error: Path to QRELS file does not exist!')
    
# If the two inputs are not provided, output message explaining what the program does
else:
    print("\nThis program computes 4 effective measures (Average Precision, Precision@10, NDCG@10, NDCG@1000) " + 
        "provided 2 arguments in the command line.\n 1: path to the qrels file containing judgments for topics, "+
        "\n 2: path to the results file created by the index engine. \n\n" +
        "Please run program again with the appropriate arguments.\n")
