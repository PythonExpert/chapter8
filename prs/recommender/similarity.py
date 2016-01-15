# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

ratings = np.array( \
        [[ 1, 2, 3 ],\
         [1, 3, 4 ],]\
         )
         
p_ratings = pd.DataFrame(ratings)
print (p_ratings)