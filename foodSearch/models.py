from django.db import models
from  django.contrib.auth.models import User


class Product(models.Model):
    reference = models.CharField('Référence', max_length=100, unique=True)
    name = models.CharField('Nom', max_length=200)
    formatted_name = models.CharField('Nom', max_length=200)
    brands = models.CharField('Marque', max_length=200)
    formatted_brands = models.CharField('Marque', max_length=200)
    url = models.URLField()
    image_url = models.URLField()
    image_small_url = models.URLField()
    nutrition_grade_fr = models.CharField(max_length=1)
    saturated_fat_100g = models.FloatField(null=True)
    carbohydrates_100g = models.FloatField(null=True)
    energy_100g = models.FloatField(null=True)
    sugars_100g = models.FloatField(null=True)
    sodium_100g = models.FloatField(null=True)
    salt_100g = models.FloatField(null=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    reference = models.CharField('Référence', max_length=100, unique=True)
    products = models.ManyToManyField(Product, related_name='categories', blank=True)

    def __str__(self):
        return self.reference


class Favorite(models.Model):
    created_at = models.DateTimeField("date d'envoi", auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    substitute = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='substitute')
    initial_search_product = models.ForeignKey(Product,
                                               on_delete=models.CASCADE,
                                               related_name='initial_search_product')

    class Meta:
        unique_together = ('user', 'substitute',)

    def __str__(self):
        return "{} {} {}".format(self.user, self.substitute, self.initial_search_product)
