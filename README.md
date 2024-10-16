# Rule Engine with AST

## Running the Application

### 1. Setup the Environment
First, create a virtual environment and install the required dependencies.

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the FastAPI Server
Once the environment is set up, run the FastAPI application.

```bash
uvicorn main:app --reload
```

### 3. MongoDB Setup
Make sure MongoDB is installed and running on your local machine or accessible via a cloud instance. The database stores the rules and their AST representations.

## Overview
This project is a Rule Engine built using FastAPI and MongoDB that allows for the creation, combination, and evaluation of dynamic rules using an Abstract Syntax Tree (AST) structure. The engine evaluates user eligibility based on conditions such as age, department, salary, and other user attributes.

The application exposes a REST API to manage rules and supports storing rule structures in MongoDB in a serialized form. This engine is highly adaptable and performant due to FastAPI's asynchronous capabilities and MongoDB's flexibility.

## Objective
The core goal of this project is to develop a 3-tier rule engine application with:

1. UI Layer: (Optional) User interface for creating, managing, and evaluating rules.
2. API Layer: Using FastAPI, a modern, high-performance web framework for API endpoints.
3. Data Layer: MongoDB for storing rules, AST representations, and application metadata.

## Design Choices

### Abstract Syntax Tree (AST)
The AST is central to the application, as it allows dynamic creation and evaluation of complex rules. The AST structure is represented using a Node class with the following fields:

- `node_type`: Identifies if the node is an operator (AND, OR) or an operand (condition like age > 30).
- `left`: Refers to the left child node (for operators).
- `right`: Refers to the right child node (for operators).
- `value`: The actual condition or comparison (e.g., age > 30).

#### Node Structure Example:
```json
{
  "node_type": "operator",
  "value": "AND",
  "left": {
    "node_type": "operand",
    "value": "age > 30"
  },
  "right": {
    "node_type": "operand",
    "value": "department == 'Marketing'"
  }
}
```

## API Design
The following API endpoints have been developed to handle the rule engine's functionality:

### 1. Create Rule (POST /create_rule/)
This endpoint creates a new rule based on the input rule string, generates its AST, and stores it in MongoDB.

**Input**: A string representing the rule.
```json
{
  "rule_string": "age > 30 AND department == 'Sales'"
}
```

**Output**: A MongoDB ObjectId of the created rule.
```json
{
  "id": "670fda1c6396eb752ed52c53",
  "message": "Rule created successfully"
}
```

### 2. Combine Rules (POST /combine_rules/)
Combines multiple rules into a single AST, minimizing redundant checks, and stores the combined rule in MongoDB.

**Input**: A list of rule strings.
```json
{
  "rules": [
    "age > 30 AND department == 'Sales'",
    "salary > 20000 OR experience > 5"
  ]
}
```

**Output**: Combined rule AST stored in MongoDB.
```json
{
  "message": "Rules combined and stored"
}
```

### 3. Evaluate Rule (POST /evaluate_rule/{rule_id})
Evaluates a user's data against the rule with the provided rule_id. The AST for the rule is deserialized from MongoDB, and the rule is evaluated against the user data.

**Input**: A JSON object containing user attributes (e.g., age, department, salary).
```json
{
  "data": {
    "age": 35,
    "department": "Sales",
    "salary": 40000,
    "experience": 3
  }
}
```

**Output**: True or False based on whether the user meets the rule criteria.
```json
{
  "evaluation_result": true
}
```

### API Testing with Swagger
FastAPI automatically generates API documentation, which can be accessed at:

- Local Testing: http://localhost:8000/docs

This provides an interactive UI where you can test API endpoints directly.

## Serialization & Deserialization
The rule AST is serialized into a dictionary format for storage in MongoDB and deserialized when retrieving the rule for evaluation. This enables easy storage, retrieval, and modification of the AST.

### MongoDB Schema Example:
```json
{
  "_id": ObjectId("670fda1c6396eb752ed52c53"),
  "rule_string": "age > 30 AND department == 'Sales'",
  "ast": {
    "node_type": "operator",
    "value": "AND",
    "left": {
      "node_type": "operand",
      "value": "age > 30"
    },
    "right": {
      "node_type": "operand",
      "value": "department == 'Sales'"
    }
  }
}
```

## AST Logic: Create, Combine, and Evaluate

### 1. Create Rule
- The rule string is tokenized into individual components.
- An AST is constructed based on operators (AND/OR) and conditions (e.g., age > 30).
- The AST is serialized and stored in MongoDB.

### 2. Combine Rules
- Multiple ASTs are combined by identifying the most frequent operator (AND/OR).
- The combined AST is stored in MongoDB, reducing redundancy and improving evaluation efficiency.

### 3. Evaluate Rule
- The user's data (e.g., age, department, salary) is matched against the conditions in the AST.
- The evaluation checks if the data satisfies the rule using comparisons (e.g., age > 30).

## Design Considerations
- **Performance**: FastAPI is used for its speed and asynchronous capabilities, which handle multiple rule evaluations simultaneously, making the system scalable and efficient.
- **Database**: MongoDB is chosen for its flexibility in handling dynamic and nested data structures like ASTs. It also allows fast reads and writes, critical for rule storage and retrieval.
- **Extensibility**: The design allows adding new operators, conditions, and user attributes without significant changes to the underlying logic.

## Error Handling & Validations
- **Invalid Rule Formats**: The application catches errors related to missing operators, invalid comparisons, or unsupported conditions.
- **Attribute Validation**: The attributes used in the rules (e.g., age, salary) are validated against a predefined catalog to ensure consistency.
- **Rule Modification**: Rules can be modified by changing operators or operand values, or by adding/removing sub-expressions within the AST.

## Test Cases
1. **Create Rule**: Test individual rule creation and verify AST representation in MongoDB.
2. **Combine Rules**: Test combining multiple rules and check the resulting AST.
3. **Evaluate Rule**: Test various user data inputs against the rules and validate the evaluation result.
4. **Error Handling**: Test invalid inputs, missing attributes, and malformed rules.

## Performance & FastAPI
FastAPI's asynchronous support allows the application to handle a large number of requests simultaneously. This ensures that rule creation, combination, and evaluation are performed quickly, even with complex rules and large datasets. FastAPI's autogenerated OpenAPI documentation (/docs) also makes it easy to test and debug the application.

## Conclusion
This Rule Engine with AST is a flexible and performant system for dynamically creating, modifying, and evaluating complex rules. It is well-suited for applications where eligibility, validation, or decision-making needs to be determined based on various user attributes. The integration of FastAPI and MongoDB ensures that the system is fast, scalable, and capable of handling complex rule evaluations efficiently.
