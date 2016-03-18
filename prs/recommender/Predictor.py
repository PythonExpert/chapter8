import math
import numpy as np
import pandas as pd

import operator
from decimal import *
import timeit
from django.db import connection
from recommender.models import CF_Similarity
from recommender.models import Ratings
from recommender import similarity

from django.db.models import Q
from django.db.models import Count
from django.db.models import Avg

from utils import OrmHelper


class Predictor:

    def __init__(self, userid):
        print("starting prediction.")
        self.userid = userid
        self.ratings = dict()
        self.avg_ratings = dict()
        self.ratings = dict()
        self.predicted_items = dict()

        #self.avg_ratings = self.average_ratings()
        #self.normalize_ratings()

    def get_ratings(self, user):
        if user in self.ratings:
            return self.ratings[user]
        else:
            self.ratings[user] = Ratings.objects.filter(userid=user)
        return self.ratings[user]

    def get_avg_rating(self, user):
        ratings = self.get_ratings(user)

        if user in self.avg_ratings:
            return self.avg_ratings[user]
        else:
            self.avg_ratings[user] = ratings.aggregate(avg=Avg('rating'))['avg']

        print (self.avg_ratings[user])
        return Decimal(self.avg_ratings[user])

    def user_collaborative_filtering(self, number, k=2):

        active_user_ratings = self.get_ratings(self.userid)

        items = set(rating.movieid for rating in active_user_ratings)
        candidate_users = self.find_candidate_users(items, k)
        usable_ratings = self.find_usable_ratings(candidate_users)

        similarities = dict()

        for user in candidate_users:
            userid = user['userid'].strip()

            if self.userid != userid:
                print("users userid ",userid, ".")
                similarities[userid] = similarity.pearson(usable_ratings, self.userid, userid)

        predictedratings=dict()
        num_predicitons = 0

        print(len(usable_ratings))

        for item in usable_ratings.values("movieid").distinct():
            if not (item['movieid'] in items):

                movieid = item['movieid'].strip()
                pred = self.user_cf_prediction(usable_ratings, movieid, similarities)
                predictedratings[movieid] = pred
                num_predicitons += 1

        sorted_predictions = sorted(predictedratings.items(), key=operator.itemgetter(1), reverse=True)

        return sorted_predictions[:number]

    def find_candidate_users(self, items, k=2):
        # Find users that that share at least on rated item
        candidate_users = Ratings.objects.filter(Q(movieid__in=items)) \
                              .values('userid') \
                              .annotate(overlapping=Count('movieid')) \
                              .order_by('-overlapping')[:k]
        return candidate_users

    def find_usable_ratings(self, candidate_users):

        usable_ratings = Ratings.objects.filter(Q(userid__in=candidate_users.values('userid')))
        return usable_ratings

    def item_collaborative_filtering(self, number):

        users_items = self.get_ratings(self.userid).values('movieid').distinct()
        item_ids = list(str(item['movieid'].strip()) for item in users_items)
        print("users_items ", item_ids)

        candidate_items = CF_Similarity.objects.filter(Q(source__in=users_items))
        print("candidate_items ", candidate_items.values('target').distinct())

        predictedratings = dict()

        num_predicitons = 0
        for item in candidate_items.values('target').distinct():
            if item not in users_items:
                predictedratings[item] = self.item_cf_prediction(userid, item)
                num_predicitons += 1

        print("predicted ", num_predicitons, " items")
        sorted_predictions = sorted(predictedratings.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_predictions[:number]


    def user_cf_prediction(self, usable_ratings, movieid, similarities):

        #print("user collaborative filtering prediction user ", self.userid, " and ", movieid, ".")

        active_user_avg_ratings = Decimal(self.get_avg_rating(self.userid))

        dividend = Decimal(0) #C
        divisor = Decimal(0) #C

        for n in set(x['userid'].strip() for x in usable_ratings.filter(movieid=movieid).values('userid')):   #D

            userid = n
            sim = Decimal(similarities[userid])    #E
            rn_avg = self.get_avg_rating(userid)      #F
            r_ratings = self.get_ratings(userid)
            rn_item = Decimal(r_ratings.filter(movieid = movieid).values('rating')[0]['rating'])

            dividend += Decimal(sim*(rn_item - Decimal(rn_avg))) #H
            divisor += Decimal(math.fabs(sim)) #I

        self.predicted_items[movieid] = (active_user_avg_ratings + dividend/divisor)
        return active_user_avg_ratings + dividend/divisor #J

    def item_cf_prediction(self, user, item):

        similary_items = self.get_similarity_dict(item) #A
        weightedsum = 0 #B
        similarity_sum = 0 #C
        for similary_item in similary_items():    #C
            user_item_row = (self.ratings[(self.ratings.userId == user) &
                                          (self.ratings.movieId == similary_item.target)])
            if (len(user_item_row) == 1): #D
                weightedsum += similary_item.similarity \
                               *user_item_row.iloc[0]["nrating"] #E
                similarity_sum += math.fabs(similary_item.similarity)

        return self.get_avg_rating(user) + weightedsum / similarity_sum

    def get_similarity_dict(self, item):
        similar_items = CF_Similarity.objects.get(source=item)
        return similar_items


    def average_ratings(self): #A
        users = set(self.ratings["userid"]) #B
        average_ratings = dict() #C

        for user in users:
            user_ratings = self.ratings[self.ratings["userid"] == user] #D
            ra = user_ratings["rating"]
            average_ratings[user] = np.array(ra).mean() #E

        return average_ratings

    def normalize_ratings(self):
        user_average = self.avg_ratings
        for user in user_average.keys():
            self.ratings.loc[:, 'normalized_rating'] = self.ratings.loc[:,'rating'] \
                                        - self.avg_ratings[user]