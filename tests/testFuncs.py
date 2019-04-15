import os

def test_funcs():

    errorCode = os.system("/Users/adminn/workspace/shellcollector/env/bin/python3 /Users/adminn/workspace/shellcollector/shellcollector.py input/testFuncs.sh")
    assert errorCode == 0

def test_directoryInput():

    errorCode = os.system("/Users/adminn/workspace/shellcollector/env/bin/python3 /Users/adminn/workspace/shellcollector/shellcollector.py input")
    assert errorCode == 0

