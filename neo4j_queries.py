""""
20. Quel r´ealisateur Director a travaill´e avec le plus grand nombre d’acteurs distincts ?
21. Quels sont les films les plus ”connect´es”, c’est-`a-dire ceux qui ont le plus d’acteurs en commun
avec d’autres films ?
22. Trouver les 5 acteurs ayant jou´e avec le plus de r´ealisateurs diff´erents.
23. Recommander un film `a un acteur en fonction des genres des films o`u il a d´ej`a jou´e.
24. Cr´eer une relation INFLUENCE PAR entre les r´ealisateurs en se basant sur des similarit´es dans
les genres de films qu’ils ont r´ealis´es.
25. Quel est le ”chemin” le plus court entre deux acteurs donn´es (ex : Tom Hanks et Scarlett
Johansson) ?
26. Analyser les communaut´es d’acteurs : Quels sont les groupes d’acteurs qui ont tendance `a
travailler ensemble ? (Utilisation d’algorithmes de d´etection de communaut´e comme Louvain.)
"""

QUERIES = {
    "actor_most_films": {
        "description": "Actor with most films",
        "type": "aggregate",
        "query": 
            """
            MATCH (a:Actor)-[:A_JOUE]->(f:Film)
            RETURN a.name AS actor, COUNT(f) AS film_count
            ORDER BY film_count DESC
            LIMIT 1
            """
    },
    "actors_starring_with_Anne_Hathaway": {
        "description": "Actors starring with Anne Hathaway",
        "type": "aggregate",
        "query": 
            """
            MATCH (a:Actor)-[:A_JOUE]->(f:Film)<-[:A_JOUE]-(Anne_Hathaway:Actor {name: 'Anne Hathaway'})
            RETURN a.name AS actor
            """
    },
    "actor_with_most_revenue": {
        "description": "Actor with most revenue",
        "type": "aggregate",
        "query": 
            """
            MATCH (a:Actor)-[:A_JOUE]->(f:Film)
            RETURN a.name AS actor, SUM(f.Revenue) AS total_revenue
            ORDER BY total_revenue DESC
            LIMIT 1
            """
    },
    "average_of_votes": {
        "description": "Average votes",
        "type": "aggregate",
        "query": 
            """
            MATCH (f:Film)
            RETURN AVG(f.Votes) AS average_votes
            """
    },
    "most_common_genre": {
        "description": "Most common genre",
        "type": "aggregate",
        "query": 
            """
            MATCH (f:Film)
            UNWIND f.genre AS genre
            WITH genre, COUNT(*) AS genre_count
            RETURN f.genre AS genre
            ORDER BY genre DESC
            LIMIT 1
            """
    },
    "films_with_project_members":  {
        "description": "Films where project members participate",
        "type": "aggregate",
        "query":
            """
            MATCH (a:Actor)-[:A_JOUE]->(f:Film)
            WHERE a.name IN ['Carlota','Jason','Julijan']
            RETURN f.title AS film, f.year AS year, f.Votes AS votes, f.Revenue AS revenue, f.rating AS rating
            ORDER BY f.year DESC
            """
    },
    "director_worked_with_plus_actors": {
        "description": "Director who has worked with the highest number of actors",
        "type": "aggregate",
        "query":
            """
            MATCH (r: Realisteur)
            MATCH (a:Actor)-[:A_JOUE]->(f:Film)
            WHERE r.name IN f.director
            RETURN r.name AS director, COUNT(DISTINCT a) AS actor_count
            ORDER BY actor_count DESC
            LIMIT 1
            """
    },
    

}