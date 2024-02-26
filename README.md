# Search Engines

**The content of this repository was originally created for MSCI 541 - Search Engines F23.**
**In order to run the programs in this repository the `latimes.gz` file is required and is not included due to copyright.**

# Setup:
  - Ensure your machine has `Python 3.6` or higher installed (NOTE: code was written and tested with `Python 3.11.1 64-bit` installed)
  - Clone repository to local machine
  - Open a command line terminal in the directory which contains the cloned repository on local machine

# Build Instructions:
 
### Index Engine - `IndexEngine.py`
- ```python IndexEngine.py <path-to-latimes.gz> <path-to-save-indexed-files> <porter-stemming-binary>```
- Indexes each document, extracts metadata and saves document in the following folder hierarchy using the DOCNO tag: `.../YY/MM/DD/DOCNO.txt` and `.../YY/MM/DD/DOCNO-metadata.txt`
- Creates a Lexicon: Mapping of terms to term IDs 
- Creates an inverted index: Dictionary mapping of termID to a list of all docID containing the term and a count of that term in each doc  

### Search Engine - `SearchEngine.py`
- CLI interactive program using the BM25 algorithm to allow user to enter a query which then computes and outputs the top 10 most relevant documents and allows user to view any of the 10 documents. 
- ```python SearchEngine.py <path-to-save-indexed-files>```

### BooleanAND - `BooleanAND.py`
- ```python BooleanAND.py <path-to-save-indexed-files> <path-to-queries.txt> <destination-path-for-results.txt>```
- Uses BooleanAND algorithm to return documents that contain **ALL** terms in query

### BooleanAND Test - `BooleanAND_Test.py`
- cd into the test folder of your cloned repository and run the following command:
    ```python BooleanAND_Test.py```

### Compute Evaluation Scores - `ComputeEvaluationScores.py`
- ```python ComputeEvaluationScores.py <path-to-qrels> <destination-path>```
- Produces a .csv file containing Average Precision, Precision@10, NDCG@10, NDCG@1000 scores for each query 

### Compute Evaluation Scores - `ComputeEvaluationScores.py`
- ```python ComputeEvaluationScores.py <path-to-qrels> <destination-path>```
- Produces a .csv file containing Average Precision, Precision@10, NDCG@10, NDCG@1000 scores for each query 

### Get Doc - `GetDoc.py`
- cd into the test folder of your cloned repository and run the following command:
    ```python GetDoc.py <path-to-save-indexed-files> <'id' or 'docno'> <value-of-id/docno>```
