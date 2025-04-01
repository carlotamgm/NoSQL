import streamlit as st
from config import MONGODB_URI, DB_NAME, DB_COLLECTION, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from mongodb_queries import QUERIES  # Import the QUERIES dictionary from mongodb_queries.py
from pymongo import MongoClient
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd 

# Create sidebars with inputs for both MongoDB and Neo4j
database_mode = st.sidebar.radio("Select Database", ["MongoDB", "Neo4j"]) # Create a selector for either MongoDB or Neo4j
collection = None  # Initialize collection variable

# Executes MongoDB queries based on the selected query name and on its type (aggregate, count, find)
def execute_mongo_query(
    collection,
    query_name: str,
    limit: int = None,
    result_as_dataframe: bool = True
):
    if query_name not in QUERIES:
        raise ValueError(f"Unknown query: {query_name}")
    
    query_info = QUERIES[query_name]
    query = query_info["query"]
    
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
        
        return pd.DataFrame(result) if result_as_dataframe and result else result
    
    except Exception as e:
        raise Exception(f"Error executing {query_name}: {str(e)}")

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

if database_mode == "MongoDB":
    st.sidebar.title("MongoDB")
    mongodb_host = MONGODB_URI
    mongodb_database = DB_NAME
    mongodb_collection = DB_COLLECTION
    collection = None

    # Connection to MongoDB
    if mongodb_host and mongodb_database and mongodb_collection: 
        try:
            client = MongoClient(mongodb_host)
            db = client[mongodb_database]
            collection = db[mongodb_collection]
            st.success(f"Connected to {mongodb_database}.{mongodb_collection}")
        except Exception as e:
            st.error(f"Failed to connect to MongoDB: {e}")

    st.header("Predefined MongoDB Queries")
    
    # Crear opciones para el selectbox
    query_options = {
        f"{v['description']} ({k})": k 
        for k, v in QUERIES.items()
    }
    
    selected_query_label = st.selectbox(
        "Choose a predefined query:",
        options=list(query_options.keys())
    )
    
    # Obtener la clave real de la query seleccionada
    query_key = query_options[selected_query_label]
    query_info = QUERIES[query_key]
    
    # Add limit parameter to find queries
    limit = None
    if query_info["type"] == "find":
        limit = st.number_input(
            "Maximum results to show", 
            min_value=1, 
            max_value=1000, 
            value=10
        )
    
    # Button to execute predefined queries
    if st.button(f"Execute: {selected_query_label.split(' (')[0]}"):
        if collection is None:
            st.error("No MongoDB connection established")
        else:
            try:
                result = execute_mongo_query(
                    collection,
                    query_name=query_key,
                    limit=limit
                )
                
                # Show results of query
                if query_info["type"] == "count":
                    st.metric(label=query_info["description"], value=result)
                # Query 4: Create an histogram with the number of films per year
                if query_key == "films_per_year":
                    st.write(result)
                    plt.figure(figsize=(12, 6))
                    sns.barplot(x=result["_id"], y=result["titles"].apply(len), color="blue")
                    plt.xticks(rotation=45)
                    plt.xlabel("Year")
                    plt.ylabel("Number of Films")
                    plt.title("Number of Films Released per Year")

                    st.pyplot(plt)
                elif isinstance(result, pd.DataFrame):
                    st.dataframe(result)
            
                else:
                    st.json(result)
                    
            except Exception as e:
                st.error(f"Error executing query: {str(e)}")

    # Sección para queries personalizadas
    st.header("Custom MongoDB Query")
    mongo_input = st.text_area("Enter MQL query (e.g., {'year': 2005})", height=100)
    
    if st.button("Run Custom Query"):
        if collection is None:
            st.error("No collection selected.")
        elif not mongo_input.strip():
            st.warning("Please enter a MongoDB query.")
        else:
            try:
                # Ejecutar query personalizada
                safe_globals = {"__builtins__": {}}
                safe_locals = {"collection": collection}
                result = eval(mongo_input, safe_globals, safe_locals)
                
                # Convertir resultados
                if hasattr(result, "__iter__") and not isinstance(result, dict):
                    result = list(result)
                
                st.success("Query executed successfully.")
                
                # Mostrar resultados
                if isinstance(result, list) and result:
                    df = pd.DataFrame(result)
                    st.dataframe(df)
                    
                    # Visualización automática para datos numéricos
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if not numeric_cols.empty:
                        selected_col = st.selectbox("Select column to visualize", numeric_cols)
                        fig, ax = plt.subplots()
                        sns.histplot(df[selected_col].dropna(), ax=ax)
                        st.pyplot(fig)
                else:
                    st.write(result)
                    
            except Exception as e:
                st.error(f"Error executing command: {e}")

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



