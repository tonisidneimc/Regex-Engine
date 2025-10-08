import sys

class State(object):
	def __init__(self, accept : bool) :
		self.accept =  accept
		self.transition = dict()
		self.epsilon_transitions = list()
	
	def add_epsilon_transition(self, to : 'State') :
		self.epsilon_transitions.append(to)
	
	def add_transition(self, to : 'State', symbol : str) :
		self.transition[symbol] = to

class NFA(object): 
	# NFA = Nondeterministic Finite Automaton
	def __init__(self, start : State, end : State) :
		self.start = start
		self.end = end

	@staticmethod
	def from_epsilon() -> 'NFA':
		# empty transition
		start = State(False)
		end = State(True)
		start.add_epsilon_transition(end)
		
		return NFA(start, end)

	@staticmethod
	def from_symbol(symbol : str) -> 'NFA':
		# single symbol transition
		start = State(False)
		end = State(True)
		start.add_transition(end, symbol)
		
		return NFA(start, end)

	@staticmethod
	def concatenate(first : 'NFA', second : 'NFA') -> 'NFA':
		# concatenate two NFAs
		first.end.add_epsilon_transition(second.start)
		first.end.accept = False

		return NFA(first.start, second.end)

	@staticmethod
	def union(first : 'NFA', second : 'NFA') -> 'NFA':
		# union two NFAs
		start = State(False)
		start.add_epsilon_transition(first.start)
		start.add_epsilon_transition(second.start)

		end = State(True)
		first.end.add_epsilon_transition(end)
		first.end.accept = False	
		second.end.add_epsilon_transition(end)
		second.end.accept = False

		return NFA(start, end)

	@staticmethod
	def closure(nfa : 'NFA') -> 'NFA':
		# closure of an NFA
		start = State(False)
		end = State(True)

		start.add_epsilon_transition(nfa.start)
		start.add_epsilon_transition(end)

		nfa.end.add_epsilon_transition(nfa.start)
		nfa.end.add_epsilon_transition(end)
		nfa.end.accept = False
		
		return NFA(start, end)

	@staticmethod
	def one_or_more(nfa : 'NFA') -> 'NFA':
		# one or more of an NFA
		start = State(False)
		end = State(True)

		start.add_epsilon_transition(nfa.start)

		nfa.end.add_epsilon_transition(nfa.start)
		nfa.end.add_epsilon_transition(end)
		nfa.end.accept = False
		
		return NFA(start, end)

	@staticmethod
	def zero_or_one(nfa : 'NFA') -> 'NFA':
		# zero or one of an NFA
		start = State(False)
		end = State(True)

		start.add_epsilon_transition(nfa.start)
		start.add_epsilon_transition(end)

		nfa.end.add_epsilon_transition(end)
		nfa.end.accept = False
		
		return NFA(start, end)


	@staticmethod
	def from_posfix(posfix_expr : str) -> 'NFA':
		"""Builds an NFA from a postfix notation expression"""
		if(posfix_expr == '') :
			return NFA.from_epsilon()
		
		stack = [] # stack of NFAs
		
		try :
			for symb in posfix_expr :
				if symb == '*' :	
					stack.append(NFA.closure(stack.pop()))
				elif symb == '+' :
					stack.append(NFA.one_or_more(stack.pop()))
				elif symb == '?':
					stack.append(NFA.zero_or_one(stack.pop()))			
				elif symb == '|':
					right = stack.pop()
					left = stack.pop()
					stack.append(NFA.union(left, right))
				elif symb == '.' :
					right = stack.pop()
					left = stack.pop()
					stack.append(NFA.concatenate(left, right))
				else :
					stack.append(NFA.from_symbol(symb))
		
		except IndexError: 
			# If IndexError, then the NFA could not be built correctly
			sys.stderr.write("Invalid regex pattern.\n")
			sys.exit(64)
		else :
			return stack.pop()
	

class RegexParser:
	"""Class responsible for parsing and processing regular expressions"""
	
	# Operator precedence table
	_precedence = {
		'|' : 0, # NFA Union Operator
		'.' : 1, # NFA Concatenation Operator
		'?' : 2, # NFA Zero or One Operator
		'*' : 2, # NFA Closure Operator
		'+' : 2  # NFA One or More Operator
	}
	
	@staticmethod
	def make_range(chars : list) -> list:
		"""Creates a character class for expressions like [a-zA-Z_]
		
		Args:
			chars: List of characters and ranges in the character class
			
		Returns:
			List representing the character class as a union of characters
		"""
		char_set = set() # Use a set to automatically eliminate duplicates
		i = 0
		
		while i < len(chars):
			# Check if it's a range (a-z)
			if i + 2 < len(chars) and chars[i+1] == '-':
				start = chars[i]
				end = chars[i+2]
				
				# Add all characters in the range (inclusive)
				for s in range(ord(start), ord(end) + 1):
					char_set.add(chr(s))
				
				i += 3  # Skip the range (e.g., "a-z")
			else:
				# Single character
				char_set.add(chars[i])
				i += 1
		
		char_list = sorted(list(char_set))  # Sort for consistent output
		
		out = ['(']
		
		if char_list:
			out.append(char_list[0])
			
			# Add remaining characters with alternation
			for char in char_list[1:]:
				out.append('|')
				out.append(char)
		
		out.append(')')
		return out

	@staticmethod
	def pre_process(expr : str) -> list:
		"""Pre-processes the regular expression, adding concatenation operators
		and processing character ranges"""
		out = []
		i = 0
		while i < len(expr) :
			
			if expr[i] == '[':
				# Extract all characters between [ and ]
				chars = []
				i += 1  # Skip the '['
				
				# Collect all characters until we find ']'
				while i < len(expr) and expr[i] != ']':
					chars.append(expr[i])
					i += 1
				
				if i < len(expr):  # Skip the ']'
					i += 1
				
				out += RegexParser.make_range(chars)
				
				# Add concatenation operator if needed after a character class
				if i < len(expr) and expr[i] not in {'*', '?', '+', ')', '|'} :
					out.append('.')
			
			else:
				out.append(expr[i])

				if expr[i] in {'(', '|'} :
					i += 1; continue
		
				elif i < len(expr) - 1 :
					if expr[i+1] not in {'*', '?', '+', ')', '|', ']'} :
						out.append('.')					
				i += 1

		return out

	@staticmethod
	def to_posfix(expr : list) -> str:
		"""Converts an infix expression to postfix notation using the Shunting-yard algorithm"""
		out, stack = [], []
		
		for symb in expr :
			if symb == '(' :
				stack.append(symb)
			
			elif symb == ')' :
				try :
					while stack[-1] != '(' :
						out.append(stack.pop())
				except IndexError:
					# If IndexError, then there are missing parentheses
					sys.stderr.write("Invalid regex pattern.\n")
					sys.exit(64)						
				else : 
					stack.pop() # Remove '('
						
			elif symb in {'+', '*', '?', '.', '|'} :
				
				while len(stack) > 0 : 
					if stack[-1] == '(' : 
						break
					elif RegexParser._precedence[symb] > RegexParser._precedence[stack[-1]] :
						break
					else : 
						out.append(stack.pop())
				
				stack.append(symb)			
			
			else :
				out.append(symb)
		
		while len(stack) > 0 :
			out.append(stack.pop())
		
		return "".join(out)


class Regex:
    def __init__(self, pattern: str):
        """Initializes a Regex object from a regular expression pattern"""
        posfix_expr = RegexParser.to_posfix(RegexParser.pre_process(pattern))
        self.nfa = NFA.from_posfix(posfix_expr)

    def _get_epsilon_closure(self, states: set) -> set:
        """Calculates the epsilon-closure for a set of states."""
        stack = list(states) # keep track of states to visit
        closure = set(states) # stores the result and prevents reprocessing states

		# While there are states on the stack to explore...
        while stack:
            state = stack.pop()
            # For each epsilon transition from the current state...
            for s in state.epsilon_transitions:
                # If this is a state we haven't visited yet...
                if s not in closure:
                    # Add it to our final set (the closure).
                    closure.add(s)
                    # And add it to the stack to explore its own epsilon transitions.
                    stack.append(s)
        return closure

    def match(self, word: str) -> bool:
        """Checks if the word completely matches the regular expression"""
        current_states = self._get_epsilon_closure({self.nfa.start})

        for symbol in word:
            next_states_from_transitions = set()
            for state in current_states:
                if symbol in state.transition:
                    next_states_from_transitions.add(state.transition[symbol])
            
            if not next_states_from_transitions:
                return False # Dead end for a full match

            current_states = self._get_epsilon_closure(next_states_from_transitions)

        # For a full match, at least one of the final states must be an accept state
        return any(s.accept for s in current_states)

    def search(self, word: str) -> bool:
        """
        Searches for the first occurrence of the pattern in the word.
        """
        # Start with the epsilon closure of the initial state
        initial_closure = self._get_epsilon_closure({self.nfa.start})
        current_states = initial_closure

        for symbol in word:
            # Find all states reachable from the current states on the current symbol
            next_states_from_transitions = set()
            for state in current_states:
                if symbol in state.transition:
                    next_states_from_transitions.add(state.transition[symbol])

            # Get the epsilon closure of the states we just reached
            current_states = self._get_epsilon_closure(next_states_from_transitions)
            
            # Add the initial states back in. This allows the NFA to start a new match
            # from the current position in the word
            current_states.update(initial_closure)
            
            # Check for a match after processing the symbol
            if any(s.accept for s in current_states):
                return True

        # If the loop finishes, check if an empty pattern matches an empty part of the string
        return any(s.accept for s in current_states)

