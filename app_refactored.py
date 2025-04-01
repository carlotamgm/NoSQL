import streamlit as st
from pymongo import MongoClient
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json

# Add a sidebar title label
st.sidebar.title("MongoDB")

# Collect the host URI
mongodb_host = st.sidebar.text_input("MongoDB Host URI")

# Collect database name
mongodb_database = st.sidebar.text_input("Database Name")

# Collect collection name
mongodb_collection = st.sidebar.text_input("Collection Name")

# Introduce a default case
collection = None

# Launch an instance of the MongoDB databse when each requirement is fulfilled
if mongodb_host and mongodb_database and mongodb_collection:
    try:
        client = MongoClient(mongodb_host) # Establish connection to client
        db = client[mongodb_database] # Connect to client database
        collection = db[mongodb_collection] # Connect to database collection
        st.success(f"Connected to {mongodb_database}.{mongodb_collection}") # Return successful conncection status to database.collection
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}") # Return a connection error

# Build the text input for queries into the specified MongoDB database
st.header("MongoDB Shell")
st.markdown("Enter MongoDB command in MQL format")
user_input = st.text_area("MongoDB Query", height=100)

# Handle the input and display the returned result
if st.button("Run Command"):
    # Check if the collection exists
    if collection is None:
        st.error("No collection selected.") # No collection warning
    # Check for whitespace in entry
    elif not user_input.strip():
        st.warning("Please enter a MongoDB command.") # No entry warning
    # Run the query
    else:
        try:
            # Restrict eval to only the collection object as to prevent malicious queries
            safe_globals = {"__builtins__": {}}
            safe_locals = {"collection": collection}

            # Execute the user's command
            result = eval(user_input, safe_globals, safe_locals)

            # Convert to list if result is an iterable (e.g., cursor)
            if hasattr(result, "__iter__") and not isinstance(result, dict):
                result = list(result)

            st.success("Query executed successfully.") # Output a success flag when the query runs without errors
            st.write(result) # Write the query to MongoDB

            # Display result as a table if it's a list of documents
            if isinstance(result, list) and len(result) > 0:
                df = pd.DataFrame(result) # Instantiate the datafram based on query result data
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
                    st.info("No numeric 'year' field found in the query result.")

        except Exception as e:
            st.error(f"Error executing command: {e}")
