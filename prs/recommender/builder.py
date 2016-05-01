import pandas as pd
from decimal import *

from recommender.models import Ratings, CF_Similarity
from django.db import connection
import django.utils.text
import datetime
import time


class Builder:

    @staticmethod
    def generate_implicit_ratings(userdata):

        w_buys = 10
        w_moredetails = 2
        w_details = 10
        w_0 = 1

        movie_ratings = []
        maxrating = 0
        for movie in userdata:
            rating = w_buys * movie["buys"] + w_moredetails * movie["moredetails"] + w_details * movie["details"] + w_0
            if rating > maxrating:
                maxrating = rating
            movie_ratings.append({"id": movie["content_id"], "title": movie["title"], "rating": rating})

        for movie_rating in movie_ratings:
            movie_rating["rating"] /= maxrating
            movie_rating["rating"] *= 5

        return movie_ratings

    @staticmethod
    def save_ratings(userid, movie_ratings):

        print("saving %s ratings" % len(movie_ratings))

        db_rating_objs = []
        for rating in movie_ratings:
            today = datetime.datetime.now()

            r = Ratings( \
                userid=userid, \
                movieid=rating["id"], \
                rating=rating["rating"], \
                date_day=today.day, \
                date_month=today.month, \
                date_year=today.year, \
                date_hour=today.hour, \
                date_minute=today.minute, \
                date_second=today.second, \
                type='implicit')

            db_rating_objs.append(r)

        Ratings.objects.bulk_create(db_rating_objs)

    @staticmethod
    def build_item_collaborative_model():
        print("building item-item similarity matrix")
        all_ratings = Ratings.objects.all()
        ratings = pd.DataFrame(list(all_ratings.values()))
        model = Builder.build_similarity_model(ratings)
        Builder.save_similarity_model(model)


    @staticmethod
    def add_normalized_rating(ratings):
        print("normalizing ratings")
        ratings['normalized_rating'] = 0.0
        ratings['normalized_rating'] = ratings.groupby('userid')['rating'].transform(
            (lambda x: (x.astype(float) - x.mean())))

    @staticmethod
    def save_similarity_model(model, created):
        #add latest to version.

        print("Save item-item model")
        db_sim_objs = []
        for key, value in model.items():
                print ("key: ", key)
                source, target = key
                if source < target:
                    iterm = source
                    source = target
                    target = iterm

                i = CF_Similarity(
                    created = created,
                    source=source,
                    target=target,
                    similarity=value,
                    version=1
                )
                db_sim_objs.append(i)
        CF_Similarity.objects.bulk_create(db_sim_objs)
        print("similarities %s saved" % len(db_sim_objs))