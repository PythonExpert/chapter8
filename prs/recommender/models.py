from django.db import models


class seeded_rec(models.Model):
    version = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=False, primary_key=True)
    source = models.CharField(max_length=200, blank=False, primary_key=True)
    target = models.CharField(max_length=200, blank=False, primary_key=True)
    support = models.FloatField()
    confidence = models.FloatField()

    class Meta:
        managed = False
        db_table = 'seeded_recs'


class Ratings(models.Model):
    userid = models.CharField(max_length=20, blank=False, primary_key=True, db_index=True)
    movieid = models.CharField(max_length=20, blank=False, primary_key=True, db_index=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)
    date_day = models.DecimalField(max_digits=2, decimal_places=0, blank=False, null=False, primary_key=True)
    date_month = models.DecimalField(max_digits=2, decimal_places=0, blank=False, null=False, primary_key=True)
    date_year = models.DecimalField(max_digits=4, decimal_places=0, blank=False, null=False, primary_key=True)
    date_hour = models.DecimalField(max_digits=4, decimal_places=0, blank=False, null=False, primary_key=True)
    date_minute = models.DecimalField(max_digits=4, decimal_places=0, blank=False, null=False, primary_key=True)
    date_second = models.DecimalField(max_digits=4, decimal_places=0, blank=False, null=False, primary_key=True)
    type = models.CharField(max_length=10, blank=False, primary_key=False)

    def __str__(self):
        return '(%s,%s):%s' % (self.userid.strip(), self.movieid.strip(), self.rating)

    class Meta:
        managed = False
        db_table = 'ratings'

class CF_Similarity(models.Model):
    created = models.DateTimeField()
    source = models.CharField(max_length=200, blank=False, primary_key=True)
    target = models.CharField(max_length=200, blank=False, primary_key=True)
    similarity = models.DecimalField(max_digits=2, decimal_places=0, blank=False, null=False)
    version = models.DecimalField(max_digits=2, decimal_places=0, blank=False, primary_key=True, null=False)

    def __str__(self):
        return '(%s,%s):%s' % (self.source.strip(), self.target.strip(), self.similarity)

    class Meta:
        managed = False
        db_table = 'cf_similarity'

