import pytest
from main import parse_expression, Function, Constant

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


if __name__ == "__main__":
    pytest.main([__file__])
    