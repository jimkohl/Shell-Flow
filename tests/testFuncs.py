import os
import re

def test_generate_fromFile():

    errorCode = os.system("/Users/adminn/workspace/shellcollector/env/bin/python3 /Users/adminn/workspace/shellcollector/shellcollector.py input/testFuncs.sh")
    assert errorCode == 0
    outputdir = 'output/'

    output = open(outputdir + 'dotData', "r").read()

    bool(re.match(r"// Shell script analysis", output))

    boxes = re.findall(r'subgraph+', output)
    assert(len(boxes) == 1)

    assert os.path.exists(outputdir + 'dotData.pdf')


def test_generate_fromDirectory():

    errorCode = os.system("/Users/adminn/workspace/shellcollector/env/bin/python3 /Users/adminn/workspace/shellcollector/shellcollector.py input")
    assert errorCode == 0

    outputdir = 'output/'

    output = open(outputdir + 'dotData', "r").read()

    bool(re.match(r"// Shell script analysis", output))

    boxes = re.findall(r'subgraph+', output)
    assert(len(boxes) == 3)

    assert os.path.exists(outputdir + 'dotData.pdf')
