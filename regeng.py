import sys

class State(object):
    def __init__(self, accept: bool):
        self.accept = accept
        self.transition = dict()
        self.epsilon_transitions = list()
    
    def add_epsilon_transition(self, to: 'State'):
        self.epsilon_transitions.append(to)
    
    def add_transition(self, to: 'State', symbol: str):
        self.transition[symbol] = to

class NFA(object): 
    # NFA = Nondeterministic Finite Automaton
    def __init__(self, start: State, end: State):
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
    def from_symbol(symbol: str) -> 'NFA':
        # single symbol transition
        start = State(False)
        end = State(True)
        start.add_transition(end, symbol)
        
        return NFA(start, end)

    @staticmethod
    def concatenate(first: 'NFA', second: 'NFA') -> 'NFA':
        # concatenate two NFAs
        first.end.add_epsilon_transition(second.start)
        first.end.accept = False

        return NFA(first.start, second.end)

    @staticmethod
    def union(first: 'NFA', second: 'NFA') -> 'NFA':
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
    def closure(nfa: 'NFA') -> 'NFA':
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
    def one_or_more(nfa: 'NFA') -> 'NFA':
        # one or more of an NFA
        start = State(False)
        end = State(True)

        start.add_epsilon_transition(nfa.start)

        nfa.end.add_epsilon_transition(nfa.start)
        nfa.end.add_epsilon_transition(end)
        nfa.end.accept = False
        
        return NFA(start, end)

    @staticmethod
    def zero_or_one(nfa: 'NFA') -> 'NFA':
        # zero or one of an NFA
        start = State(False)
        end = State(True)

        start.add_epsilon_transition(nfa.start)
        start.add_epsilon_transition(end)

        nfa.end.add_epsilon_transition(end)
        nfa.end.accept = False
        
        return NFA(start, end)


    @staticmethod
    def from_posfix(posfix_expr: str) -> 'NFA':
        """Builds an NFA from a postfix notation expression"""
        if(posfix_expr == ''):
            return NFA.from_epsilon()
        
        stack = [] # stack of NFAs
        
        try:
            i = 0
            while i < len(posfix_expr):
                symb = posfix_expr[i]
                
                # Check for escaped special characters (marked with SOH control character)
                if symb == '\x01' and i + 1 < len(posfix_expr):
                    # This is a marked special character - treat it as a literal
                    stack.append(NFA.from_symbol(posfix_expr[i + 1]))
                    i += 2  # Skip the marker and the character
                    continue
                
                # Handle regular operators
                if symb == '*':    
                    stack.append(NFA.closure(stack.pop()))
                elif symb == '+':
                    stack.append(NFA.one_or_more(stack.pop()))
                elif symb == '?':
                    stack.append(NFA.zero_or_one(stack.pop()))            
                elif symb == '|':
                    right = stack.pop()
                    left = stack.pop()
                    stack.append(NFA.union(left, right))
                elif symb == '.':
                    right = stack.pop()
                    left = stack.pop()
                    stack.append(NFA.concatenate(left, right))
                else:
                    stack.append(NFA.from_symbol(symb))
                
                i += 1
        
        except IndexError: 
            # If IndexError, then the NFA could not be built correctly
            sys.stderr.write("Invalid regex pattern.\n")
            sys.exit(64)
        else:
            return stack.pop()


class RegexParser:
    """Class responsible for parsing and processing regular expressions"""
    
    # Operator precedence table
    _precedence = {
        '|': 0, # NFA Union Operator
        '.': 1, # NFA Concatenation Operator
        '?': 2, # NFA Zero or One Operator
        '*': 2, # NFA Closure Operator
        '+': 2  # NFA One or More Operator
    }
    
    @staticmethod
    def make_range(chars: list) -> list:
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
    def _expand_alias(char: str) -> list:
        """Expands regex aliases like d, w, s into their character classes"""
        match char:
            case 'd':  # Digits: 0-9
                return RegexParser.make_range(['0', '-', '9'])
                
            case 'w':  # Word characters: a-zA-Z0-9_
                chars = []
                chars.extend(['a', '-', 'z'])
                chars.extend(['A', '-', 'Z'])
                chars.extend(['0', '-', '9'])
                chars.append('_')
                return RegexParser.make_range(chars)
                
            case 's':  # Whitespace characters
                return RegexParser.make_range([' ', '\t', '\n', '\r', '\f', '\v'])
                
            # Special characters that need to be escaped - use a special prefix to mark them
            # We'll use ASCII control characters that won't appear in normal regex patterns
            case '.':  # Literal dot
                return ['\x01.']  # SOH (Start of Heading) + .
                
            case '-':  # Literal hyphen
                return ['\x01-']  # SOH + -
                
            case '+':  # Literal plus
                return ['\x01+']  # SOH + +
                
            case '*':  # Literal asterisk
                return ['\x01*']  # SOH + *
                
            case '?':  # Literal question mark
                return ['\x01?']  # SOH + ?
                
            case '(':  # Literal opening parenthesis
                return ['\x01(']  # SOH + (
                
            case ')':  # Literal closing parenthesis
                return ['\x01)']  # SOH + )
                
            case '[':  # Literal opening bracket
                return ['\x01[']  # SOH + [
                
            case ']':  # Literal closing bracket
                return ['\x01]']  # SOH + ]
                
            case '|':  # Literal pipe
                return ['\x01|']  # SOH + |
                
            case _:  # Any other character
                return [char]
    
    @staticmethod
    def pre_process(expr: str) -> list:
        """Pre-processes the regular expression, adding concatenation operators
        and processing character ranges and aliases"""
        out = []
        i = 0
        while i < len(expr):
            # Handle escape sequences and aliases
            if i < len(expr) - 1 and expr[i] == '\\':
                next_char = expr[i+1]
                # Process any escaped character (including aliases)
                alias_expansion = RegexParser._expand_alias(next_char)
                out.extend(alias_expansion)
                
                i += 2
                
                # Add concatenation operator if needed after an alias or escaped character
                if i < len(expr) and expr[i] not in {'*', '?', '+', ')', '|'}:
                    out.append('.')
                continue
            
            # Handle character classes
            elif expr[i] == '[':
                # Extract all characters between [ and ]
                chars = []
                i += 1  # Skip the '['
                
                # Collect all characters until we find ']'
                while i < len(expr) and expr[i] != ']':
                    # Handle escape sequences and aliases inside character classes
                    if i < len(expr) - 1 and expr[i] == '\\':
                        next_char = expr[i+1]
                        # Process any escaped character (including aliases)
                        alias_expansion = RegexParser._expand_alias(next_char)
                        # Add all individual characters (skipping '(', ')', and '|')
                        for char in alias_expansion:
                            if char not in ['(', ')', '|']:
                                chars.append(char)
                        i += 2
                        continue
                    # Regular character
                    chars.append(expr[i])
                    i += 1
                
                if i < len(expr):  # Skip the ']'
                    i += 1
                
                out += RegexParser.make_range(chars)
                
                # Add concatenation operator if needed after a character class
                if i < len(expr) and expr[i] not in {'*', '?', '+', ')', '|'}:
                    out.append('.')
                continue
            
            # Handle regular characters
            else:
                out.append(expr[i])

                if expr[i] in {'(', '|'}:
                    i += 1
                    continue
        
                elif i < len(expr) - 1:
                    if expr[i+1] not in {'*', '?', '+', ')', '|', ']'}:
                        out.append('.')                    
                i += 1

        return out

    @staticmethod
    def to_posfix(expr: list) -> str:
        """Converts an infix expression to postfix notation using the Shunting-yard algorithm"""
        out, stack = [], []
        
        for symb in expr:
            if symb == '(':
                stack.append(symb)
            
            elif symb == ')':
                try:
                    while stack[-1] != '(':
                        out.append(stack.pop())
                except IndexError:
                    # If IndexError, then there are missing parentheses
                    sys.stderr.write("Invalid regex pattern.\n")
                    sys.exit(64)                        
                else: 
                    stack.pop() # Remove '('
                    
            elif symb in {'+', '*', '?', '.', '|'}:
                
                while len(stack) > 0: 
                    if stack[-1] == '(':
                        break
                    elif RegexParser._precedence[symb] > RegexParser._precedence[stack[-1]]:
                        break
                    else:
                        out.append(stack.pop())
                
                stack.append(symb)            
            
            else:
                out.append(symb)
        
        while len(stack) > 0:
            out.append(stack.pop())
        
        return "".join(out)


class Match:
    """Represents a match found in a string"""
    
    def __init__(self, string: str, start: int, end: int):
        """
        Initialize a Match object
        
        Args:
            string: The original string that was searched
            start: The start index of the match
            end: The end index of the match (exclusive)
        """
        self.string = string
        self.start = start
        self.end = end
    
    @property
    def span(self) -> tuple[int, int]:
        """Returns a tuple containing the (start, end) positions of the match"""
        return (self.start, self.end)
        
    @property
    def group(self) -> str:
        """Returns the substring that was matched"""
        return self.string[self.start:self.end]
        
    def __repr__(self) -> str:
        """String representation of the match"""
        return f"<Match: '{self.group}' at {self.span}>"


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

    def match(self, word: str) -> Match or None:
        """
        Checks if the word completely matches the regular expression
        
        Returns:
            Match object if the entire string matches, None otherwise
        """
        current_states = self._get_epsilon_closure({self.nfa.start})

        for symbol in word:
            next_states_from_transitions = set()
            for state in current_states:
                if symbol in state.transition:
                    next_states_from_transitions.add(state.transition[symbol])
            
            if not next_states_from_transitions:
                return None # Dead end for a full match

            current_states = self._get_epsilon_closure(next_states_from_transitions)

        # For a full match, at least one of the final states must be an accept state
        if any(s.accept for s in current_states):
            return Match(word, 0, len(word))
        return None

    def search(self, word: str) -> Match or None:
        """
        Searches for the first occurrence of the pattern in the word.
        Finds the longest match starting at the earliest position.
        
        Returns:
            Match object with the first occurrence found, None if no match
        """
        # Handle empty string case separately
        if word == "":
            # Check if the pattern can match an empty string
            initial_states = self._get_epsilon_closure({self.nfa.start})
            if any(s.accept for s in initial_states):
                return Match(word, 0, 0)
            return None
            
        # Try starting the match at each position in the string
        for start_pos in range(len(word)):
            # Find all possible matches starting at this position
            matches = self._find_all_matches(word, start_pos)
            
            if matches:
                # Return the longest match starting at this position
                return max(matches, key=lambda m: m.end - m.start)
        
        return None
    
    def _find_all_matches(self, word: str, start_pos: int) -> list[Match]:
        """
        Finds all possible matches starting at the given position.
        Uses a breadth-first approach to find the longest possible match.
        
        Args:
            word: The string to search in
            start_pos: The position to start the search from
            
        Returns:
            List of Match objects for all matches found
        """
        matches = []
        
        # Start with the initial state
        current_states = self._get_epsilon_closure({self.nfa.start})
        
        # Check if the initial state is accepting (for empty string matches)
        if any(s.accept for s in current_states):
            matches.append(Match(word, start_pos, start_pos))
        
        # Process the word character by character
        pos = start_pos
        while pos < len(word):
            symbol = word[pos]
            
            # Find all states reachable from current states on this symbol
            next_states = set()
            for state in current_states:
                if symbol in state.transition:
                    next_states.add(state.transition[symbol])
            
            # If no transitions are possible, we're done
            if not next_states:
                break
            
            # Get epsilon closure of next states
            current_states = self._get_epsilon_closure(next_states)
            pos += 1
            
            # If we've reached an accept state, record this match
            if any(s.accept for s in current_states):
                matches.append(Match(word, start_pos, pos))
        
        return matches
