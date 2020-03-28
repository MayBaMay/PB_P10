#! /usr/bin/env python3
# coding: utf-8

"""
This module create a command allowing user to reset or fill database
with datas from openfactfood api in order to use them in the appliaction foodSearch
"""

import time
import datetime
from statistics import mean
import unicodedata

from django.core.management.base import BaseCommand
from django.db import transaction

import openfoodfacts

from foodSearch.models import Category, Product, Favorite
from .settings import FIRST_PAGE, LAST_PAGE, DB_REPORTS_FILE


class InitDB:
    """
    This class defines code relative to reset or fill database
    """

    def __init__(self):
        self.tps = []
        self.initial_page = 0
        self.page = 0 # page counter
        self.last_page = 0 # number of page wanted from the api

    @staticmethod
    def reset_db():
        """Method clearing database"""
        Category.objects.all().delete()
        Favorite.objects.all().delete()
        Product.objects.all().delete()

    @staticmethod
    def upper_unaccent(sentence):
        """"return a string in upper case and without any accent"""
        try:
            sentence_unaccent = ''.join(
                (c for c in unicodedata.normalize('NFD', sentence)
                 if unicodedata.category(c) != 'Mn'))
            return sentence_unaccent.upper()
        except:
            print('upper_unaccent error')
            return sentence

    def load_datas(self, page, last_page):
        """method loading datas from api in the database"""

        self.initial_page = page
        self.page = page # page counter
        self.last_page = last_page # number of page wanted from the api

        while self.page <= self.last_page:
            print("\n")
            print("loading page "+ str(self.page))
            start_time = time.time()
            # use openfactfood api to load pages
            page_prods = openfoodfacts.products.get_by_facets(
                {'country': 'france'}, page=self.page, locale="fr"
            )

            for product in page_prods:

                try:
                    saturated_fat_100g = product['nutriments']['saturated-fat_100g']
                except KeyError:
                    saturated_fat_100g = ""
                try:
                    carbohydrates_100g = product['nutriments']['carbohydrates_100g']
                except KeyError:
                    carbohydrates_100g = ""
                try:
                    energy_100g = product['nutriments']['energy_100g']
                except KeyError:
                    energy_100g = ""
                try:
                    sugars_100g = product['nutriments']['sugars_100g']
                except KeyError:
                    sugars_100g = ""
                try:
                    sodium_100g = product['nutriments']['sodium_100g']
                except KeyError:
                    sodium_100g = ""
                try:
                    salt_100g = product['nutriments']['salt_100g']
                except KeyError:
                    salt_100g = ""

                try:
                    name = product["product_name"]
                    formatted_name = self.upper_unaccent(name)
                    brands = product["brands"]
                    formatted_brands = self.upper_unaccent(brands)

                    with transaction.atomic():
                        # insert each product in database

                        new_product = Product.objects.create(
                            reference=product["id"],
                            name=name,
                            formatted_name=formatted_name,
                            brands=brands,
                            formatted_brands=formatted_brands,
                            nutrition_grade_fr=product["nutrition_grades"],
                            url=product["url"],
                            image_url=product["image_url"],
                            image_small_url=product["image_small_url"],
                            saturated_fat_100g=saturated_fat_100g,
                            carbohydrates_100g=carbohydrates_100g,
                            energy_100g=energy_100g,
                            sugars_100g=sugars_100g,
                            sodium_100g=sodium_100g,
                            salt_100g=salt_100g,
                        )
                        # insert each category in database only if products
                        # has categories infos(no keyerror in product['categories_hierarchy'])
                        try:
                            with transaction.atomic():
                                for category in product['categories_hierarchy']:
                                    if category[0:3] == 'en:':
                                        try:
                                            # try to get the category in database
                                            cat = Category.objects.get(reference=category)
                                        except Category.DoesNotExist:
                                            # if category doesn't exist yet, create one
                                            cat = Category.objects.create(reference=category)
                                            # categ = Category.objects.get(reference=category)
                                        # in any case, add a relation between Category and Product
                                        cat.products.add(new_product)
                        ###### only keep cleaned datas #######
                        except:
                            pass
                except:
                    pass

            print("{} products in database".format(Product.objects.count()))
            print("{} categories in database".format(Category.objects.count()))
            tps_page = round((time.time() - start_time), 1)
            print("Temps d'execution page: {} secondes ---".format(tps_page))
            self.tps.append(tps_page)
            self.page += 1


class Command(BaseCommand):
    """Update datas in database - options: reset or fill"""

    def add_arguments(self, parser):
        """Class arguments : reset or fill"""
        parser.add_argument('-r',
                            '--reset',
                            action='store_true',
                            dest='reset',
                            help='Reset database')
        parser.add_argument('-f',
                            '--fill',
                            action='store_true',
                            dest='fill',
                            help='Fill database')

    def handle(self, **options):
        """Class handler, launch reset or fill depending on option choice"""

        if options['reset']:
            database = InitDB()
            database.reset_db()

            file = open(DB_REPORTS_FILE, "a")
            file.write("\nRESET Database the {}:--DATABASE EMPTY\n".format(datetime.datetime.now()))
            file.close()

            self.stdout.write(self.style.SUCCESS("Reset base de données effectué"))

        if options['fill']:
            products = Product.objects.count()
            categories = Category.objects.count()

            database = InitDB()
            database.load_datas(FIRST_PAGE, LAST_PAGE)

            file = open(DB_REPORTS_FILE, "a")
            file.write("""
            Database updated the {}:
            --- Database FILLED from page {} to {}
            --- {} products in database ({} added)
            --- {} categories in database ({} added)
            --- Temps moyen d'execution : {} secondes par page ---\n"""
                       .format(datetime.datetime.now(),
                               database.initial_page,
                               database.last_page,
                               Product.objects.count(),
                               Product.objects.count()-products,
                               Category.objects.count(),
                               Category.objects.count()-categories,
                               round(mean(database.tps), 1)))
            file.close()

            self.stdout.write(self.style.SUCCESS("\nTemps moyen d'execution : {} secondes ---"
                                                 .format(round(mean(database.tps), 1))))
