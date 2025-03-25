from pymongo import MongoClient
from neo4j import GraphDatabase
import ast

print("\nType 'exit' at any time to quit.")
print("------------------------------------------------\n")

# Interactive Loop
while True:
    mode = input("\nWhich database do you want to query? (mongo/neo4j): ").strip().lower()
    if mode == "exit":
        break

    if mode == "mongo":
        
        # MongoDB Setup
        MONGO_URI = input("Enter MongoDB URI (default: mongodb://localhost:27017): ") or "mongodb://localhost:27017"
        mongo_client = MongoClient(MONGO_URI)

        db_name = input("Enter MongoDB database name: ")
        collection_name = input("Enter MongoDB collection name: ")
        mongo_collection = mongo_client[db_name][collection_name]

        print("\nExample: {'year': {'$gt': 2000}}")
        query_input = input("Enter MongoDB find() query as a Python dict: ")
        if query_input.lower() == "exit":
            break
        try:
            query = ast.literal_eval(query_input)
            results = mongo_collection.find(query).limit(10)
            for doc in results:
                print(doc)
        except Exception as e:
            print("⚠️ Error parsing or running MongoDB query:", e)

    elif mode == "neo4j":
        # Neo4j Setup
        NEO4J_URI = input("Enter Neo4j bolt URI (default: bolt://localhost:7687): ") or "bolt://localhost:7687"
        NEO4J_USER = input("Enter Neo4j username: ")
        NEO4J_PASS = input("Enter Neo4j password: ")

        neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

        print("\nExample: MATCH (m:Film) RETURN m.title, m.year LIMIT 5")
        cypher_query = input("Enter Neo4j Cypher query: ")
        if cypher_query.lower() == "exit":
            break
        try:
            with neo4j_driver.session() as session:
                result = session.run(cypher_query)
                for record in result:
                    print(dict(record))
        except Exception as e:
            print("⚠️ Error running Neo4j query:", e)
    else:
        print("Please choose either 'mongo' or 'neo4j'.")

# Cleanup
mongo_client.close()
neo4j_driver.close()
print("\n✅ Connections closed. Goodbye!")
