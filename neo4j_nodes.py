# Imports data from MongoDB to Neo4j
def import_to_neo4j(driver, mongo_data):
    with driver.session() as session:
        documents = list(mongo_data.clone()) if hasattr(mongo_data, 'clone') else list(mongo_data)
        total_docs = len(documents)
        
        if total_docs == 0:
            print("No hay documentos para importar")
            return

        for i, doc in enumerate(documents):
            try:
                # Extraer campos principales con validación
                film_id = str(doc.get("_id", ""))
                title = str(doc.get("title", "Unknown Title")).strip()
                year = int(doc.get("year", 0)) if str(doc.get("year", "0")).isdigit() else 0
                votes = int(doc.get("Votes", 0)) if str(doc.get("Votes", "0")).isdigit() else 0
                revenue = float(doc.get("Revenue", 0)) if str(doc.get("Revenue", "0")).replace('.','',1).isdigit() else 0.0
                rating = float(doc.get("rating", 0.0)) if str(doc.get("rating", "0.0")).replace('.','',1).isdigit() else 0.0

                
                # Node Films 
                session.run("""
                    MERGE (f:Films {id: $id})
                    SET f.title = $title,
                        f.year = $year,
                        f.Votes = $votes,
                        f.Revenue = $revenue,
                        f.rating = $rating
                """, id=film_id, title=title, year=year, votes=votes, 
                    revenue=revenue, rating=rating)

                # Nodes Réalisateur
                if "director" in doc and doc["director"]:
                    director = doc["director"]
                    session.run("""
                        MERGE (r:Realisateur {name: $director})
                    """, director=director)

                # Nodes Actors and relation 
                actors = doc.get("actors", [])
                if isinstance(actors, list):
                    for actor in actors:
                        if actor:  
                            session.run("""
                                MERGE (a:Actor {name: $actor})
                                MERGE (f:Film {id: $id})
                                MERGE (a)-[:A_JOUE]->(f)
                            """, actor=actor, id=film_id)
                
                # Add the members of the project as actors to the film "NoSQL"
                project_members = ["Carlota", "Jason", "Julijan"]  
                film_title = "NoSQL"
                for member in project_members:
                    session.run("""
                        MERGE (a:Actor {name: $member})
                        MERGE (f:Film {title: $title})
                        MERGE (a)-[:A_JOUE]->(f)
                    """, member=member, title=film_title)

            except Exception as e:
                print(f"Error processing document {doc}: {e}")
                continue

