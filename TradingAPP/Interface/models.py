from django.db import models


# Create your models here.

class Sesion(models.Model):
    algoritmo_elegido = models.CharField(max_length=200)

    @classmethod
    def create(cls, algoritmo_elegido):
        sesion = cls(algoritmo_elegido=algoritmo_elegido)
        return sesion
