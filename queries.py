
// 1. Afficher l’année o`u le plus grand nombre de films ont été sortis.
[
  {
    $group:
      /**
       * Joins data by the same field
       * _id: The id of the field we want to analyse.
       * count: The number result of "sum". It sums all the movies that went out in that year. 
       */
      {
        _id: "$year",
        count: {
          $sum: 1
        }
      }
  },
  {
    $sort:
      /**
       * Put results in reverse order (-1) so we can see the highest value.
       */
      {
          "count": -1
        }
  },
  /**
  * Restriction to read only the first line of the result.
  */
  {
    $limit: 1
  }
]

// 2. Quel est le nombre de films sortis apr`es l’année 1999.
[{
  /**
  * Filter data by year greater than > 1999
  */
    "$match": { "year": { "$gt": 1999 } }
  },
 /**
  * The result is the number of movies returned.
  */
  {
    "$count": "totalMovies"
  }]

// 3. Quelle est la moyenne des votes des films sortis en 2007.
[ {
  /**
  * Filter data by year 2007
  */
    "$match": { "year": 2007 }
  },
  {
  /**
  * Calculate average of votes
  */
    "$group": {
      "_id": null,
      "avgVotes": { "$avg": "$Votes" }
    }
  },
 /**
 * Remove id from result
 */
  {
    "$project": {
      "_id": 0,
      "avgVotes": 1
    }
  }
]
 
