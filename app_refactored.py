import streamlit as st
from config import MONGODB_URI, DB_NAME, DB_COLLECTION, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from pymongo import MongoClient
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json

# Create sidebars with inputs for both MongoDB and Neo4j
database_mode = st.sidebar.radio("Select Database", ["MongoDB", "Neo4j"]) # Create a selector for either MongoDB or Neo4j
collection = None  # Initialize collection variable

def neo4j_query_14(driver):
    """Actor con más películas"""
    query = """
    MATCH (a:Actor)-[:A_JOUE]->(f:Film)
    RETURN a.name AS actor, COUNT(f) AS film_count
    ORDER BY film_count DESC
    LIMIT 1
    """
    with driver.session() as session:
        result = session.run(query)
        return result.single()

# Imports data from MongoDB to Neo4j
def import_to_neo4j(driver, mongo_data):
    with driver.session() as session:
        for doc in mongo_data:
            try:
                # Asegurarse de que los campos requeridos existan
                film_id = str(doc.get("_id", ""))
                title = doc.get("title", "Unknown Title")
                year = doc.get("year", 0)
                votes = doc.get("Votes", 0)
                revenue = doc.get("Revenue", 0)
                rating = doc.get("rating", 0.0)
                
                # Validar tipos de datos
                try:
                    year = int(year) if year else 0
                except (ValueError, TypeError):
                    year = 0
                
                # Node Films (con manejo de campos faltantes)
                session.run("""
                    MERGE (f:Film {id: $id})
                    SET f.title = $title,
                        f.year = $year,
                        f.Votes = $votes,
                        f.Revenue = $revenue,
                        f.rating = $rating
                """, id=film_id, title=title, year=year, votes=votes, 
                    revenue=revenue, rating=rating)

                # Nodes Réalisateur and relation (solo si existe director)
                if "director" in doc and doc["director"]:
                    director = doc["director"]
                    session.run("""
                        MERGE (r:Realisateur {name: $director})
                        MERGE (f:Film {id: $id})
                        MERGE (r)-[:A_REALISE]->(f)
                    """, director=director, id=film_id)

                # Nodes Acteurs and relation (solo si existen actores)
                actors = doc.get("actors", [])
                if isinstance(actors, list):
                    for actor in actors:
                        if actor:  # Solo si el nombre no está vacío
                            session.run("""
                                MERGE (a:Actor {name: $actor})
                                MERGE (f:Film {id: $id})
                                MERGE (a)-[:A_JOUE]->(f)
                            """, actor=actor, id=film_id)

            except Exception as e:
                st.error(f"Erreur lors de l'importation du document {doc.get('_id', 'inconnu')}: {e}")
                st.error(f"Document problématique: {doc}")


st.header("NoSQL Project - MongoDB and Neo4j Integration")

def mongo_query_1(collection):
    """Year with most film releases"""
    pipeline = [
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    return list(collection.aggregate(pipeline))[0]


# Database mode case for MongoDB
if database_mode == "MongoDB":

    st.sidebar.title("MongoDB") # Add a sidebar title label for MongoDB
    mongodb_host = MONGODB_URI #  host URI
    mongodb_database = DB_NAME #  database name
    mongodb_collection = DB_COLLECTION #  collection name

    collection = None  # Reset collection variable for MongoDB mode

    
    # Launch an instance of the MongoDB database when each requirement is fulfilled
    if mongodb_host and mongodb_database and mongodb_collection: 
        try:
            client = MongoClient(mongodb_host) # Establish connection to client
            db = client[mongodb_database] # Connect to client database
            collection = db[mongodb_collection] # Connect to database collection
            st.success(f"Connected to {mongodb_database}.{mongodb_collection}") # Return successful connection status to database.collection
        except Exception as e:
            st.error(f"Failed to connect to MongoDB: {e}") # Return a connection error
    
    # Build the text interface for MongoDB

    st.markdown("Enter a MongoDB query in MQL format")
    mongo_input = st.text_area("MongoDB Query", height=100)

    # Handle the input and display the returned result
    if st.button("Run Command"):

        # Check if the collection exists
        if collection is None:
            st.error("No collection selected.") # No collection warning

        # Check if the entry is empty
        elif not mongo_input.strip():
            st.warning("Please enter a MongoDB command.") # No entry warning

        # Run the query
        else:
            try:
                
                # Restrict eval to only the collection object as to prevent malicious queries
                safe_globals = {"__builtins__": {}}
                safe_locals = {"collection": collection}

                # Execute the user's command
                result = eval(mongo_input, safe_globals, safe_locals)

                # Convert to list if result is an iterable (e.g., cursor)
                if hasattr(result, "__iter__") and not isinstance(result, dict):
                    result = list(result)

                st.success("Query executed successfully.") # Output a success flag when the query runs without errors
                st.write(result) # Write the query to MongoDB

                # Display result as a table if it's a list of documents
                if isinstance(result, list) and len(result) > 0:
                    df = pd.DataFrame(result) # Instantiate the dataframe based on query result data
                    st.dataframe(df) # Display the dataframe on streamlit

                    # Plot a histogram only if 'year' is in the result and numeric
                    if "year" in df.columns and pd.api.types.is_numeric_dtype(df["year"]):
                        st.subheader("Number of Films Per Year")
                        figure, axes = plt.subplots()  # Create the plot canvas
                        sns.histplot(df["year"].dropna(), bins=20, discrete=True, ax=axes)  # Plot histogram for 'year'
                        axes.set_xlabel("Year")  # Label x-axis with 'Year'
                        axes.set_ylabel("Number of Films")  # Generic y-axis label
                        st.pyplot(figure)  # Display the plot in Streamlit
                    else:
                        st.info("No numeric 'year' field found in the query result.") # Unplottable histogram error

            except Exception as e:
                st.error(f"Error executing command: {e}") # Failed query error

# Database mode case for Neo4j
elif database_mode == "Neo4j":
    # Connection details from config.py
    st.sidebar.title("Neo4j")  
    neo4j_host = NEO4J_URI
    neo4j_username = NEO4J_USERNAME
    neo4j_password = NEO4J_PASSWORD 

    # Verify fields are filled 
    if neo4j_host and neo4j_username and neo4j_password:
        try:
            # Connect to Neo4j database
            driver = GraphDatabase.driver(neo4j_host, auth=(neo4j_username, neo4j_password))
            st.success("Connected to Neo4j")  # Success message
            collection = None  # Reset collection variable for Neo4j mode

            # First establish MongoDB connection
            try:
                mongo_client = MongoClient(MONGODB_URI)
                db = mongo_client[DB_NAME]
                collection = db[DB_COLLECTION]
                
                # Add import button
                if st.button("Import Data from MongoDB to Neo4j"):
                    with st.spinner("Importing data..."):
                        import_to_neo4j(driver, collection.find())
                    st.success("Data imported successfully!")
                    
            except Exception as e:
                st.error(f"Failed to connect to MongoDB: {e}")
            
        except Exception as e:
            st.error(f"Failed to connect to Neo4j: {e}")  
            driver = None  # Avoid executing queries if connection fails

    # Cypher query input

    st.markdown("Enter a Neo4j query in Cypher format")
    neo4j_input = st.text_area("Cypher Query", height=100)

    # Button to execute queries
    if st.button("Run Cypher Command"):
        if driver is None:
            st.error("No active Neo4j connection.") 
        elif not neo4j_input.strip():
            st.warning("Please enter a Cypher query.")  # No entry warning
        else:
            try:
                with driver.session() as session:
                    result = session.run(neo4j_input) # Execute the Cypher query
                    data = [record.data() for record in result]  # Transform result into a list of dictionaries

                    st.success("Query executed successfully.")  
                    st.write(data)  # Show results

                    # Transform data into a DataFrame for display
                    if data:
                        df = pd.DataFrame(data)
                        st.dataframe(df)  # Show table in Streamlit
                    else:
                        st.info("Query returned no results.")  # No results warning
            except Exception as e:
                st.error(f"Error executing Cypher query: {e}") 



