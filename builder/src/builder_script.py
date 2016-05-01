import database
import item_cf_builder

ratings = database.get_ratings()

item_cf_builder.build(ratings)
