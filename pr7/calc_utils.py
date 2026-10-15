
import ast
import operator
import math

BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _calculate(node):
    if isinstance(node, ast.Expression):
        return _calculate(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ValueError("Разрешены только числа")
        if not math.isfinite(node.value):
            raise ValueError("Число должно быть конечным")
        return node.value

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)

        if op_type not in BINARY_OPERATORS:
            raise ValueError("Операция не поддерживается")

        left = _calculate(node.left)
        right = _calculate(node.right)

        if op_type is ast.Pow and abs(right) > 10:
            raise ValueError("Слишком большая степень")

        result = BINARY_OPERATORS[op_type](left, right)

        if isinstance(result, (int, float)):
            if isinstance(result, float) and not math.isfinite(result):
                raise ValueError("Результат слишком большой")

        return result

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)

        if op_type not in UNARY_OPERATORS:
            raise ValueError("Операция не поддерживается")

        return UNARY_OPERATORS[op_type](_calculate(node.operand))

    raise ValueError("Недопустимое выражение")


def calculate(expression):
    if len(expression) > 200:
        raise ValueError("Выражение слишком длинное")

    tree = ast.parse(expression, mode="eval")
    result = _calculate(tree)

    if isinstance(result, float) and not math.isfinite(result):
        raise ValueError("Результат должен быть конечным")

    return result
