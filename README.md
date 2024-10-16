# Rule Engine with AST

## Running the Application

### 1. Setup the Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the FastAPI Server

```bash
uvicorn main:app --reload
```

### 3. MongoDB Setup

Ensure MongoDB is running and configured correctly. The database stores the rules and their AST representations.

## Overview

This project is a Rule Engine that uses an Abstract Syntax Tree (AST) to represent and evaluate dynamic rules. The system is designed to evaluate user eligibility based on various attributes such as age, department, income, and more. It supports the creation, combination, modification, and evaluation of rules, making it a flexible and extensible rule-based decision system.

## Objective

The main objective is to create a 3-tier application consisting of:

1. Simple UI: (Optional) A user-friendly interface to manage rules.
2. API Layer: Using FastAPI to expose rule creation, combination, and evaluation.
3. Backend (Data Layer): A MongoDB database to store rule definitions and their AST representations.

### Features:
- Dynamic creation of rules using an AST structure.
- Combining multiple rules into a single structure.
- Evaluating user data against predefined rules.
- Easy modification and validation of rules.

## Data Structure

### Abstract Syntax Tree (AST)

The AST structure is represented using a Node class with the following fields:

- `type`: Defines the type of node. Either "operator" (AND/OR) or "operand" (condition).
- `left`: Reference to the left child node (for operators).
- `right`: Reference to the right child node (for operators).
- `value`: The operand value (e.g., age > 30 for comparisons).

This flexible structure allows dynamic creation, modification, and combination of rules.

#### Example Node Structure

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

### Data Storage

#### Database: MongoDB

We store the rules and their corresponding AST representations in MongoDB for persistence. The database schema for storing rules looks like:

##### MongoDB Schema

```json
{
  "_id": ObjectId("..."),
  "rule_string": "((age > 30 AND department = 'Marketing')) AND (salary > 20000 OR experience > 5)",
  "ast": {
    "node_type": "operator",
    "value": "AND",
    "left": { ... },
    "right": { ... }
  }
}
```

### Sample Rules

Rule 1:
```
((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)
```

Rule 2:
```
((age > 30 AND department = 'Marketing')) AND (salary > 20000 OR experience > 5)
```

## API Design

The application exposes several APIs to manage and evaluate rules.

### 1. Create Rule (POST /create_rule/)

Creates a new rule based on the input string and stores its AST in the database.

- Input: A string representing the rule (e.g., "age > 30 AND department == 'Sales'").
- Output: A MongoDB ObjectId of the created rule.

### 2. Combine Rules (POST /combine_rules/)

Combines multiple rules into a single AST, choosing the most frequent operator (AND/OR) based on predefined logic.

- Input: A list of rule strings to combine.
- Output: Combined rule stored in MongoDB.

### 3. Evaluate Rule (POST /evaluate_rule/{rule_id})

Evaluates the rule (identified by rule_id) against the given user data.

- Input: A JSON object containing user attributes (e.g., age, department, salary).
- Output: True or False indicating whether the user meets the rule criteria.

### API Example

```json
POST /create_rule/
{
  "rule_string": "age > 30 AND department == 'Marketing'"
}

POST /evaluate_rule/670fda1c6396eb752ed52c53
{
  "data": {
    "age": 35,
    "department": "Sales",
    "salary": 40000,
    "experience": 3
  }
}
```

## Test Cases

1. Create Rule
   - Test creating individual rules using create_rule and verifying their AST representation in MongoDB.

2. Combine Rules
   - Test combining multiple rules using combine_rules. Ensure the combined AST correctly reflects the intended logic.

3. Evaluate Rule
   - Test evaluate_rule with various user data inputs. Check if the rule evaluation returns the expected result (True/False).

4. Invalid Input Handling
   - Test handling of invalid rule strings (e.g., missing operators) and invalid data inputs (e.g., missing attributes).

## Error Handling & Validations

- Implemented error handling for invalid rule formats and missing operators.
- Attribute validation: Ensures that the attributes used in the rule are part of a valid catalog (e.g., age, department, salary).
- Enhanced rule modification: Rules can be modified by changing operators or operand values, or by adding/removing sub-expressions.

## Bonus Features

- User-Defined Functions: Extend the rule system to support user-defined functions for advanced conditions (e.g., complex mathematical expressions or custom checks).

## Conclusion

This Rule Engine with AST is a powerful and flexible system to evaluate user eligibility based on dynamic rules. It supports creating, combining, and evaluating complex conditions, making it highly adaptable to various use cases.
