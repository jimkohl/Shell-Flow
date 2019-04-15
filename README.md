![](images/shell.jpeg)

# ShellCollector

## Purpose
ShellCollector is python implemented tool which scans bash shellscripts (single or from a directory) 
and produces a visualization of calls to shell functions and OS utilities.

It is currently under development with more work required.

## Origins
This project began as a fork of [Shell-flow](github.com/sivaswami/Shell-Flow) 
which was a starting place but not fully implemented.

## Dependencies

* [Python](https://www.python.org/downloads/) (tested with 3.7.3)

This tool utilizes the graphviz package and pygraphviz wrapper.  To install:
* brew install graphviz
* python3 -m venv tutorial-env 
* source tutorial-env/bin/activate
* pip3 install graphviz 
* pip3 install pytest
* pytest


