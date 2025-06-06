import pytest
from main import parse_expression, Function, Constant, Variable, evaluate

def test_parse_expression_not_true():
    expression = "Not(true)"
    expected_ast = Function('Not', [Constant(True)])
    actual_ast = parse_expression(expression)
    assert actual_ast.name == expected_ast.name
    assert len(actual_ast.args) == len(expected_ast.args)
    assert actual_ast.args[0].value == expected_ast.args[0].value


def test_parse_expression_not_not_true():
    expression = "Not(Not(true))"
    expected_ast = Function('Not', [Function('Not', [Constant(True)])])
    actual_ast = parse_expression(expression)
    assert actual_ast.name == expected_ast.name
    assert len(actual_ast.args) == len(expected_ast.args)
    assert actual_ast.args[0].name == expected_ast.args[0].name
    assert len(actual_ast.args[0].args) == len(expected_ast.args[0].args)
    assert actual_ast.args[0].args[0].value == expected_ast.args[0].args[0].value

def test_parse_expression_not_not_something():
    expression = "Not(Not(x))"
    expected_ast = Function('Not', [Function('Not', [Variable('x')])])
    actual_ast = parse_expression(expression)
    assert actual_ast.name == expected_ast.name
    assert len(actual_ast.args) == len(expected_ast.args)
    assert actual_ast.args[0].name == expected_ast.args[0].name
    assert len(actual_ast.args[0].args) == len(expected_ast.args[0].args)
    assert actual_ast.args[0].args[0].name == expected_ast.args[0].args[0].name

def test_evaluate_expression_not_true():
    expected_result = Constant(False)
    expression_to_evaluate = "Not(true)"
    sample_rules_and_assignments = """
    Not:1
    Not(true) -> false
    Not(false) -> true
    Not(Not(x)) -> x
    """
    evaluated_ast, trace = evaluate(expression_to_evaluate, sample_rules_and_assignments)
    print(f"\nExpression '{expression_to_evaluate}' evaluated to: {evaluated_ast}")
    print("\nAST Trace:")
    for i, (before, lhs, rhs, after) in enumerate(trace):
        print(f"Step {i+1}:")
        print(f"  Before: {before}")
        print(f"  Rule: {lhs} -> {rhs}")
        print(f"  After: {after}")
    assert evaluated_ast == expected_result

def test_evaluate_expression_not_not_true():
    expected_result = Constant(True)
    expression_to_evaluate = "Not(Not(true))"
    sample_rules_and_assignments = """
    Not:1
    Not(true) -> false
    Not(false) -> true
    Not(Not(x)) -> x
    """
    evaluated_ast, trace = evaluate(expression_to_evaluate, sample_rules_and_assignments)
    print(f"\nExpression '{expression_to_evaluate}' evaluated to: {evaluated_ast}")
    print("\nAST Trace:")
    for i, (before, lhs, rhs, after) in enumerate(trace):
        print(f"Step {i+1}:")
        print(f"  Before: {before}")
        print(f"  Rule: {lhs} -> {rhs}")
        print(f"  After: {after}")
    assert evaluated_ast == expected_result


if __name__ == "__main__":
    pytest.main([__file__])
    