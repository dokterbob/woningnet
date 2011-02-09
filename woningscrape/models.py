from django.db import models

class Gemeente(models.Model):
    class Meta:
        verbose_name_plural = 'gemeentes'
        ordering = ['naam',]
        
    naam = models.CharField(max_length=50, db_index=True)
    
    def __unicode__(self):
        return self.naam

class Wijk(models.Model):
    class Meta:
        verbose_name_plural = 'wijken'
        ordering = ['gemeente', 'naam',]
        
    naam = models.CharField(max_length=50, db_index=True)
    gemeente = models.ForeignKey(Gemeente)
    
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
        ordering = ['reacties',]
        
    woningnet_id = models.CharField(max_length=50, db_index=True, unique=True)
    woningnummer = models.CharField(max_length=10)
    woonversnelling = models.BooleanField(default=False)
    reacties = models.PositiveSmallIntegerField(default=0)
    
    adres = models.CharField(max_length=100)
    postcode = models.CharField(blank=True, max_length=100)
    wijk = models.ForeignKey(Wijk)
    gemeente = models.ForeignKey(Gemeente)
    
    rekenhuur = models.FloatField(default=0.0)
    brutohuur = models.FloatField(default=0.0)
    
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
    
    def get_absolute_url(self):
        return 'http://www.woningnet.nl/woningdetails.asp?IID=5&id=%s' % self.woningnet_id
    