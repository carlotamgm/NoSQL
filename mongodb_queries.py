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
    "films_per_year": {
    "description": "Films per year",
    "type": "aggregate",
    "query": [
        {
            "$group": {
                "_id": "$year",
                "titles": { "$push": "$title" }  
            }
        },
        { "$sort": { "_id": 1 } }
        ]
    },
    "available_genres": {
        "description": "Available genres",
        "type": "aggregate",
        "query": [
            # if there is more than 1 genre, split them into separate elements
            { "$project": 
                { "genre": {
                    "$split": ["$genre", ","]
                    } 
                } 
            },  
            # divides info into subsets based on the genre
            { "$unwind": "$genre"},
            {
                "$group": {
                    "_id": "$genre"
                }
            },
            # return genres in alphabetical order
            { "$sort": { "_id": 1 } }
        ]
    },
    "highest_revenue_film": {
        "description": "Film with highest revenue",
        "type": "aggregate",
        "query": [
            # Check that the revenue field exists and is not None
            {"$match": {"Revenue (Millions)": {"$exists": True, "$ne": None, "$type": "double"}}},
            # Order by revenue in descending order, from highest to lowest
            {"$sort": {"Revenue (Millions)": -1}},
            # Take the first film
            {"$limit": 1}
        ]
    },
    "directors_with_multiple_films": {
        "description": "Directors who have taken part in more than 5 films",
        "type": "aggregate",
        "query": [
            {"$group": {"_id": "$Director", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 5}}},
            # Sort by the number of films in descending order, from highest to lowest
            {"$sort": {"count": -1}},
        ]
    },
    "genre_with_highest_revenue": {
        "description": "Genre with highest revenue",
        "type": "aggregate",
        "query": [
            # Calculate the revenue of each genre
            { "$project": 
                { "genre": {
                    "$split": ["$genre", ","]
                    } ,
                    "revenue": "$Revenue (Millions)"
                } 
            },  
            # divides info into subsets based on the genre
            { "$unwind": "$genre"},
            # Check that the revenue field exists and is not None
            {"$match": {"revenue": {"$exists": True, "$ne": None, "$type": "double"}}},
            # Group by genre and sum the revenue for each genre
            {
                "$group": {
                    "_id": "$genre",
                    # Sum the revenue for each genre
                    "totalRevenue": {"$sum": "$revenue"}
                }
            },
            # Sort by total revenue in descending order, from highest to lowest
            {"$sort": {"totalRevenue": -1}},
            # Limit to the top genre
            {"$limit": 1}
        ]
    },
    "top_rated_by_decade": {
        "description": "Top 3 highest rated films by decade",
        "type": "aggregate",
        "query": [
            {
                "$match": {
                    "rating": {"$exists": True, "$ne": None, "$ne": "unrated"},
                    "year": {"$exists": True, "$ne": None, "$type": "int"}
                }
            },
            {
                "$addFields": {
                    "decade": {
                        "$subtract": ["$year", {"$mod": ["$year", 10]}]
                    }
                }
            },
            {
                "$sort": {"decade": 1, "rating": -1}
            },
            {
                "$group": {
                    "_id": "$decade",
                    "top_films": {
                        "$push": {
                            "title": "$title",
                        }
                    }
                }
            },
            {
                "$project": {
                    "decade": "$_id",
                    "top_3_films": {"$slice": ["$top_films", 3]},
                    "_id": 0
                }
            },
            {
                "$sort": {"decade": 1}
            }
        ]
    },
    "longest_film_by_genre": {
        "description": "Longest film by genre",
        "type": "aggregate",
        "query": [
            {
                "$match": {
                    "Runtime (Minutes)": {"$exists": True, "$ne": None, "$type": "int"}
                }
            },
            { "$project":
                { 
                    "genre": {
                        "$split": ["$genre", ","]
                    },
                    "Runtime (Minutes)": 1,
                    "title": 1
                } 
            },
            { "$unwind": "$genre"},
       # Group by genre and find the longest film in each genre
            {
                "$group": {
                    "_id": "$genre",
                    "longest_film": {
                        "$first": {
                            "Title": "$title",
                            "Duration (Minutes)": "$Runtime (Minutes)"
                        }
                    }
                }
            }
        ]
    },
    "high_rating_high_revenue": {
        "description": "Create a MongoDB view that displays only the films with a score greater than 80 (Metascore)",
        "type": "aggregate",
        "query": [
            {
                "$match": {
                    "Metascore": {"$gt": 80},
                    "Revenue (Millions)": {"$gt": 50}
                }
            }
        ]
    },
    "runtime_revenue_correlation_data": {
        "description": "Calculate the correlation between film runtime and revenue",
        "type": "find",
        "query": {
            "Runtime (Minutes)": {"$ne": None},
            "Revenue (Millions)": {"$ne": None}
        },
        "projection": {
            "_id": 0,
            "Runtime (Minutes)": 1,
            "Revenue (Millions)": 1
        }
    },
    "average_runtime_by_decade": {
        "description": "Check if average runtime of films changed by decade",
        "type": "aggregate",
        "query": [
            {
                "$match": {
                    "year": {"$ne": None},
                    "Runtime (Minutes)": {"$ne": None}
                }
            },
            {
                "$project": {
                    "decade": {
                        "$multiply": [
                            { "$floor": { "$divide": ["$year", 10] } },
                            10
                        ]
                    },
                    "Runtime (Minutes)": 1
                }
            },
            {
                "$group": {
                    "_id": "$decade",
                    "average_runtime": { "$avg": "$Runtime (Minutes)" },
                    "count": { "$sum": 1 }
                }
            },
            {
                "$sort": { "_id": 1 }
            }
        ]
    }
}