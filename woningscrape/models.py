from django.db import models

class Gemeente(models.Model):
    naam = models.CharField(max_length=50, db_index=True)
    
    def __unicode__(self):
        return self.naam

class Woning(models.Model):
    woningnet_id = models.CharField(max_length=50, db_index=True, unique=True)
    woningnummer = models.CharField(max_length=10)
    reacties = models.PositiveSmallIntegerField(default=0)
    
    adres = models.CharField(max_length=100)
    postcode = models.CharField(blank=True, max_length=100)
    gemeente = models.ForeignKey(Gemeente)
    
    rekenhuur = models.FloatField()
    brutohuur = models.FloatField()
    
    # Extra info
    leegper = models.DateField(blank=True, null=True)
    leeftijd = models.PositiveSmallIntegerField(blank=True, null=True)
    
    woningtype = models.CharField(blank=True, max_length=100)
    
    extra = models.TextField(default='')
    
    def __unicode__(self):
        return '%s, %s' % (self.adres, self.gemeente)
    