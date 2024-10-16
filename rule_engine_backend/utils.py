import re

class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.node_type = node_type  # "operator" or "operand"
        self.left = left            # Reference to left child (Node)
        self.right = right          # Reference to right child (Node)
        self.value = value          # The value of the node (e.g., the operator or operand)

    def to_dict(self):
        # Create a dictionary representation of the Node for storage in MongoDB
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


        # Value for operand nodes

def tokenize(rule_string):
    # Tokenize the input rule string while keeping operators and parentheses
    # This pattern captures conditions, operators, AND, OR, and parentheses correctly
    pattern = r'\s*(=>|<=|==|!=|>=|>|<|AND|OR|\(|\)|\'[^\']*\'|\"[^\"]*\"|[\w_]+\s*[=><!]+\s*[^() ]+|[\w_]+)\s*'
    return re.findall(pattern, rule_string)

def create_operator_node(operators, operands):
    op = operators.pop()  # Get the operator
    right = operands.pop()  # Right operand
    left = operands.pop()  # Left operand
    operands.append(Node("operator", left=left, right=right, value=op))

def create_rule(rule_string):
    tokens = tokenize(rule_string)
    operators = []  # Stack for operators (AND/OR)
    operands = []   # Stack for operands (conditions or other expressions)

    precedence = {'AND': 2, 'OR': 1}  # Precedence of operators
    i = 0
    
    while i < len(tokens):
        token = tokens[i]
        
        if token == '(':
            # If the token is '(', we look for the complete expression within it
            start = i + 1  # Start looking after '('
            balance = 1  # To keep track of parentheses balance
            while balance > 0 and i < len(tokens) - 1:
                i += 1
                if tokens[i] == '(':
                    balance += 1
                elif tokens[i] == ')':
                    balance -= 1
            # Extract the full expression within parentheses
            expression = ' '.join(tokens[start:i])
            operands.append(create_rule(expression))  # Recursively create the subtree
        elif token in precedence:
            while (operators and operators[-1] != '(' and 
                   precedence[operators[-1]] >= precedence[token]):
                create_operator_node(operators, operands)
            operators.append(token)
        elif i + 2 < len(tokens) and tokens[i + 1] in ['>', '<', '>=', '<=', '==', '!=']:
            # Handle full operand including the operator and value
            full_operand = f"{token} {tokens[i + 1]} {tokens[i + 2]}"
            operands.append(Node("operand", value=full_operand))
            i += 2  # Skip the operator and the next value
        else:
            # If it's a standalone identifier (shouldn't happen in this case)
            operands.append(Node("operand", value=token))
        i += 1

    while operators:
        create_operator_node(operators, operands)

    return operands[0] if operands else None  # Return the root of the AST or None




def combine_rules(rules):
    operator_count = {'AND': 0, 'OR': 0}

    # Count the frequency of operators in the provided rules
    for rule in rules:
        tokens = tokenize(rule)
        for token in tokens:
            if token in operator_count:
                operator_count[token] += 1

    # Choose the most frequent operator to combine rules
    main_operator = 'OR' if operator_count['OR'] >= operator_count['AND'] else 'AND'
    
    combined_operands = []

    for rule in rules:
        ast = create_rule(rule)  # Ensure this returns a Node, not a coroutine
        combined_operands.append(ast)

    # Combine all ASTs based on the main operator
    root = combined_operands.pop(0)
    while combined_operands:
        next_operand = combined_operands.pop(0)
        root = Node("operator", left=root, right=next_operand, value=main_operator)

    return root



def node_to_dict(node):
    """Convert a Node object to a dictionary representation."""
    if node is None:
        return None
    return {
        "node_type": node.node_type,
        "value": node.value,
        "left": node_to_dict(node.left),
        "right": node_to_dict(node.right)
    }





def evaluate_node(node, data):
    # Check if the node is an operator
    if node.node_type == "operator":
        if node.value in ("AND", "OR"):
            # Evaluate left and right children
            left_eval = evaluate_node(node.left, data)
            right_eval = evaluate_node(node.right, data)

            if node.value == "AND":
                return left_eval and right_eval
            elif node.value == "OR":
                return left_eval or right_eval
        else:
            raise ValueError(f"Unexpected operator: {node.value}")

    # Check if the node is an operand
    elif node.node_type == "operand":
        # Ensure that node.value is not empty and contains an operator
        if not node.value or len(node.value.split()) < 3:
            raise ValueError(f"Unexpected operand format: {node.value}")

        # Split the value into left operand, operator, and right operand
        parts = re.split(r'\s*(==|!=|>=|<=|>|<)\s*', node.value)
        if len(parts) != 3:
            raise ValueError(f"Unexpected operand format: {node.value}")

        left, operator, right = parts

        # Strip any whitespace around the values
        left = left.strip()
        right = right.strip()

        # Get the actual values from the data dictionary
        left_value = data.get(left, None)
        right_value = eval(right) if right.isdigit() else right.strip("'")

        # Perform the comparison
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

