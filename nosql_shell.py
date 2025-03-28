from pymongo import MongoClient
from neo4j import GraphDatabase
import ast

mongo_client = None
neo4j_driver = None
mongo_collection = None

# Interactive Loop
while True:
    
    # Create input selector prompt for the user
    mode = input("\nWhich database do you want to query? (mongo/neo4j/exit): ").strip().lower()
    
    # Exit on user command
    if mode == "exit":
        break

    # Enter a mongoDB database
    if mode == "mongo":
        
        # Select host connection url based on user input (or default localhost configuration)
        MONGO_URI = input("Enter MongoDB URI (default: mongodb://localhost:27017): ") or "mongodb://localhost:27017"
        mongo_client = MongoClient(MONGO_URI)

        # Input desired database and collection names
        db_name = input("Enter MongoDB database name: ")
        collection_name = input("Enter MongoDB collection name: ")
        mongo_collection = mongo_client[db_name][collection_name]

        # Prompt user commands, and provide query example (note, this will need to be adjusted to perform queries other than .find())
        print("\nType 'exit' to return to main menu.")
        print("Example: find({'year': {'$gt': 2000}}, {'title': 1, '_id': 0})")

        # Conditional while loop based on user input
        while True:
            cmd = input("Enter MongoDB find() command or 'exit': ")
            if cmd.lower() == "exit":
                break
            try:
                results = eval(f"mongo_collection.{cmd}")
                for doc in results:
                    print(doc)
            except Exception as e:
                print("Error running MongoDB command:", e)

    # Enter a neo4j database
    elif mode == "neo4j":
        
        # Select host for Neo4j based on user input
        NEO4J_URI = input("Enter Neo4j bolt URI (default: bolt://localhost:7687): ") or "bolt://localhost:7687"

        # Enter specific username and password required to connect to Neo4j host
        NEO4J_USER = input("Enter Neo4j username: ")
        NEO4J_PASS = input("Enter Neo4j password: ")
        neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

        # Prompt user commands, including a provided query example
        print("\nType 'exit' to return to main menu.")
        print("Example: MATCH (m:Film) RETURN m.title, m.year LIMIT 5")

        # Conditional while loop based on user input
        while True:
            cypher_query = input("Enter Neo4j Cypher query or 'exit': ")
            if cypher_query.lower() == "exit":
                break
            try:
                with neo4j_driver.session() as session:
                    result = session.run(cypher_query)
                    for record in result:
                        print(dict(record))
            except Exception as e:
                print("Error running Neo4j query:", e)
    
    else:
        # Default case
        print("Please choose either 'mongo', 'neo4j', or 'exit'.")

# Exit respecive databases
if mongo_client:
    mongo_client.close()
if neo4j_driver:
    neo4j_driver.close()

# Goodbye
print("\nConnections closed. Goodbye!")
