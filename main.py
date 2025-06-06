
sample_rules = """
And: 2
And(true, true) -> true
And(true, false) -> false
And(false, true) -> false
And(false, false) -> false

Or: 2
Or(true, true) -> true
Or(true, false) -> true
Or(false, true) -> true
Or(false, false) -> false

Xor: 2
Xor(true, true) -> false
Xor(true, false) -> true
Xor(false, true) -> true
Xor(false, false) -> false

Not: 1
Not(true) -> false
Not(false) -> true
"""

# --- AST Node Classes ---
class Term:
    pass

class Function(Term):
    def __init__(self, name: str, args: list):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"Function({self.name}, {self.args})"

class Constant(Term):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Constant({self.value})"

class Variable(Term):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Variable({self.name})"

def parse_rules(rules: str):
    # Parse the rules from the given string and return a dictionary of rules and their arities.
    rule_dict = {}
    arity_dict = {}
    lines = rules.strip().split('\n')
    current_rule = None
    for line in lines:
        # if a line has a name colon number, it declares the arity of the rule
        if ':' in line:
            parts = line.split(':')
            current_rule = parts[0].strip()
            arity_dict[current_rule] = int(parts[1].strip())
            rule_dict[current_rule] = []
        elif '->' in line and current_rule is not None:
            # if a line has an expression -> expression, it is a rule
            expression = line.strip()
            lhs = expression.split('->')[0].strip()
            rhs = expression.split('->')[1].strip()
            rule_dict[current_rule].append((lhs, rhs))

    return rule_dict, arity_dict

# --- Parser ---
def parse_term_recursive(tokens: list, index: list) -> Term:
    """Recursively parses tokens to build a Term (Constant, Variable, or Function).
    index is a list to allow modification by reference for the current token position.
    """
    if index[0] >= len(tokens):
        raise ValueError("Unexpected end of expression")

    token = tokens[index[0]]
    index[0] += 1 # Consume the token

    # Check for constants
    if token == 'true':
        return Constant(True)
    elif token == 'false':
        return Constant(False)
    # Check for variables (convention: lower case names)
    elif token[0].islower():
        return Variable(token)
    # Assume any other token followed by '(' is a function
    elif index[0] < len(tokens) and tokens[index[0]] == '(':
        func_name = token
        index[0] += 1 # Consume '('

        args = []
        # Parse arguments until ')' is encountered
        while index[0] < len(tokens) and tokens[index[0]] != ')':
            # Parse argument
            args.append(parse_term_recursive(tokens, index))
            # Check for comma separator, but don't require it after the last argument
            if index[0] < len(tokens) and tokens[index[0]] == ',':
                index[0] += 1 # Consume ','
            elif index[0] < len(tokens) and tokens[index[0]] != ')':
                 raise ValueError(f"Expected ',' or ')' after argument for '{func_name}'")


        if index[0] >= len(tokens) or tokens[index[0]] != ')':
            raise ValueError(f"Expected ')' after arguments for '{func_name}'")
        index[0] += 1 # Consume ')'

        return Function(func_name, args)
    else:
        # If it's not a known constant, function, or variable, it's an error
        raise ValueError(f"Unknown term: '{token}'")

def parse_expression(expression: str) -> Term:
    """Parses a string expression into an AST (Term object)."""
    tokens = tokenize(expression)
    # Use a mutable list to pass index by reference for the recursive function
    index = [0]
    ast = parse_term_recursive(tokens, index)
    
    if index[0] != len(tokens):
        raise ValueError(f"Unexpected tokens remaining after parsing: {tokens[index[0]:]}")
    return ast



# --- Tokenizer ---
def tokenize(expression: str):
    """Tokenizes the expression into a list of tokens."""
    tokens = []
    current_token = ''
    for char in expression:
        if char in '(),':
            if current_token:
                tokens.append(current_token)
                current_token = ''
            if char != ',':
                tokens.append(char)
        elif char.isspace():
            if current_token:
                tokens.append(current_token)
                current_token = ''
        else:
            current_token += char
    if current_token:
        tokens.append(current_token)
    return tokens

if __name__ == "__main__":
    rules, arity = parse_rules(sample_rules)
    # print rules and their arities
    print("Rules and their arities:")
    for rule, arity_value in arity.items():
        print(f"{rule}: {arity_value}")
    print("Parsed Rules:")
    for rule, expressions in rules.items():
        print(f"{rule}:")
        for expr in expressions:
            print(f"  {expr}")

    print('end')
