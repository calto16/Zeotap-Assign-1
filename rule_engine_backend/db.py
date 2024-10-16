from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["rule_engine"]
rules_collection = db["rules"]