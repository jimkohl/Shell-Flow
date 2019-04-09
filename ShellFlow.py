#!/usr/bin/python
import sys
import re
import collections
from graphviz import Digraph

# Parsing based on Bash Grammar provided in link : http://wiki.bash-hackers.org/syntax/basicgrammar

class BashParser:

	shellbuiltInWords = "alias, bg, bind, break, builtin, caller, cd, command, compgen, complete, compopt, continue, declare, dirs, disown, echo, enable, eval, exec, exit, export, false, fc, fg, getopts, hash, help, history, jobs, kill, let, local, logout, mapfile, popd, printf, pushd, pwd, read, readarray, readonly, return, set, shift, shopt, source, suspend, test, times, trap, true, type, typeset, ulimit, umask, unalias, unset, wait"
	usualCommands = "mkdir, rmdir, rm -rf, ls, ps, tree, find, grep, egrep, sed, awk, ifconfig, ping, rm, du, df, less, more, test"
	complexWords = "for, if, else, elif, fi, do, done, while, {, }, ((, )), [[, ]], case, esac, until, select"

	def __init__(self):
		self.line = ""

	def parse(self, cmdString):
		cmdString = cmdString.strip()
		cmd = None
		runCommand = cmdString.split(" ")[0].lower()
		if ( ("||" not in cmdString) and ("|" in cmdString)):
			cmd = PipelineCommand(cmdString)
			return cmd

		elif ( "()" in cmdString or "function " in cmdString): 
			cmd = BashFunction(cmdString.replace("function","").replace("(","").replace(")","").strip())
			return cmd

		elif (("=" in cmdString) and ("==" not in cmdString)):
			cmd = AssignmentCommand(cmdString)
			return cmd

		elif runCommand in self.complexWords:
			cmd = CompoundCommand(cmdString)
			return cmd

		elif runCommand in self.usualCommands:
			cmd = UsualCommand(cmdString)
			return cmd

		elif runCommand in self.shellbuiltInWords:
			cmd = BuiltinCommand(cmdString)
			return cmd

		else:
			cmd = BashCommand(runCommand)
			return cmd
	
class BashCommand:

	def __init__(self, cmdString):
		self.cmd = cmdString.split(" ")[0]
		self.shape = "box"
		self.cmdType = "Other"

	def printGraph(self, dot):
		if ("FUNCT" in self.cmdType):
			return dot.node(self.cmd, self.cmd, shape = self.shape, type = self.cmdType)
		else:
			return dot.edge('mylocal', self.cmd, constraint='false')
			
class BlockCommand:

	def __init__(self, cmdString):
		self.cmds = []
		self.shape = "box3d"
		self.cmdType = "block"

	def printGraph(self, dot):
		if ("FUNCT" in self.cmdType):
			return dot.node(self.cmd, self.cmd, shape = self.shape, type = self.cmdType)
		else:
			return None

class AssignmentCommand(BashCommand):

	#builtInWords = self.shellbuiltInWords.split(",")
	def __init__(self, cmdString):
		super(AssignmentCommand, self).__init__(cmdString.split("=")[0])
		self.shape = "box"
		self.cmdType = "SET"

    # may want to turn this off as assignments are generally not that interesting
	def printGraph(self, dot):
		#return dot.node(self.cmdType, self.cmd, shape = self.shape)
		return None

	def isBuiltin():
		return True;
		
class BuiltinCommand (BashCommand):

	#builtInWords = self.shellbuiltInWords.split(",")
	def __init__(self, cmdString):
		super(BuiltinCommand, self).__init__(cmdString)
		self.shape = "box"
		self.cmdType = "BUILTIN"

	def isBuiltin():
		return True;

class UsualCommand (BashCommand):

	#builtInWords = self.usualCommands.split(",")
	def __init__(self, cmdString):
		super(UsualCommand, self).__init__(cmdString)
		self.shape = "box"
		self.cmdType = "USUAL"

	def isBuiltin():
		return False;
		
class PipelineCommand (BashCommand):
	def __init__(self, cmdString):
		super(PipelineCommand, self).__init__(cmdString)
		self.cmdType = "PIPELINE"
		self.shape = "cds"
		self.leftCmd = cmdString
		self.rightCmd = cmdString
		
class ListCommand (BashCommand):
	def __init__(self, cmdString):
		super(ListCommand, self).__init__(cmdString)
		self.cmd = cmdString.split(" ")[0]
		#self.cmdType = "LIST"
		#self.cmdList.add(cmdString.split("&&,&,;,||,"))
		self.shape = "hexagon"
		#if ( ("&&" in cmdString) or ("&" in cmdString)): 
		#	self.cmd="AND"
		#elif ("||" in cmdString):
		#	self.cmd="OR"
		
class CompoundCommand (BlockCommand):
	def __init__(self, cmdString):
		super(CompoundCommand, self).__init__(cmdString)
		#self.cmdType="COMPOUND"
		if "if" in cmdString or "then" in cmdString or "fi" in cmdString or "else" in cmdString:
			self.cmdType="IF"
			self.cmd = cmdString.split(" ")[0] #.upper()
			self.shape = "diamond"

		elif "{" in cmdString and "}" in cmdString:
			self.cmdType = "LOOP"
			self.cmd = cmdString.split(" ")[0] #.upper()
			self.shape = "box3d"
			#self.cmds=[cmdString.split(" ")[0]]

		elif "{" not in cmdString and "}" in cmdString:
			self = ''

		else:
			self.cmd = ''

	def findCmdType(self):
		''' 
		 for command
		 while, do while loop commands
		 if then elif command
		 do done command
		 sub-shell or execute commands
		 {} - run a s group command
		 (()) and [[]] expressions		
		'''

class BashFunction (BlockCommand):
	def __init__(self, cmdString):
		super(BashFunction, self).__init__(cmdString)
		self.cmd = cmdString.replace(" {", "").replace(" }", "")
		self.shape = "ellipse"
		if "{" in cmdString and "}" in cmdString:
			self.cmdType="FUNCT_DEF_1LINE"
		else:
			self.cmdType="FUNCT_DEF"
		self.commandsInBlock=[]

		
def Grammar(bashCommand):
	SingleQuoteRegEx = '(\\\'.*?\\\')'
	DoubleQuoteRegEx = '(\\\".*?\\\")'
	VariableRegEx    = '\$[\{].*?[\}]'
	BackQuoteRegEx   = '(`).*?(`)'
	SubShellRegEx    = '($\().*?(\))'
	TestCmdRegEx     = '($\[\[).*?(\]\])'
	Test2CmdRegEx    = '($\[).*?(\])'
	Others           = '.*?'
	line = re.sub(SingleQuoteRegEx,'CMD_CONSTANTVAR', bashCommand)
	line = re.sub(BackQuoteRegEx,'CMD_SUBSHELL', line)
	line = re.sub(SubShellRegEx,'CMD_SUBSHELL2', line)
	line = re.sub(TestCmdRegEx,"TESTINPUT",line)
	line = re.sub(Test2CmdRegEx,"TEST2INPUT", line)
	return line

#for x in builtInWords:
	#print(x)
	
if __name__ == "__main__":
	ctr = 0;
	lines  = list(open(sys.argv[1]))
	dot = Digraph(comment = "Shell script analysis")

    # dot.node('A', 'King Arthur')
    # dot.node('L', 'Sir Lancelot the Brave')
	#
    # dot.edges(['AB', 'AL'])
	#
    # dot.edge('B', 'L', constraint='false')

	precmd = None
	dq = collections.deque()
	for line in lines:
		bparser = BashParser()
		if ((line.strip() is not None) and (line.strip().startswith("#")==False) and line.strip() !=''):
			grammarLine = Grammar(line.strip())
			print(grammarLine)
			currentCmd = bparser.parse(grammarLine)
			try:
				if dq:
					prevcmd = dq.pop()
					print(prevcmd.cmdType + " vs "+ currentCmd.cmdType)
					print(currentCmd.cmdType)
					# if prevcmd.cmdType != currentCmd.cmdType:
					# 	if prevcmd.cmd != currentCmd.cmd:
					dq.append(prevcmd)
		
			except IndexError:
				print("ER")
				pass

			currentCmd.cmdType
			dq.append(currentCmd)
			
	while True:
		try:
			dotNode = dq.popleft().printGraph(dot)
		except IndexError:
			break
		
		# if ((precmd is not None) and (dotNode is not None)):
		# 	if (isinstance(cmd,BashCommand)):
		# 		dot.edge(precmd.cmd.cmd,"Next")
		# 		precmd=cmd
		# 		print("[*] " + line.strip() + "=>" + cmd.cmd)
		# else:
		# 	dot.edge(precmd.cmd.cmds[0],"Next")
		# 	precmd=cmd
		# 	print("[*] " + line.strip() + "=>" + cmds.cmds[0])

	dot.render("output/test", view=True)
		
		#if not line.trim().startswith(pattern) for pattern in builtInWords