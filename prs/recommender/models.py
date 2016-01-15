from django.db import models


# Create your models here.
class seeded_rec(models.Model):
    version = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=False, primary_key=True)    
    source = models.CharField(max_length=200, blank=False, primary_key=True)
    target = models.CharField(max_length=200, blank=False, primary_key=True)
    #target = models.ForeignKey('movie.Movies', 'id', db_column='target')
    support = models.FloatField()
    confidence = models.FloatField()

    class Meta:
        managed = False
        db_table = 'seeded_recs'