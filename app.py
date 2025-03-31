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
mongodb_database = "entertainment"

# Collect collection name
mongodb_collection = "films"

# Introduce a default case
collection = None

# Import data from json file
decoder = json.JSONDecoder()
with open('movies.json') as f:
    movies_data = f.read()
    pos = 0
    movies = []
    while pos < len(movies_data):
        try:
            movie, pos = decoder.raw_decode(movies_data, pos)
            movies.append(movie)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            break

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
# Mongo query
if user_input:
    try:
        # Execute the query
        result = collection.command(user_input) if user_input else None

        # Display the result
        if result:
            st.json(result)
        else:
            st.info("No results found.")
    except Exception as e:
        st.error(f"Error executing query: {e}")