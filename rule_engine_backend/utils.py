import re

class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.node_type = node_type  
        self.left = left            
        self.right = right          
        self.value = value          

    def to_dict(self):
        node_dict = {
            "node_type": self.node_type,
            "value": self.value,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }
        return node_dict

    @staticmethod
    def from_dict(data):
        node = Node(node_type=data["node_type"], value=data.get("value"))
        if data.get("left"):
            node.left = Node.from_dict(data["left"])
        if data.get("right"):
            node.right = Node.from_dict(data["right"])
        return node



def tokenize(rule_string):
    pattern = r'\s*(=>|<=|==|!=|>=|>|<|AND|OR|\(|\)|\'[^\']*\'|\"[^\"]*\"|[\w_]+\s*[=><!]+\s*[^() ]+|[\w_]+)\s*'
    return re.findall(pattern, rule_string)

def create_operator_node(operators, operands):
    op = operators.pop() 
    right = operands.pop() 
    left = operands.pop()  
    operands.append(Node("operator", left=left, right=right, value=op))

def create_rule(rule_string):
    tokens = tokenize(rule_string)
    operators = []  
    operands = []   

    precedence = {'AND': 2, 'OR': 1}
    i = 0
    
    while i < len(tokens):
        token = tokens[i]
        
        if token == '(':
            start = i + 1  
            balance = 1  
            while balance > 0 and i < len(tokens) - 1:
                i += 1
                if tokens[i] == '(':
                    balance += 1
                elif tokens[i] == ')':
                    balance -= 1
            expression = ' '.join(tokens[start:i])
            operands.append(create_rule(expression))  
        elif token in precedence:
            while (operators and operators[-1] != '(' and 
                   precedence[operators[-1]] >= precedence[token]):
                create_operator_node(operators, operands)
            operators.append(token)
        elif i + 2 < len(tokens) and tokens[i + 1] in ['>', '<', '>=', '<=', '==', '!=']:
            full_operand = f"{token} {tokens[i + 1]} {tokens[i + 2]}"
            operands.append(Node("operand", value=full_operand))
            i += 2 
        else:
            operands.append(Node("operand", value=token))
        i += 1

    while operators:
        create_operator_node(operators, operands)

    return operands[0] if operands else None  




def combine_rules(rules):
    operator_count = {'AND': 0, 'OR': 0}
    for rule in rules:
        tokens = tokenize(rule)
        for token in tokens:
            if token in operator_count:
                operator_count[token] += 1
    main_operator = 'OR' if operator_count['OR'] >= operator_count['AND'] else 'AND'
    
    combined_operands = []

    for rule in rules:
        ast = create_rule(rule) 
        combined_operands.append(ast)
    root = combined_operands.pop(0)
    while combined_operands:
        next_operand = combined_operands.pop(0)
        root = Node("operator", left=root, right=next_operand, value=main_operator)

    return root



def node_to_dict(node):
    if node is None:
        return None
    return {
        "node_type": node.node_type,
        "value": node.value,
        "left": node_to_dict(node.left),
        "right": node_to_dict(node.right)
    }



def evaluate_node(node, data):
    if node.node_type == "operator":
        left_eval = evaluate_node(node.left, data)
        right_eval = evaluate_node(node.right, data)

        if node.value == "AND":
            return left_eval and right_eval
        elif node.value == "OR":
            return left_eval or right_eval
        else:
            raise ValueError(f"Unexpected operator: {node.value}")

    elif node.node_type == "operand":
        if not node.value or len(node.value.split()) < 3:
            raise ValueError(f"Unexpected operand format: {node.value}")

        parts = re.split(r'\s*(==|!=|>=|<=|>|<)\s*', node.value)
        if len(parts) != 3:
            raise ValueError(f"Unexpected operand format: {node.value}")

        left, operator, right = parts
        left = left.strip()
        right = right.strip()
        left_value = data.get(left, None)

        if right.isdigit():
            right_value = float(right)  # Assume it's a number
        elif right.startswith("'") and right.endswith("'"):
            right_value = right.strip("'")  # Treat as string
        else:
            raise ValueError(f"Invalid operand value: {right}")

        if left_value is None:
            return False

        if operator == '==':
            return left_value == right_value
        elif operator == '!=':
            return left_value != right_value
        elif operator == '>':
            return left_value > right_value
        elif operator == '<':
            return left_value < right_value
        elif operator == '>=':
            return left_value >= right_value
        elif operator == '<=':
            return left_value <= right_value
        else:
            raise ValueError(f"Unexpected comparison operator: {operator}")

    else:
        raise ValueError(f"Unexpected node type: {node.node_type}")

def evaluate_rule(ast_root, data):
    return evaluate_node(ast_root, data)


# example

# rule_string = "((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)"
# ast = create_rule(rule_string)
# # print ast 

# def print_ast(node, level=0):
#     if node is not None:
#         print(' ' * (level * 4) + f"{node.node_type}: {node.value}")
#         print_ast(node.left, level + 1)
#         print_ast(node.right, level + 1)

# print_ast(ast)
# print(ast.to_dict())

