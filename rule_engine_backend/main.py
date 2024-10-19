from fastapi import FastAPI, HTTPException
from bson.objectid import ObjectId
from models import RuleInput
from models import EvaluateData
from models import CombinedRules
from db import rules_collection
from fastapi import Body
from utils import Node, create_rule, combine_rules, evaluate_rule

app = FastAPI()
def print_ast(node, level=0):
    if node is not None:
        print(' ' * (level * 4) + f"{node.node_type}: {node.value}")
        print_ast(node.left, level + 1)
        print_ast(node.right, level + 1)

@app.post("/create_rule/")
async def create_rule_api(rule_input: RuleInput):
    try:
        rule_string = rule_input.rule_string
        ast = create_rule(rule_string)
        
        print_ast(ast)
        ast_serialized = ast.to_dict()
        print(ast_serialized) 
        result = rules_collection.insert_one({"rule_string": rule_string, "ast": ast_serialized})
        
        return {"id": str(result.inserted_id), "message": "Rule created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating rule: {str(e)}")



@app.post("/combine_rules/")
async def combine_rules_api(rules: CombinedRules):
    try:
        combined_ast = combine_rules(rules.rules)
        print_ast(combined_ast)
        combined_ast_serialized = combined_ast.to_dict()  

        print(combined_ast_serialized) 
        result = rules_collection.insert_one({"combined_rules": rules.rules, "ast": combined_ast_serialized})

        return {
            "id": str(result.inserted_id),
            "message": "Combined rule created successfully",
            "combined_ast": combined_ast_serialized
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error combining rules: {str(e)}")


@app.post("/evaluate_rule/{rule_id}")
async def evaluate_rule_api(rule_id: str, data: EvaluateData):
    try:
        rule_data = rules_collection.find_one({"_id": ObjectId(rule_id)})
        if not rule_data:
            raise HTTPException(status_code=404, detail=f"Rule with ID '{rule_id}' not found")
        ast_dict = rule_data["ast"]
        ast_root = Node.from_dict(ast_dict) 
        evaluation_result = evaluate_rule(ast_root, data.data)  # Ensure evaluate_rule takes a Node and dict
        return {"evaluation_result": evaluation_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating rule: {str(e)}")


# Start the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
