from django.db import models


# Create your models here.

class Sesion(models.Model):
    algoritmo_elegido = models.ForeignKey('AlgoritmoTrading', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.algoritmo_elegido.__str__()


class AlgoritmoTrading(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=10000)
    autor = models.CharField(max_length=200)
    imagen = models.ImageField()

    def __str__(self):
        return self.nombre
