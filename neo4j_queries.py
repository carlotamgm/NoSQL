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
            WHERE r1 <> r2 AND f <> f2
            MERGE (r1)-[:INFLUENCED_BY {genre: g.name}]->(r2)
            RETURN DISTINCT r1.name AS director1, r2.name AS director2, g.name AS genre
            """
    },
    #TODO/TOFIX mini error after
    "shortest_path_between_actors": {
        "description": "Shortest path between two actors",
        "query":
            """
            MATCH p = shortestPath(
            (a1:Actor {name: $actorName1})-[:ACTED_IN*]-(a2:Actor {name: $actorName2}))
            RETURN p
            """
    },
    "analyse_actors_communities": {
        "description": "Analyse actors communities",
        "query1":
            """
            CALL gds.graph.project(
            'actors_graph',
            ['Actor', 'Film'],
            {
                ACTED_IN: {
                orientation: 'UNDIRECTED'
                }
            });
            """,
        "query2":
            """
            CALL gds.louvain.write('actors_graph', { writeProperty: 'community' });
            """,
        "query3":
            """
            MATCH (a:Actor)
            RETURN a.name AS actor, a.community AS community
            ORDER BY a.community;
            """
    },

    "films_same_genre_different_director": {
        "description": "Films with the same genre but different directors",

        "query":
            """
            MATCH (f1:Film)-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(f2:Film)
            MATCH (f1:Film)<-[:DIRECTED]-(d1:Director), (f2:Film)<-[:DIRECTED]-(d2:Director)
            WHERE d1 <> d2 AND f1 <> f2
            RETURN DISTINCT f1.title AS film1, f2.title AS film2, g.name AS genre, d1.name AS director1, d2.name AS director2
            """
    },
    "recommended_films_based_on_actor": {
        "description": "Recommended films based on actor",

        "query":
            """
            MATCH (a:Actor {name: $actorName})-[:ACTED_IN]->(f:Film)
            RETURN DISTINCT f.title 
            ORDER BY f.title
            """
    },
    "directors_similar_films_per_year": {
        "description": "Directors who produced similar films per year",

        "query":
            """
            MATCH (d:Director)-[:DIRECTED]->(f:Film)-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(f2:Film)<-[:DIRECTED]-(d2:Director)
            WHERE d <> d2 AND f.year = f2.year
            MERGE (d)-[:COMPETES_WITH {year: f.year, genre: g.name}]->(d2)
            RETURN d.name AS director1, d2.name AS director2, f.year AS year, g.name AS genre
            ORDER BY year DESC;
            """
    },
    "collaborations_for_votes_or_revenue": {
        "description": "Collaborations between actors and directors based on revenue or votes",

        "query":
            """
            MATCH (d:Director)-[:DIRECTED]->(f:Film)<-[:ACTED_IN]-(a:Actor)
            WITH d, a, f,
            AVG(f.revenue) AS avg_revenue, 
            AVG(f.votes) AS avg_votes,
            CASE 
                WHEN AVG(f.revenue) > AVG(f.votes) THEN AVG(f.revenue)
                ELSE AVG(f.votes)
            END AS max_metric
            ORDER BY max_metric DESC
            RETURN d.name AS director, a.name AS actor, f.title, avg_revenue, avg_votes, max_metric
            LIMIT 10
            """
    },

}