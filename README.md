
# Term Rewriting Engine

This repository contains a basic Term Rewriting Engine.

## What is a Term Rewriting Engine?

A Term Rewriting Engine evaluates expressions by systematically applying a set of predefined transformation rules. These rules replace specific patterns within an expression with corresponding replacement expressions. The process continues until the expression can no longer be transformed, reaching a "normal form."

Examples:

- Not(true) ->
- Not(false) -> true
- Not(Not(x)) -> x

Not is a function, true and false are constants, and x is a variable.

## Key Concepts

- Term: The fundamental data unit. Terms are tree-like structures. They can be:

  - Constants: Atomic values (e.g., T, F, 1, 2.5).
  - Variables: Placeholders that can match any term (e.g., X, Y, Z).
  - Functions (or Constructors): Composed terms consisting of a function symbol and its arguments (e.g., AND(T, F), NOT(X)).

- Arity: The arity of a function symbol is the fixed number of arguments it takes. For example:

  - NOT has an arity of 1 (e.g., NOT(X)).
  - AND has an arity of 2 (e.g., AND(X, Y)).
  - Constants have an arity of 0.
  - Arity is crucial for parsing and pattern matching, ensuring terms are well-formed.

- Rewrite Rule: A rule defines a transformation from a pattern term to a replacement term.

  - written as pattern -> replacement.
  - When the engine finds a subterm that matches the pattern, it replaces that subterm with the replacement term, after substituting any variables matched during the pattern matching.

## How Rewrite Rules Work (Briefly)

1. Pattern Matching: The engine searches the current expression for subterms that structurally resemble the pattern of a rule. If a subterm matches, any variables in the pattern are "bound" to the corresponding parts of the subterm.
2. Substitution: Once a match is found and variables are bound, these bindings are applied to the replacement term of the rule.
3. Replacement: The matched subterm in the original expression is then replaced by the resulting substituted replacement term.
4. Iteration: This process repeats on the modified expression. The engine continues to apply rules until no more rules can be applied to any subterm, indicating the expression has reached its normal form.

## Status

Evaluation and Traces work.

``` txt
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
```
Responds with:
``` txt
  Given the rules and assignments:
  And: 2
      And(true, true) -> true
      And(true, false) -> false

      x = true
      y = false

  Expression 'And(x, y)' evaluated to: Constant(False)

  AST Trace:
  Step 1:
    Before: Function(And, [Constant(True), Constant(False)])
    Rule: And(true, false) -> false
    After: Constant(False)
```
