import sys

def makeRange(start, end):
	out = ['(']
	
	for s in range(ord(start), ord(end)) :
		out.append(chr(s))
		out.append('|')
		
	out.append(end)
	
	return out

def preProcess(expr : str) -> list:
	#add any missing . (NFA Concat operator)	
	out = []
	
	i = 0

	while i < len(expr) :
		
		if expr[i] == '[':
					
			start = expr[i+1]
			end = expr[i+3]
			
			out += makeRange(start, end)			
			i += 4			
	
		else :
			out.append(expr[i] if expr[i] != ']' else ')')

			if expr[i] in {'(', '|'} :
				i += 1; continue
	
			elif i < len(expr) - 1 :
				if expr[i+1] not in {'*', '?', '+', ')', '|', ']'} :
					out.append('.')					
			i += 1			

	return out

#operator precedence table

Precedence = {
	'|' : 0, #NFA Union Operator
	'.' : 1, #NFA Concat Operator
	'?' : 2, #NFA zero or one Operator
	'*' : 2, #NFA Closure Operator
	'+' : 2  #NFA one or more Operator
}

def toPosfix(expr : list) -> str:
	
	out, stack = [], []
	
	for symb in expr :
		if symb == '(' :
			stack.append(symb)
		
		elif symb == ')' :
			try :
				while stack[-1] != '(' :
					out.append(stack.pop())
			except IndexError:
				#if IndexError, then there are some missing parentheses
				sys.stderr.write("Invalid regex pattern.\n")
				sys.exit(64)						
			else : 
				stack.pop() #pop '('
					
		elif symb in {'+', '*', '?', '.', '|'} :
			
			while len(stack) > 0 : 
				if stack[-1] == '(' : 
					break
				elif Precedence[symb] > Precedence[stack[-1]] :
					break
				else : 
					out.append(stack.pop())
			
			stack.append(symb)			
		
		else :
			out.append(symb)
	
	while len(stack) > 0 :
		out.append(stack.pop())
	
	return "".join(out)

class State :
	def __init__(self, isEnd : bool) :
		self.isEnd =  isEnd
		self.transition = {}
		self.epsilonTransitions = []
	
	def addEpsilonTransition(self, to) :
		self.epsilonTransitions.append(to)
	
	def addTransition(self, to, symbol) :
		self.transition[symbol] = to

class NFA :
	def __init__(self, start : State, end : State) :
		self.start = start
		self.end = end

def fromEpsilon() -> NFA:
	start = State(False)
	end = State(True)
	start.addEpsilonTransition(end)
	
	return NFA(start, end)

def fromSymbol(symbol) -> NFA:
	start = State(False)
	end = State(True)
	start.addTransition(end, symbol)
	
	return NFA(start, end)

def concatenate(first : NFA, second : NFA) -> NFA:
	first.end.addEpsilonTransition(second.start)
	first.end.isEnd = False

	return NFA(first.start, second.end)

def union(first : NFA, second : NFA) -> NFA:
	start = State(False)
	start.addEpsilonTransition(first.start)
	start.addEpsilonTransition(second.start)

	end = State(True)
	first.end.addEpsilonTransition(end)
	first.end.isEnd = False	
	second.end.addEpsilonTransition(end)
	second.end.isEnd = False

	return NFA(start, end)

def closure(nfa : NFA) -> NFA:
	start = State(False)
	end = State(True)

	start.addEpsilonTransition(nfa.start)
	start.addEpsilonTransition(end)

	nfa.end.addEpsilonTransition(nfa.start)
	nfa.end.addEpsilonTransition(end)
	nfa.end.isEnd = False
	
	return NFA(start, end)

def oneOrMore(nfa : NFA) -> NFA:
	start = State(False)
	end = State(True)

	start.addEpsilonTransition(nfa.start)

	nfa.end.addEpsilonTransition(nfa.start)
	nfa.end.addEpsilonTransition(end)
	nfa.end.isEnd = False
	
	return NFA(start, end)

def zeroOrOne(nfa : NFA) -> NFA:
	start = State(False)
	end = State(True)

	start.addEpsilonTransition(nfa.start)
	start.addEpsilonTransition(end)

	nfa.end.addEpsilonTransition(end)
	nfa.end.isEnd = False
	
	return NFA(start, end)

def toNFA(posfixExpr : str) -> NFA:
	if(posfixExpr == '') :
		return fromEpsilon()
	
	stack = [] #stack of NFAs
	
	try :
		for symb in posfixExpr :
			if symb == '*' :	
				stack.append(closure(stack.pop()))
			elif symb == '+' :
				stack.append(oneOrMore(stack.pop()))
			elif symb == '?':
				stack.append(zeroOrOne(stack.pop()))			
			elif symb == '|':
				right = stack.pop()
				left = stack.pop()
				stack.append(union(left, right))
			elif symb == '.' :
				right = stack.pop()
				left = stack.pop()
				stack.append(concatenate(left, right))
			else :
				stack.append(fromSymbol(symb))
	
	except IndexError: 
		#if indexError, then the NFA could not be built correctly
		sys.stderr.write("Invalid regex pattern.\n")
		sys.exit(64)
	else :
		return stack.pop()

def setNextState(state : State, nextStates : list, visited : list) :
	
	if len(state.epsilonTransitions) > 0 :
		for stt in state.epsilonTransitions:
			if not stt in visited :
				visited.append(stt)
				setNextState(stt, nextStates, visited)
	else :
		nextStates.append(state)

def search(nfa : NFA, word : str) -> bool :
	current = []
	setNextState(nfa.start, current, [])
	
	for symbol in word :
		nextStates = []
		
		for state in current :
			if symbol in state.transition:
				setNextState(state.transition[symbol], nextStates, [])
		
		current = nextStates
	
	for state in current:
		if state.isEnd :
			return True
	
	return False

class Regex :
	def __init__(self, expr : str) :
		expr = toPosfix(preProcess(expr))
		self.nfa = toNFA(expr)
	
	def match(self, word : str) -> bool:
		return search(self.nfa, word)

