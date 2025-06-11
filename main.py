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
Not(Not(x)) -> x
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

    def __eq__(self, other):
        # Constant(False) == Constant(False)
        if isinstance(other, Constant):
            return self.value == other.value
        return False

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
            tokens.append(char) # Always append the delimiter
        elif char.isspace():
            if current_token:
                tokens.append(current_token)
                current_token = ''
        else:
            current_token += char
    if current_token:
        tokens.append(current_token)
    return tokens

# --- Evaluate ---
def parse_rules_and_assignments(rules_and_assignments_string: str):
    rule_dict = {}
    arity_dict = {}
    assignment_map = {}
    lines = rules_and_assignments_string.strip().split('\n')
    current_rule_name = None

    for line in lines:
        if ':' in line and '->' not in line and '=' not in line: # Rule arity declaration
            parts = line.split(':')
            current_rule_name = parts[0].strip()
            arity_dict[current_rule_name] = int(parts[1].strip())
            rule_dict[current_rule_name] = []
        elif '->' in line and current_rule_name is not None: # Rule definition
            expression = line.strip()
            lhs = expression.split('->')[0].strip()
            rhs = expression.split('->')[1].strip()
            rule_dict[current_rule_name].append((lhs, rhs))
        elif '=' in line: # Assignment
            parts = line.split('=')
            var_name = parts[0].strip()
            value_str = parts[1].strip()
            if value_str == 'true':
                assignment_map[var_name] = Constant(True)
            elif value_str == 'false':
                assignment_map[var_name] = Constant(False)
            else:
                raise ValueError(f"Unsupported assignment value: {value_str}")
        elif not line.strip(): # Empty line
            current_rule_name = None # Reset current rule context
        else:
            pass # Ignore other lines for now

    return rule_dict, arity_dict, assignment_map

def substitute_variables(ast: Term, assignments: dict) -> Term:
    if isinstance(ast, Constant):
        return ast
    elif isinstance(ast, Variable):
        if ast.name in assignments:
            return assignments[ast.name] # Return the assigned Constant node
        else:
            return ast # Variable not in assignments, return as is
    elif isinstance(ast, Function):
        new_args = [substitute_variables(arg, assignments) for arg in ast.args]
        return Function(ast.name, new_args)
    else:
        raise ValueError(f"Unknown term type during substitution: {type(ast)}")

def match_pattern(pattern: Term, target: Term, bindings: dict) -> bool:
    """
    Attempts to match a pattern AST against a target AST, populating bindings.
    Returns True if a match is found, False otherwise.
    """
    if isinstance(pattern, Constant):
        return isinstance(target, Constant) and pattern.value == target.value
    elif isinstance(pattern, Variable):
        # If variable is already bound, check if target matches the bound value
        if pattern.name in bindings:
            return target == bindings[pattern.name]
        else:
            # Bind the variable to the target
            bindings[pattern.name] = target
            return True
    elif isinstance(pattern, Function):
        if not isinstance(target, Function) or pattern.name != target.name or len(pattern.args) != len(target.args):
            return False
        # Recursively match arguments
        for p_arg, t_arg in zip(pattern.args, target.args):
            if not match_pattern(p_arg, t_arg, bindings):
                return False
        return True
    return False

def apply_single_rule_pass(current_ast: Term, rules: dict, ast_trace: list) -> tuple[Term, bool]:
    """
    Attempts to apply one rule in a single pass over the AST.
    Returns the modified AST and a boolean indicating if any change occurred.
    """
    changed = False
    
    # Helper to recursively apply rules
    def _apply_recursive(node: Term) -> Term:
        nonlocal changed
        if isinstance(node, Function):
            # First, apply rules to arguments
            new_args = []
            for arg in node.args:
                new_arg = _apply_recursive(arg)
                if new_arg != arg: # Check if argument changed
                    changed = True
                new_args.append(new_arg)
            node = Function(node.name, new_args) # Create new function node with potentially changed args

            # Then, try to apply rules to the current function node itself
            for rule_name, rule_list in rules.items():
                if node.name == rule_name: # Only consider rules for the current function's name
                    for lhs_str, rhs_str in rule_list:
                        lhs_ast = parse_expression(lhs_str)
                        rhs_ast = parse_expression(rhs_str)
                        
                        bindings = {}
                        if match_pattern(lhs_ast, node, bindings):
                            # Apply the rule: substitute variables in RHS with bound values
                            transformed_node = substitute_variables(rhs_ast, bindings)
                            ast_trace.append((node, lhs_str, rhs_str, transformed_node)) # Record the transformation
                            changed = True
                            return transformed_node # Return the transformed node and stop for this rule
        return node # No rule applied or not a Function node

    new_ast = _apply_recursive(current_ast)
    return new_ast, changed

def evaluate(expression_string: str, rules_and_assignments_string: str) -> tuple[Term, list]:
    rules, arities, assignments = parse_rules_and_assignments(rules_and_assignments_string)
    
    # Parse the initial expression
    current_ast = parse_expression(expression_string)

    # Apply assignments to the AST
    current_ast = substitute_variables(current_ast, assignments)

    # Initialize AST trace
    ast_trace = []

    # Apply rules iteratively until no more changes
    changed = True
    while changed:
        current_ast, changed = apply_single_rule_pass(current_ast, rules, ast_trace)

    return current_ast, ast_trace

# --- Infix Expression Parsing with Shunting Yard Algorithm ---
def parse_infix_expression(expression: str) -> Term:
    """
    Parses an infix expression (like "2 + 3*4") into an AST using the shunting yard algorithm.
    """
    tokens = tokenize_infix(expression)
    output_queue = []
    operator_stack = []
    
    precedence = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '^': 3  # Exponentiation
    }
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        # Numbers become Constant nodes
        if token.isdigit():
            output_queue.append(Constant(int(token)))
        
        # Variables (identifiers)
        elif token.isalpha():
            output_queue.append(Variable(token))
        
        # Left parenthesis
        elif token == '(':
            operator_stack.append(token)
        
        # Right parenthesis
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                # Pop operators from stack to queue until '(' is found
                handle_operator_popping(operator_stack, output_queue)
            
            if operator_stack and operator_stack[-1] == '(':
                operator_stack.pop()  # Remove the '(' from stack
            else:
                raise ValueError("Mismatched parentheses in expression")
        
        # Operators
        elif token in precedence:
            # While there's an operator on top with higher/equal precedence, pop it
            while (operator_stack and operator_stack[-1] != '(' and
                   operator_stack[-1] in precedence and
                   precedence[operator_stack[-1]] >= precedence[token]):
                handle_operator_popping(operator_stack, output_queue)
            
            operator_stack.append(token)
            
        i += 1
    
    # Pop any remaining operators
    while operator_stack:
        if operator_stack[-1] == '(':
            raise ValueError("Mismatched parentheses in expression")
        handle_operator_popping(operator_stack, output_queue)
    
    # The output queue should now contain a single AST
    if len(output_queue) != 1:
        raise ValueError(f"Invalid expression: expected 1 result, got {len(output_queue)}")
    
    return output_queue[0]

def handle_operator_popping(operator_stack: list, output_queue: list):
    """Helper function to handle operator popping in the shunting yard algorithm."""
    op = operator_stack.pop()
    
    # Map of operators to function names
    op_to_func = {
        '+': 'Add',
        '-': 'Sub',
        '*': 'Mul',
        '/': 'Div',
        '^': 'Pow'
    }
    
    if op in op_to_func:
        # Pop the right operand first (for non-commutative operations)
        if len(output_queue) < 2:
            raise ValueError(f"Not enough operands for operator {op}")
        
        right = output_queue.pop()
        left = output_queue.pop()
        
        # Create function node for this operation
        output_queue.append(Function(op_to_func[op], [left, right]))

def tokenize_infix(expression: str) -> list:
    """
    Tokenizes an infix expression, handling numbers, operators, and parentheses.
    """
    tokens = []
    i = 0
    
    while i < len(expression):
        char = expression[i]
        
        # Skip whitespace
        if char.isspace():
            i += 1
            continue
            
        # Handle numbers (multi-digit)
        if char.isdigit():
            num = char
            j = i + 1
            while j < len(expression) and expression[j].isdigit():
                num += expression[j]
                j += 1
            tokens.append(num)
            i = j
            continue
            
        # Handle identifiers (variable names)
        if char.isalpha():
            name = char
            j = i + 1
            while j < len(expression) and (expression[j].isalnum() or expression[j] == '_'):
                name += expression[j]
                j += 1
            tokens.append(name)
            i = j
            continue
            
        # Operators and parentheses (single characters)
        if char in '+-*/^()':
            tokens.append(char)
            i += 1
            continue
            
        # Unknown character
        raise ValueError(f"Unknown character in expression: '{char}'")
    
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

    # Example usage of the new evaluate function
    sample_rules_and_assignments = """
    And: 2
    And(true, true) -> true
    And(true, false) -> false

    x = true
    y = false
    """
    expression_to_evaluate = "And(x, y)"
    evaluated_ast, trace = evaluate(expression_to_evaluate, sample_rules_and_assignments)
    print(f"\nGiven the rules and assignments:\n{sample_rules_and_assignments.strip()}")
    print(f"\nExpression '{expression_to_evaluate}' evaluated to: {evaluated_ast}")
    print("\nAST Trace:")
    for i, (before, lhs, rhs, after) in enumerate(trace):
        print(f"Step {i+1}:")
        print(f"  Before: {before}")
        print(f"  Rule: {lhs} -> {rhs}")
        print(f"  After: {after}")

    print('end')
