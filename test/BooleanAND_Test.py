# Name: Saif Abuosba 
# File Name: BooleanAND_Test.py


import unittest

# List of expected output from Program #2 
expected = ['401 Q0 LA080290-0001 1 1 sabuosbaAND',
            '401 Q0 LA041090-0002 2 0 sabuosbaAND',
            '402 Q0 LA080290-0001 1 1 sabuosbaAND',
            '402 Q0 LA041090-0002 2 0 sabuosbaAND',
            '403 Q0 LA080290-0001 1 0 sabuosbaAND',
            '404 Q0 LA080290-0002 1 0 sabuosbaAND',
            '405 Q0 LA080290-0001 1 0 sabuosbaAND',
            '406 Q0 LA080290-0002 1 0 sabuosbaAND',
            '407 Q0 LA080290-0002 1 0 sabuosbaAND',
            '408 Q0 LA080290-0002 1 0 sabuosbaAND',
            '409 Q0 LA080290-0001 1 4 sabuosbaAND',
            '409 Q0 LA080290-0002 2 3 sabuosbaAND',
            '409 Q0 LA050189-0001 3 2 sabuosbaAND',
            '409 Q0 LA041090-0001 4 1 sabuosbaAND',
            '409 Q0 LA041090-0002 5 0 sabuosbaAND',
            '411 Q0 LA050189-0001 1 0 sabuosbaAND']

# Declare list to store actual output of Program #2 
actual = []


# Read output of Program #2 from txt file and store in list 'actual'
with open ("hw2-results-test.txt", 'r') as file:
     for line in file:
          actual.append(line.strip())

class TestOutput(unittest.TestCase):

    # Unit test which compares the expected and actual outputs of 
    # Program #2 based on a test dataset collection of documents and test queries
    def test_output(self):
            
            counter = 0
            
            for line in actual:
                
                if (line == expected[counter]):
                     result = 'PASS'
                else:
                    result = 'FAIL'
                
                print('Actual: ' + line + " Expected: " + expected[counter] + ' --> ' + result)
                bool(self.assertEqual(line, expected[counter]))
                counter += 1

# Run unit test 
if __name__ == '__main__':
    unittest.main()
