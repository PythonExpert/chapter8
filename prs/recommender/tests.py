from django.test import SimpleTestCase

import pandas as pd
import numpy as np

from recommender.builder import Builder


class BuilderTests(SimpleTestCase):
    def get_ratings(self):
        data = np.array( \
            ([[0, 0, 5.0], [0, 1, 5.0], [0, 3, 2.0], [0, 4, 2], [0, 5, 2], \
              [1, 0, 4], [1, 1, 5], [1, 2, 4], [1, 4, 3], [1, 5, 3], \
              [2, 0, 5], [2, 1, 3], [2, 2, 5], [2, 3, 2], [2, 4, 1], [2, 5, 1], \
              [3, 0, 3], [3, 2, 3], [3, 3, 5], [3, 4, 1], [3, 5, 1], \
              [4, 0, 3], [4, 1, 3], [4, 2, 3], [4, 3, 2], [4, 4, 4], [4, 5, 5], \
              [5, 0, 2], [5, 1, 3], [5, 2, 2], [5, 3, 3], [5, 4, 5], [5, 5, 5], ]))  # B

        return pd.DataFrame(data, columns=["userid", "movieid", "rating"])

    def test_build_similarity_model(self):
        """Checks that the similarity model is calculated correct."""
        ratings = self.get_ratings()

        model = Builder.build_similarity_model(ratings)
        self.assertIsNotNone(model)
        self.assertEqual(len(model), 15)

        # item 0 and 2 has identical ratings. Their similarity should therefore be 1.0
        self.assertAlmostEqual(model[frozenset({0, 2})], 1.0)

    def test_add_normalized_rating(self):
        """Checks that the user average is substracted from all the ratings."""
        ratings = self.get_ratings()

        Builder.add_normalized_rating(ratings)

        norm_ratings = ratings[ratings['userid'] == 3]
        self.assertAlmostEqual(norm_ratings.iloc[0]['movieid'], 0)
        self.assertAlmostEqual(norm_ratings.iloc[0]['normalized_rating'], 0.4)
        self.assertAlmostEqual(norm_ratings.iloc[1]['movieid'], 2)
        self.assertAlmostEqual(norm_ratings.iloc[1]['normalized_rating'], 0.4)
        self.assertAlmostEqual(norm_ratings.iloc[2]['movieid'], 3)
        self.assertAlmostEqual(norm_ratings.iloc[2]['normalized_rating'], 2.4)
        self.assertAlmostEqual(norm_ratings.iloc[3]['movieid'], 4)
        self.assertAlmostEqual(norm_ratings.iloc[3]['normalized_rating'], -1.6)
        self.assertAlmostEqual(norm_ratings.iloc[4]['movieid'], 5)
        self.assertAlmostEqual(norm_ratings.iloc[4]['normalized_rating'], -1.6)
