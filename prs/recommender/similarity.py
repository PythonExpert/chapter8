import pandas as pd
import numpy as np
from decimal import *

import math
import operator


def pearson(ratings_array, a, b):

    ratings = pd.DataFrame(list(ratings_array.values()))
    ratings['userid'] = ratings['userid'].map(str.strip)
    ratings['movieid'] = ratings['movieid'].map(str.strip)

    a_movies = ratings.loc[ratings["userid"] == a].copy()
    b_movies = ratings.loc[ratings["userid"] == b.strip()].copy()

    #print(len(b_movies), ",", len(a_movies), len(a_movies) | len(b_movies))
    if len(a_movies) == 0 | len(b_movies) == 0:
        return -1

    add_normalized_ratings(a_movies, a)
    add_normalized_ratings(b_movies, b)
    user_a_b = pd.merge(a_movies, b_movies, on="movieid")

    user_a_b["rating_product"] = user_a_b.loc[:, "normalized_rating_x"] * \
                                 user_a_b.loc[:, "normalized_rating_y"]

    user_a_b["square_x"] = user_a_b.loc[:, "normalized_rating_x"] * \
                           user_a_b.loc[:, "normalized_rating_x"]
    user_a_b["square_y"] = user_a_b.loc[:, "normalized_rating_y"] * \
                           user_a_b.loc[:, "normalized_rating_y"]

    sum_square_x = user_a_b["square_x"].sum()
    sum_square_y = user_a_b["square_y"].sum()
    sum_rating_product = Decimal(user_a_b["rating_product"].sum())

    sim = sum_rating_product/Decimal((math.sqrt(sum_square_x)*math.sqrt(sum_square_y)))
    #print("sim(", a, ", ", b, ") = ", sim)

    return sim


def add_normalized_ratings(ratings, userid): #A

    ra = ratings["rating"]
    average_rating = np.array(ra).mean() #E

    ratings["normalized_rating"] = ratings["rating"]/average_rating

    return ratings


def cosine(ratings_array, a,b):
    ratings = pd.DataFrame(list(ratings_array))

    print(ratings)
    movie_a_b = pd.merge(ratings[ratings["movieid"] == a], \
                     ratings[ratings["movieid"] == b], on="userid")

    movie_a_b["rating_product"] = movie_a_b.loc[:, "normalized_rating_x"] \
                                * movie_a_b.loc[:, "normalized_rating_y"]

    movie_a_b["square_x"] = movie_a_b.loc[:, "normalized_rating_x"] *\
                            movie_a_b.loc[:, "normalized_rating_x"]
    movie_a_b["square_y"] = movie_a_b.loc[:, "normalized_rating_y"] *\
                            movie_a_b.loc[:, "normalized_rating_y"]

    sum_square_x = movie_a_b["square_x"].sum()
    sum_square_y = movie_a_b["square_y"].sum()

    sum_rating_product = movie_a_b["rating_product"].sum()
    return sum_rating_product/((math.sqrt(sum_square_x)*math.sqrt(sum_square_y)))


def find_similar_users(ratings, a):
    users = set(ratings["userid"])

    similarity = dict()
    for user in users:
        similarity[user] = pearson(ratings, a, user)

    sorted_similarity = sorted(similarity.items(), key=operator.itemgetter(1), reverse=True)

    return sorted_similarity

