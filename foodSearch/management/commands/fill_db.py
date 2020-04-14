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

# test avec import des settings de prod
from pur_beurre_project.settings.production import SECRET_KEY, DATABASES

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
            sentence_unaccent = "".join(
                (c for c in unicodedata.normalize("NFD", sentence)
                 if unicodedata.category(c) != "Mn"))
            return sentence_unaccent.upper()
        except:
            return sentence

    def load_off_page(self):
        """load page of products from openfactfood"""
        print("\n")
        print("loading page "+ str(self.page))
        # use openfactfood api to load pages
        page_prods = openfoodfacts.products.get_by_facets(
            {"country": "france"}, page=self.page, locale="fr"
        )
        return page_prods

    def load_product(self, off_product):
        """
        load product's infos from openfactfood page of products into a dictionnary
        devided between required fields and optionnal fields
        """
        product_infos = {
            "required":{"error":False},
            "optional":{}
            }

        try:
            # required informations
            product_infos["required"]["reference"] = off_product["id"]
            product_infos["required"]["name"] = off_product["product_name"]
            product_infos["required"]["formatted_name"] = self.upper_unaccent(off_product["product_name"])
            product_infos["required"]["brands"] = off_product["brands"]
            product_infos["required"]["formatted_brands"] = self.upper_unaccent(off_product["brands"])
            product_infos["required"]["nutrition_grade_fr"] = off_product["nutrition_grades"]
            product_infos["required"]["url"] = off_product["url"]
            product_infos["required"]["image_url"] = off_product["image_url"]
            product_infos["required"]["image_small_url"] = off_product["image_small_url"]

        except KeyError:
            product_infos["required"]["error"] = True #keep only complete product

        if not product_infos["required"]["error"]:
            # optional informations

            try:
                product_infos["optional"]["saturated_fat_100g"] = off_product["nutriments"]["saturated-fat_100g"]
            except KeyError:
                pass
            try:
                product_infos["optional"]["carbohydrates_100g"] = off_product["nutriments"]["carbohydrates_100g"]
            except KeyError:
                pass
            try:
                product_infos["optional"]["energy_100g"] = off_product["nutriments"]["energy_100g"]
            except KeyError:
                pass
            try:
                product_infos["optional"]["sugars_100g"] = off_product["nutriments"]["sugars_100g"]
            except KeyError:
                pass
            try:
                product_infos["optional"]["sodium_100g"] = off_product["nutriments"]["sodium_100g"]
            except KeyError:
                pass
            try:
                product_infos["optional"]["salt_100g"] = off_product["nutriments"]["salt_100g"]
            except KeyError:
                pass

        return product_infos

    def load_datas(self, page, last_page):
        """method loading datas from api in the database"""

        self.initial_page = page
        self.page = page # page counter
        self.last_page = last_page # number of page wanted from the api
        start_time = time.time()

        while self.page <= self.last_page:
            page_prods = self.load_off_page()

            for off_product in page_prods:
                product_infos = self.load_product(off_product)

                if not product_infos["required"]["error"]:

                    if Product.objects.filter(name=product_infos["required"]["name"]).exists():
                        self.update_product(off_product, product_infos)
                    else:
                        self.add_product(off_product, product_infos)

            print("{} products in database".format(Product.objects.count()))
            print("{} categories in database".format(Category.objects.count()))
            tps_page = round((time.time() - start_time), 1)
            print("Temps d'execution page: {} secondes ---".format(tps_page))
            self.tps.append(tps_page)
            self.page += 1

    @staticmethod
    def keep_eng_categories(off_product):
        """
        keep only relevant categories from openfactfood datas
        Even for french products, categories are mostly in english
        """
        parsed_categories = []
        for category in off_product["categories_hierarchy"]:
            if category[0:3] == "en:":
                parsed_categories.append(category)
        return parsed_categories

    @staticmethod
    def update_categories(parsed_categories, product):
        """
        Create if needed a new category &
        Update M2M relation between the produt and categories
        """
        # insert each category in database only if products
        # has categories infos(no keyerror in product["categories_hierarchy"])

        with transaction.atomic():
            try:
                for category in parsed_categories:
                    try:
                        # try to get the category in database
                        cat = Category.objects.get(reference=category)
                    except Category.DoesNotExist:
                        # if category doesn"t exist yet, create one
                        cat = Category.objects.create(reference=category)
                        # categ = Category.objects.get(reference=category)
                    # in any case, add a relation between Category and Product
                    cat.products.add(product)
            ###### only keep cleaned datas #######
            except:
                print('error')

    def add_product(self, off_product, product_infos):
        """
        create a new product in database
        """
        with transaction.atomic():
            # insert each product in database

            try:
                new_product = Product.objects.create(
                    reference=product_infos["required"]["reference"],
                    name=product_infos["required"]["name"],
                    formatted_name=product_infos["required"]["formatted_name"],
                    brands=product_infos["required"]["brands"],
                    formatted_brands=product_infos["required"]["formatted_brands"],
                    nutrition_grade_fr=product_infos["required"]["nutrition_grade_fr"],
                    url=product_infos["required"]["url"],
                    image_url=product_infos["required"]["image_url"],
                    image_small_url=product_infos["required"]["image_small_url"],
                )
                Product.objects.filter(pk=new_product.id).update(**product_infos["optional"])

                parsed_categories = self.keep_eng_categories(off_product)
                self.update_categories(parsed_categories,
                                       new_product)

            ###### only keep cleaned datas #######
            except:
                pass

    def update_product(self, off_product, product_infos):
        """
        Update product's informations
        """
        product = Product.objects.filter(name=product_infos["required"]["name"])
        del product_infos["required"]["error"]
        product.update(**product_infos["required"])
        product.update(**product_infos["optional"])

        product = Product.objects.get(name=product_infos["required"]["name"])
        parsed_categories = self.keep_eng_categories(off_product)
        if len(parsed_categories) > Category.objects.filter(products__id=product.id).count():
            product.categories.clear()
            self.update_categories(off_product, product)


class Command(BaseCommand):
    """Update datas in database - options: reset or fill"""

    def add_arguments(self, parser):
        """Class arguments : reset or fill"""
        parser.add_argument("-r",
                            "--reset",
                            action="store_true",
                            dest="reset",
                            help="Reset database")
        parser.add_argument("-f",
                            "--fill",
                            action="store_true",
                            dest="fill",
                            help="Fill database")

    def handle(self, **options):
        """Class handler, launch reset or fill depending on option choice"""

        if options["reset"]:
            database = InitDB()
            database.reset_db()

            file = open(DB_REPORTS_FILE, "a")
            file.write("\nRESET Database the {}:--DATABASE EMPTY\n".format(datetime.datetime.now()))
            file.close()

            self.stdout.write(self.style.SUCCESS("Reset base de données effectué"))

        if options["fill"]:
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
            --- Temps moyen d"execution : {} secondes par page ---\n"""
                       .format(datetime.datetime.now(),
                               database.initial_page,
                               database.last_page,
                               Product.objects.count(),
                               Product.objects.count()-products,
                               Category.objects.count(),
                               Category.objects.count()-categories,
                               round(mean(database.tps), 1)
                               ))
            file.close()

            self.stdout.write(self.style.SUCCESS("\nTemps moyen d'execution : {} secondes ---"
                                                 .format(round(mean(database.tps), 1))))

if "__name__" = "__main__":
    print(DATABASES)
