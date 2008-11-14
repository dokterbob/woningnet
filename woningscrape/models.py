from django.db import models

class Gemeente(models.Model):
    naam = models.CharField(max_length=50, db_index=True)
    
    def __unicode__(self):
        return self.naam

ENERGIE_LABELS = (
    ('A' , 'A'),
    ('B' , 'B'),
    ('C' , 'C'),
    ('D' , 'D'),
    ('E' , 'E'),
    ('F' , 'F'),
    ('G' , 'G')
)

class Woning(models.Model):
    class Meta:
        verbose_name_plural = 'woningen'
        ordering = ['-reacties',]
        
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
    leeftijd = models.CharField(blank=True, max_length=25)
    
    kamers = models.PositiveSmallIntegerField(blank=True, null=True)
    oppervlakte = models.FloatField(blank=True, null=True)
    energielabel = models.CharField(blank=True, max_length=1, choices=ENERGIE_LABELS)
    woningtype = models.CharField(blank=True, max_length=100)
    
    extra = models.TextField(default='')
    
    def __unicode__(self):
        return '%s, %s' % (self.adres, self.gemeente)
    