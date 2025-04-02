import pymongo
from neo4j import GraphDatabase
from tqdm import tqdm
from pymongo.errors import PyMongoError
from neo4j.exceptions import Neo4jError
from config import MONGODB_URI, DB_NAME, DB_COLLECTION, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

# MongoDB Connection
client = pymongo.MongoClient(MONGODB_URI)
db = client[DB_NAME]
films = db[DB_COLLECTION]

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def clear_neo4j():
    try:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("Neo4j database cleared successfully.")
    except Neo4jError as e:
        print(f"Error clearing Neo4j database: {e}")


def safe_float(value, default=0.0):

                try:
                    return float(value) if value else default
                except (ValueError, TypeError):
                    return default

def safe_int(value, default=0):
    try:
        if isinstance(value, str):
            value = value.replace(',', '')
        return int(float(value)) if value and str(value).strip() not in ['', 'N/A'] else default
    except (ValueError, TypeError):
        return default

def import_data():
    # Create constraints
    constraints = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Film) REQUIRE f.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Actor) REQUIRE a.name IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Director) REQUIRE d.name IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE"
    ]

    try:
        with driver.session() as session:
            for constraint in constraints:
                session.run(constraint)
    except Neo4jError as e:
        print(f"Error creating constraints: {e}")
        return

    # Process each film document
    try:
        for film in tqdm(films.find(), total=films.count_documents({}), desc="Importing data"):


            # Then in your film_data:
            film_data = {
                "id": str(film.get("_id", "")),
                "title": film.get("title") or film.get("Title", "Unknown"),
                "year": safe_int(film.get("year")),
                "votes": safe_int(film.get("Votes")),
                "revenue": safe_float(film.get("revenue") or film.get("Revenue (Millions)")),
                "rating": film.get("rating", ""),
                "metascore": safe_int(film.get("Metascore")),
                "runtime": safe_int(film.get("runtime_minutes") or film.get("Runtime (Minutes)")),
                "director": film.get("director") or film.get("Director", "Unknown"),
                "actors": film.get("actors") or film.get("Actors", ""),
                "genres": film.get("genre") or film.get("Genre", "")
            }
            print(f"Processed votes value: {film_data['votes']}")
            with driver.session() as session:
                session.run("""
                    MERGE (f:Film {id: $id})
                    SET f.title = $title,
                        f.year = $year,
                        f.votes = $votes,
                        f.revenue = $revenue,
                        f.rating = $rating,
                        f.metascore = $metascore,
                        f.runtime = $runtime
                """, film_data)

                if film_data["director"]:
                    session.run("""
                        MERGE (d:Director {name: $director})
                        MERGE (f:Film {id: $id})
                        MERGE (d)-[:DIRECTED]->(f)
                    """, film_data)

                if film_data["actors"]:
                    actors = [a.strip() for a in film_data["actors"].split(",") if a.strip()]
                    for actor in actors:
                        session.run("""
                            MERGE (a:Actor {name: $actor})
                            MERGE (f:Film {id: $id})
                            MERGE (a)-[:ACTED_IN]->(f)
                        """, {"id": film_data["id"], "actor": actor})


                if film_data["genres"]:
                    genres = [g.strip() for g in film_data["genres"].split(",") if g.strip()]
                    for genre in genres:
                        session.run("""
                            MERGE (g:Genre {name: $genre})
                            MERGE (f:Film {id: $id})
                            MERGE (f)-[:HAS_GENRE]->(g)
                        """, {"id": film_data["id"], "genre": genre})


        with driver.session() as session:
            session.run("""
                MERGE (you:Actor {name: $name})
                MERGE (f:Film {title: $title})
                MERGE (you)-[:ACTED_IN]->(f)
            """, {
                "name": "Carlota",
                "title": "Avatar"
            })

        print("Data import completed successfully!")

    except (PyMongoError, Neo4jError, ValueError) as e:
        print(f"Error during data import: {e}")

if __name__ == "__main__":
    print("Starting data migration from MongoDB to Neo4j...")
    clear_neo4j()
    import_data()
    driver.close()
