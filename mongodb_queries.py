# mongodb_queries.py
from typing import Union, Dict, List

# Definición de tipos para mayor claridad
MongoQuery = Union[Dict, List[Dict]]

QUERIES = {
    "year_with_most_films": {
        "description": "Year with most film releases",
        "type": "aggregate",
        "query": [
            {"$group": {"_id": "$year", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]
    },
    "films_after_1999": {
        "description": "Count films released after 1999",
        "type": "count",
        "query": {"year": {"$gt": 1999}}
    },
    "avg_votes_2007": {
        "description": "Average votes for 2007 films",
        "type": "aggregate",
        "query": [
            {"$match": {"year": 2007}},
            {"$group": {"_id": None, "averageVotes": {"$avg": "$Votes"}}}
        ]
    },
    "high_rated_films": {
        "description": "Find films with rating > 8",
        "type": "find",
        "query": {"rating": {"$gt": 8}},
        "projection": {"_id": 0, "title": 1, "year": 1, "rating": 1}
    }
}