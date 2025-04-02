""""

25. Quel est le ”chemin” le plus court entre deux acteurs donn´es (ex : Tom Hanks et Scarlett
Johansson) ?
26. Analyser les communaut´es d’acteurs : Quels sont les groupes d’acteurs qui ont tendance `a
travailler ensemble ? (Utilisation d’algorithmes de d´etection de communaut´e comme Louvain.)
"""

QUERIES = {
    "actor_most_films": {
        "description": "Actor with most films",

        "query": 
            """
            MATCH (a:Actor)-[:ACTED_IN]->(f:Film)
            RETURN a.name AS actor, COUNT(f) AS film_count
            ORDER BY film_count DESC
            LIMIT 1
            """
    },
    "actors_starring_with_Anne_Hathaway": {
        "description": "Actors starring with Anne Hathaway",

        "query": 
            """
            MATCH (a:Actor)-[:ACTED_IN]->(f:Film)<-[:ACTED_IN]-(Anne_Hathaway:Actor {name: 'Anne Hathaway'})
            RETURN a.name AS actor, f.title AS film
            """
    },
    "actor_with_most_revenue": {
        "description": "Actor with most revenue",

        "query": 
            """
            MATCH (a:Actor)-[:ACTED_IN]->(f:Film)
            WHERE f.revenue IS NOT NULL
            AND f.revenue > 0
            RETURN a.name AS actor, SUM(f.revenue) AS total_revenue 
            ORDER BY total_revenue DESC
            LIMIT 1
            """
    },
    "average_of_votes": {
        "description": "Average votes",

        "query": 
            """
            MATCH (f:Film)
            RETURN ROUND(AVG(f.votes),2) AS average_votes
            """
    },
    "most_common_genre": {
        "description": "Most common genre",

        "query": 
            """
            MATCH (f:Film)-[:HAS_GENRE]->(g:Genre)
            RETURN g.name AS genre, COUNT(g) AS genre_count
            ORDER BY genre_count DESC
            LIMIT 1
            """
    },
    "films_starring_actors_costar_of_members_of_project":  {
        "description": "Films where co-stars play, having they played with project members in other films",

        "query":
            """
            MATCH (a2:Actor)-[:ACTED_IN]->(f:Film)<-[:ACTED_IN]-(a: Actor)
            WHERE a.name = 'Carlota' AND a2.name <> 'Carlota'
            MATCH (a2)-[:ACTED_IN]->(f2:Film)
            WHERE f2.title <> f.title
            RETURN f2.title AS film, a2.name AS actor
            """
    },
    "director_worked_with_plus_actors": {
        "description": "Director who has worked with the highest number of actors",

        "query":
            """
            MATCH (r:Director)-[:DIRECTED]->(f:Film)<-[:ACTED_IN]-(a:Actor)
            RETURN r.name AS director, COUNT(DISTINCT a) AS actor_count
            ORDER BY actor_count DESC
            LIMIT 1
            """
    },
    #CHECK TODO/TOFIX
    "most_connected_films": {
        "description": "Most connected films",

        "query":
            """
            MATCH (a:Actor)-[:ACTED_IN]->(f:Film)<-[:ACTED_IN]-(a2:Actor)
            MATCH (f2:Film)<-[:ACTED_IN]-(a2)
            WHERE f <> f2
            RETURN f.title AS film, COUNT(DISTINCT a2) AS connected_actors
            ORDER BY connected_actors DESC
            LIMIT 1
            """
    },
    "most_prolific_actors": {
        "description": "Actors who have played with the most directors",

        "query":
            """
            MATCH (a:Actor)-[:ACTED_IN]->(f:Film)<-[:DIRECTED]-(r:Director)
            RETURN a.name AS actor, COUNT(DISTINCT r) AS directors_count
            ORDER BY directors_count DESC
            LIMIT 5
            """
    },
    "recommended_film_for_actor": {
        "description": "Recommended film for an actor based on genres",

        "query":
            """
            MATCH (a:Actor)-[:ACTED_IN]->(f:Film)-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(f2:Film)<-[:ACTED_IN]-(a2:Actor)
            WHERE a <> a2
            RETURN DISTINCT f2.title AS recommended_film, a.name AS actor
            ORDER BY f2.title
            LIMIT 1
            """
    },
    "relation_influenced_by": {
        "description": "Influence relation between directors based on genres",

        "query":
            """
            MATCH (r1:Director)-[:DIRECTED]->(f:Film)-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(f2:Film)<-[:DIRECTED]-(r2:Director)
            WHERE r1 <> r2
            RETURN DISTINCT r1.name AS director1, r2.name AS director2, g.name AS genre
            """
    },

    

}