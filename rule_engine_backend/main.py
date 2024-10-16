from fastapi import FastAPI, HTTPException
from bson.objectid import ObjectId
from models import RuleInput
from models import EvaluateData
from models import CombinedRules
from db import rules_collection
from pydantic import BaseModel
from fastapi import Body
from utils import Node, create_rule, combine_rules, evaluate_rule

app = FastAPI()


# Step 3: Store Rule AST in MongoDB
@app.post("/create_rule/")
async def create_rule_api(rule_input: RuleInput):
    try:
        # Access the rule_string from the input object
        rule_string = rule_input.rule_string
        
        # Generate the AST from the rule string
        ast = create_rule(rule_string)
        
        # Convert the AST to a dictionary format for storage
        ast_serialized = ast.to_dict()
        
        # Print the AST for debugging purposes
        print(ast_serialized)  # This will show the complete nested structure in the console

        # Store the rule and its AST in MongoDB
        result = rules_collection.insert_one({"rule_string": rule_string, "ast": ast_serialized})
        
        return {"id": str(result.inserted_id), "message": "Rule created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating rule: {str(e)}")



@app.post("/combine_rules/")
async def combine_rules_api(rules: CombinedRules):
    try:
        # Combine the rules directly using the existing combine_rules method
        combined_ast = combine_rules(rules.rules)

        # Convert the combined AST to a dictionary format for storage
        combined_ast_serialized = combined_ast.to_dict()  # Assuming to_dict method exists

        # Print the combined AST for debugging purposes
        print(combined_ast_serialized)  # This will show the complete nested structure in the console

        # Store the combined rules and their AST in MongoDB
        result = rules_collection.insert_one({"combined_rules": rules.rules, "ast": combined_ast_serialized})

        return {
            "id": str(result.inserted_id),
            "message": "Combined rule created successfully",
            "combined_ast": combined_ast_serialized
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error combining rules: {str(e)}")




# Step 5: Evaluate Rule against Data
@app.post("/evaluate_rule/{rule_id}")
async def evaluate_rule_api(rule_id: str, data: EvaluateData):
    try:
        rule_data = rules_collection.find_one({"_id": ObjectId(rule_id)})
        if not rule_data:
            raise HTTPException(status_code=404, detail=f"Rule with ID '{rule_id}' not found")

        # Retrieve the AST from the stored document and reconstruct the Node objects
        ast_dict = rule_data["ast"]
        ast_root = Node.from_dict(ast_dict)  # Assuming you implement a from_dict method to deserialize

        # Evaluate the rule using the existing logic
        evaluation_result = evaluate_rule(ast_root, data.data)  # Ensure evaluate_rule takes a Node and dict
        return {"evaluation_result": evaluation_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating rule: {str(e)}")


# Start the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
