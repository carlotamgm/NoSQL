import streamlit as st
from config import MONGODB_URI, DB_NAME, DB_COLLECTION, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from mongodb_queries import QUERIES  
from neo4j_queries import QUERIES as NEO4J_QUERIES  
from pymongo import MongoClient
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd 

# Sidebar selection for database mode
database_mode = st.sidebar.radio("Select Database", ["MongoDB", "Neo4j"])
collection = None  

# Function to execute MongoDB queries with optional parameters
def execute_mongo_query(collection, query_name: str, limit: int = None, parameters: dict = None):
    if query_name not in QUERIES:
        raise ValueError(f"Unknown query: {query_name}")
    
    query_info = QUERIES[query_name]
    query = query_info["query"]

    # Replace placeholders in queries with provided parameters
    if parameters:
        for key, value in parameters.items():
            query = query.replace(f"{{{key}}}", value)

    try:
        if query_info["type"] == "aggregate":
            result = list(collection.aggregate(query))
        elif query_info["type"] == "count":
            return collection.count_documents(query)
        elif query_info["type"] == "find":
            find_args = {"filter": query}
            if "projection" in query_info:
                find_args["projection"] = query_info["projection"]
            if limit:
                find_args["limit"] = limit
            result = list(collection.find(**find_args))
        else:
            raise ValueError(f"Unsupported query type: {query_info['type']}")

        return pd.DataFrame(result) if result else result
    
    except Exception as e:
        st.error(f"Error executing {query_name}: {str(e)}")
        return None

st.header("NoSQL Project - MongoDB and Neo4j Integration")

# MongoDB section
if database_mode == "MongoDB":
    st.sidebar.title("MongoDB")
    mongodb_host = MONGODB_URI
    mongodb_database = DB_NAME
    mongodb_collection = DB_COLLECTION

    # Connect to MongoDB
    if mongodb_host and mongodb_database and mongodb_collection: 
        try:
            client = MongoClient(mongodb_host)
            db = client[mongodb_database]
            collection = db[mongodb_collection]
            st.success(f"Connected to {mongodb_database}.{mongodb_collection}")
        except Exception as e:
            st.error(f"Failed to connect to MongoDB: {e}")

    st.header("Predefined MongoDB Queries")
    
    # Create query options for the dropdown
    query_options = {f"{v['description']} ({k})": k for k, v in QUERIES.items()}
    
    selected_query_label = st.selectbox("Choose a predefined query:", options=list(query_options.keys()))
    query_key = query_options[selected_query_label]
    query_info = QUERIES[query_key]

    # Input fields for queries requiring parameters
    query_parameters = {}
    if query_key in ["films_by_director", "films_by_actor"]:
        param_key = "director_name" if query_key == "films_by_director" else "actor_name"
        query_parameters[param_key] = st.text_input(f"Enter {param_key.replace('_', ' ')}:")

    # Limit parameter for 'find' queries
    limit = st.number_input("Maximum results to show", min_value=1, max_value=1000, value=10) if query_info["type"] == "find" else None

    # Button to execute the query
    if st.button(f"Execute: {selected_query_label.split(' (')[0]}"):
        if collection is None:
            st.error("No MongoDB connection established")
        else:
            result = execute_mongo_query(collection, query_key, limit, query_parameters)
            if result is not None:
                if isinstance(result, pd.DataFrame):
                    st.dataframe(result)
                elif isinstance(result, int):
                    st.metric(label=query_info["description"], value=result)
                else:
                    st.json(result)

    # Custom query input
    st.header("Custom MongoDB Query")
    mongo_input = st.text_area("Enter MQL query (e.g., {'year': 2005})", height=100)
    
    if st.button("Run Custom Query"):
        if collection is None:
            st.error("No collection selected.")
        elif not mongo_input.strip():
            st.warning("Please enter a MongoDB query.")
        else:
            try:
                safe_globals = {"__builtins__": {}}
                safe_locals = {"collection": collection}
                result = eval(mongo_input, safe_globals, safe_locals)
                
                if isinstance(result, list) and result:
                    df = pd.DataFrame(result)
                    st.dataframe(df)
                else:
                    st.write(result)
            except Exception as e:
                st.error(f"Error executing command: {e}")

# Neo4j section
elif database_mode == "Neo4j":
    st.sidebar.title("Neo4j")  
    neo4j_host = NEO4J_URI
    neo4j_username = NEO4J_USERNAME
    neo4j_password = NEO4J_PASSWORD 

    # Connect to Neo4j
    if neo4j_host and neo4j_username and neo4j_password:
        try:
            driver = GraphDatabase.driver(neo4j_host, auth=(neo4j_username, neo4j_password))
            st.success("Connected to Neo4j")
        except Exception as e:
            st.error(f"Failed to connect to Neo4j: {e}")  
            driver = None  

    st.header("Predefined Neo4j Queries")
    
    # Create query options for the dropdown
    query_options = {f"{v['description']} ({k})": k for k, v in NEO4J_QUERIES.items()}
    
    selected_query_label = st.selectbox("Choose a predefined query:", options=list(query_options.keys()))
    query_key = query_options[selected_query_label]
    query_neo4j_info = NEO4J_QUERIES[query_key]

    # Input fields for parameterized queries
    query_parameters = {}
    if query_key == "recommended_films_based_on_actor":
        query_parameters["actor_name"] = st.text_input("Enter actor name:")
    elif query_key == "shortest_path_between_actors":
        query_parameters["actor_name1"] = st.text_input("Enter first actor name:")
        query_parameters["actor_name2"] = st.text_input("Enter second actor name:")

    # Button to execute the query
    if st.button(f"Execute: {selected_query_label.split(' (')[0]}"):
        if driver is None:
            st.error("No Neo4j connection established")
        else:
            try:
                with driver.session() as session:
                    if query_key == "recommended_films_based_on_actor":
                        result = session.run(query_neo4j_info["query"], actorName= query_parameters["actor_name"])
                    elif query_key == "shortest_path_between_actors":
                        result = session.run(query_neo4j_info["query"], actorName1=query_parameters["actor_name1"],
                                            actorName2=query_parameters["actor_name2"])
                    else:
                        result = session.run(query_neo4j_info["query"])

                    data = [record.data() for record in result]
                    if data:
                        st.json(data)
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                    else:
                        st.warning("No results found.")
            except Exception as e:
                st.error(f"Error executing query: {str(e)}")

    # Custom Cypher query input
    st.markdown("Enter a Neo4j query in Cypher format")
    neo4j_input = st.text_area("Cypher Query", height=100)

    if st.button("Run Cypher Command"):
        if driver is None:
            st.error("No active Neo4j connection.") 
        elif not neo4j_input.strip():
            st.warning("Please enter a Cypher query.")  
        else:
            try:
                with driver.session() as session:
                    result = session.run(neo4j_input)
                    data = [record.data() for record in result]

                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df)
                    else:
                        st.info("Query returned no results.")
            except Exception as e:
                st.error(f"Error executing Cypher query: {e}")  
