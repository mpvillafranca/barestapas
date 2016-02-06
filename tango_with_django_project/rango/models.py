from django.db import models
from django.template.defaultfilters import slugify

# Create your models here.
class Bar(models.Model):
    nombre = models.CharField(max_length=128, unique=True)
    direccion = models.CharField(max_length=128)
    n_visitas = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        super(Bar, self).save(*args, **kwargs)

    def __unicode__(self):  #For Python 2, use __str__ on Python 3
        return self.nombre

class Tapa(models.Model):
    bar = models.ForeignKey(Bar)
    nombre = models.CharField(max_length=128)
    votos = models.IntegerField(default=0)

    def __unicode__(self):      #For Python 2, use __str__ on Python 3
        return self.nombre
