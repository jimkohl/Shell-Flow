#!/usr/bin/python

import argparse
import sys
import os
import re
import collections
from graphviz import Digraph

# Parsing based on Bash grammar provided in link : http://wiki.bash-hackers.org/syntax/basicgrammar

# Note: Ply (lex/yacc) seems like a better tool for this job, but for now using what was provided

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
		runcommand = cmdstring.split(" ")[0]

		if ("||" not in cmdstring) and ("|" in cmdstring):
			return PipelineCommand(cmdstring)

		elif ("=" in cmdstring) and ("==" not in cmdstring):
			return AssignmentCommand(cmdstring)

		elif runcommand in self.complexWords:
			return CompoundCommand(cmdstring)

		elif runcommand in self.usualCommands:
			return UsualCommand(cmdstring)

		elif runcommand in self.shellbuiltInWords:
			return BuiltinCommand(cmdstring)

		elif "()" in cmdstring or "FUNCTION" in cmdstring or "function" in cmdstring:
			return BashFunction(cmdstring.replace("function", "").replace("(", "").replace(")", "").strip())

		else:
			return BashCommand(runcommand)


class BashCommand:
	def __init__(self, cmdstring):
		self.cmd = cmdstring.split(" ")[0]
		self.shape = "egg"
		self.cmdType = "CALL"

	def printgraph(self, localdot):
		if "FUNC" in self.cmdType:
			return localdot.node(self.cmd, self.cmd, shape=self.shape, type=self.cmdType)
		else:
			return localdot.edge(script_name, self.cmd, constraint='false')


class ShellBlock:

	def __init__(self, cmdstring):
		self.cmd = cmdstring.split(" ")[0]
		self.cmds = []
		self.shape = "point"
		self.cmdType = "block"

	def printgraph(self, localdot):
		return localdot.node(self.cmd, self.cmd, shape=self.shape, type=self.cmdType)


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
		self.shape = "plaintext"
		self.cmdType = "BUILTIN"

	def printgraph(self, localdot):
		#return localdot.node(self.cmd, self.cmd, shape=self.shape, type=self.cmdType)
		return None

	@staticmethod
	def isbuiltin():
		return True


class UsualCommand (BashCommand):

	# builtInWords = self.usualCommands.split(",")
	def __init__(self, cmdstring):
		super(UsualCommand, self).__init__(cmdstring)
		self.shape = "point"
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


# create a bounded box for a script's functions and calls to built-ins / functions / system commands
def create_subgraph(parent, script):
	global script_name
	script_name = os.path.basename(script)

	print("file=" + script)

	lines = list(open(script))

	graph_attr = {'label': script_name}
	script_graph = Digraph(name="cluster" + script, graph_attr=graph_attr, node_attr={'shape': 'box'})    # cluster sets compound=true;

	precmd = None

	dq = collections.deque()
	dq.append(ShellBlock(script_name))
	for line in lines:
		parser = BashParser()
		if (line.strip() is not None) and (line.strip().startswith("#") is False) and line.strip() != '':
			grammarline = grammar(line.strip())
			currentcmd = parser.parse(grammarline)
			try:
				if dq:
					prevcmd = dq.pop()
					# if prevcmd.cmdType != currentcmd.cmdType:
					# 	if prevcmd.cmd != currentcmd.cmd:
					dq.append(prevcmd)
				print(currentcmd.cmdType + "\t→ " + grammarline)

			except IndexError:
				print("ER")
				pass

			dq.append(currentcmd)

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
			dq.popleft().printgraph(script_graph)
		except IndexError:
			break

	# with parent.subgraph(name='cluster_0') as c:
	#     c.attr(style='filled')
	#     c.attr(color='lightgrey')
	#     c.node_attr.update(style='filled', color='white')
	#     c.edges([('a0', 'a1'), ('a1', 'a2'), ('a2', 'a3')])
	#     c.attr(label='process #1')

	parent.subgraph(script_graph)   # this has to be deferred


# scan script(s) for shell script elements

if __name__ == "__main__":
	path = sys.argv[1]
	displayfile = bool(len(sys.argv) > 2)    # TODO: hokey way to check for display option; head in this direction:

	# parser = argparse.ArgumentParser(description='Eval shellscripts and gen graph')
	# parser.add_argument("input", ..., required=True)
	# parser.add_argument("display", ..., required=False)
	# parser.parse_args()

	scripts = []

	if os.path.isdir(path):    # specialize to only process .sh files
		for root, dirs, files in os.walk(path):
			for file in files:
				if file.endswith('.sh'):
					scripts.append(root + "/" + file)
	else:
		scripts.append(path)

	parent = Digraph(comment="Shell script analysis")

	for script in scripts:
		create_subgraph(parent, script)

	parent.render("output/dotData", view=displayfile)

# if not line.trim().startswith(pattern) for pattern in builtInWords
