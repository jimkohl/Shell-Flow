#!/usr/bin/python

import sys
import os
import re
import collections
from graphviz import Digraph

# Parsing based on Bash grammar provided in link : http://wiki.bash-hackers.org/syntax/basicgrammar


class BashParser:

	shellbuiltInWords = \
		"alias, bg, bind, break, builtin, caller, cd, command, compgen, complete, compopt, continue, " + \
		"declare, dirs, disown, echo, enable, eval, exec, exit, export, false, fc, fg, getopts, " + \
		"hash, help, history, jobs, kill, let, local, logout, mapfile, popd, printf, pushd, pwd, read, " + \
		"readarray, readonly, return, set, shift, shopt, source, suspend, test, times, trap, true, type, typeset, " + \
		"ulimit, umask, unalias, unset, wait"

	usualCommands = \
		"mkdir, rmdir, rm -rf, ls, ps, tree, find, grep, egrep, sed, awk, " + \
		"ifconfig, ping, rm, du, df, less, more, test"

	complexWords = "for, if, else, elif, fi, do, done, while, {, }, ((, )), [[, ]], case, esac, until, select"

	def __init__(self):
		self.line = ""

	def parse(self, cmdstring):
		cmdstring = cmdstring.strip()
		runcommand = cmdstring.split(" ")[0].lower()

		if ("||" not in cmdstring) and ("|" in cmdstring):
			return PipelineCommand(cmdstring)

		elif "()" in cmdstring or "FUNCTION" in cmdstring or "function" in cmdstring:
			return BashFunction(cmdstring.replace("function", "").replace("(", "").replace(")", "").strip())

		elif ("=" in cmdstring) and ("==" not in cmdstring):
			return AssignmentCommand(cmdstring)

		elif runcommand in self.complexWords:
			return CompoundCommand(cmdstring)

		elif runcommand in self.usualCommands:
			return UsualCommand(cmdstring)

		elif runcommand in self.shellbuiltInWords:
			return BuiltinCommand(cmdstring)

		else:
			return BashCommand(runcommand)


class BashCommand:

	def __init__(self, cmdstring):
		self.cmd = cmdstring.split(" ")[0]
		self.shape = "box"
		self.cmdType = "CALL"

	def printgraph(self, localdot):
		if "FUNC" in self.cmdType:
			return localdot.node(self.cmd, self.cmd, shape=self.shape, type=self.cmdType)
		else:
			return localdot.edge('mylocal', self.cmd, constraint='false')


class BlockCommand:

	def __init__(self, cmdstring):
		self.cmd = cmdstring.split(" ")[0]
		self.cmds = []
		self.shape = "box3d"
		self.cmdType = "block"

	def printgraph(self, localdot):
		if "FUNC" in self.cmdType:
			return localdot.node(self.cmd, self.cmd, shape=self.shape, type=self.cmdType)
		else:
			return None


class AssignmentCommand(BashCommand):

	# builtInWords = self.shellbuiltInWords.split(",")
	def __init__(self, cmdstring):
		super(AssignmentCommand, self).__init__(cmdstring.split("=")[0])
		self.shape = "box"
		self.cmdType = "ASSIGN"

	# may want to turn this off as assignments are generally not that interesting
	def printgraph(self, localdot):
		# return localdot.node(self.cmdType, self.cmd, shape = self.shape)
		return None

	@staticmethod
	def isbuiltin():
		return True


class BuiltinCommand (BashCommand):

	# builtInWords = self.shellbuiltInWords.split(",")
	def __init__(self, cmdstring):
		super(BuiltinCommand, self).__init__(cmdstring)
		self.shape = "box"
		self.cmdType = "BUILTIN"

	@staticmethod
	def isbuiltin():
		return True


class UsualCommand (BashCommand):

	# builtInWords = self.usualCommands.split(",")
	def __init__(self, cmdstring):
		super(UsualCommand, self).__init__(cmdstring)
		self.shape = "box"
		self.cmdType = "USUAL"

	@staticmethod
	def isbuiltin():
		return False


# ls | grep 'pattern' | more

class PipelineCommand (BashCommand):
	def __init__(self, cmdstring):
		super(PipelineCommand, self).__init__(cmdstring)
		self.cmdType = "PIPELINE"
		self.shape = "cds"
		self.leftCmd = cmdstring
		self.rightCmd = cmdstring


class ListCommand (BashCommand):
	def __init__(self, cmdstring):
		super(ListCommand, self).__init__(cmdstring)
		self.cmd = cmdstring.split(" ")[0]

		# self.cmdType = "LIST"
		# self.cmdList.add(cmdstring.split("&&,&,;,||,"))

		self.shape = "hexagon"

	# if ( ("&&" in cmdstring) or ("&" in cmdstring)):
	#  self.cmd="AND"
	# elif ("||" in cmdstring):
	#  self.cmd="OR"


class CompoundCommand (BlockCommand):
	def __init__(self, cmdstring):
		super(CompoundCommand, self).__init__(cmdstring)
		# self.cmdType="COMPOUND"
		if "if" in cmdstring or "then" in cmdstring or "fi" in cmdstring or "else" in cmdstring:
			self.cmdType = "IF"
			self.cmd = cmdstring.split(" ")[0]   # .upper()
			self.shape = "diamond"

		elif "{" in cmdstring and "}" in cmdstring:
			self.cmdType = "LOOP"
			self.cmd = cmdstring.split(" ")[0]   # .upper()
			self.shape = "box3d"
		# self.cmds=[cmdstring.split(" ")[0]]

		elif "{" not in cmdstring and "}" in cmdstring:
			self.cmd = ''

		else:
			self.cmd = ''

	def findcmdtype(self):
		"""
		for command
		while, do while loop commands
		if then elif command
		do done command
		sub-shell or execute commands
		{} - run a s group command
		(()) and [[]] expressions
		"""

#inFunction = false;

# [ function ] name [ () ] { command-list; }

class BashFunction (BlockCommand):
	def __init__(self, cmdstring):
		super(BashFunction, self).__init__(cmdstring)
		self.cmd = cmdstring.replace(" {", "").replace(" }", "")

		global func_name
		func_name = self.cmd

		self.shape = "ellipse"
		if "{" in cmdstring and "}" in cmdstring:
			self.cmdType = "FUNC1"
		else:
			self.cmdType = "FUNC"
		self.commandsInBlock = []


def grammar(bashcommand):
	single_quote_regex = r'(\\\'.*?\\\')'
	# double_quote_regex = '(\\\".*?\\\")'
	# variable_regex = '\$[\{].*?[\}]'
	backquote_regex = '(`).*?(`)'
	subshell_regex = r'($\().*?(\))'
	testcmd_regex = r'($\[\[).*?(\]\])'
	test2cmd_regex = r'($\[).*?(\])'
	# others = '.*?'

	parsedline = re.sub(single_quote_regex, 'CMD_CONSTANTVAR', bashcommand)
	parsedline = re.sub(backquote_regex, 'CMD_SUBSHELL', parsedline)
	parsedline = re.sub(subshell_regex, 'CMD_SUBSHELL2', parsedline)
	parsedline = re.sub(testcmd_regex, "TESTINPUT", parsedline)
	parsedline = re.sub(test2cmd_regex, "TEST2INPUT", parsedline)
	return parsedline

# for x in builtInWords:
# print(x)



def create_subgraph(script):
	func_name = os.path.basename(script)
	lines = list(open(script))

	script_graph = Digraph(name="cluster" + script, node_attr={'shape': 'box'})    # cluster sets compound=true;

	precmd = None
	dq = collections.deque()
	for line in lines:
		parser = BashParser()
		if (line.strip() is not None) and (line.strip().startswith("#") is False) and line.strip() != '':
			grammarLine = grammar(line.strip())
			currentCmd = parser.parse(grammarLine)
			try:
				if dq:
					prevcmd = dq.pop()
					# if prevcmd.cmdType != currentCmd.cmdType:
					# 	if prevcmd.cmd != currentCmd.cmd:
					dq.append(prevcmd)
				print(currentCmd.cmdType + "\t→ " + grammarLine)

			except IndexError:
				print("ER")
				pass

			dq.append(currentCmd)

	# if ((precmd is not None) and (dotNode is not None)):
	# 	if (isinstance(cmd,BashCommand)):
	# 		dot.edge(precmd.cmd.cmd,"Next")
	# 		precmd=cmd
	# 		print("[*] " + line.strip() + "=>" + cmd.cmd)
	# else:
	# 	dot.edge(precmd.cmd.cmds[0],"Next")
	# 	precmd=cmd
	# 	print("[*] " + line.strip() + "=>" + cmds.cmds[0])

	while True:
		try:
			dotNode = dq.popleft().printgraph(script_graph)
			parent.subgraph(script_graph)     # this has to be deferred
		except IndexError:
			break

	return dotNode


if __name__ == "__main__":
	path = sys.argv[1]

	files = []

	if os.path.isdir(path):    # specialize to only process .sh files
		files = [path + f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
	else:
		files.append(path)

	parent = Digraph(comment="Shell script analysis")

	for script in files:
		create_subgraph(script)

	parent.render("output/dotData", view=True)

# if not line.trim().startswith(pattern) for pattern in builtInWords
