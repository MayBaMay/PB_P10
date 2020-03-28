#!/usr/bin/env python

"""
This module parse products in database to get closest results of searched product
"""

import unicodedata
from django.db.models import Q
from .models import Product

class QueryParser:
    """
    This class parse products in database to get closest results of searched product
    """

    def __init__(self, query):
        self.query = query
        self.product_list = []
        self.formatted_query = self.upper_no_accent(self.query)


    def upper_no_accent(self, sentence):
        """
        This method returns query formatted without accent and in upper case
        """
        query_up = sentence.upper()
        query_up_no_accent = self.no_accent(query_up)
        return query_up_no_accent

    @staticmethod
    def no_accent(sentence):
        """
        This method returns query without accent
        """
        no_accent = ''.join((c for c in unicodedata.normalize('NFD', sentence)
                             if unicodedata.category(c) != 'Mn'))
        return no_accent

    def get_final_list(self):
        """
        This method increments product_list attribute with the 12 most relevant products
        """
        i = 0
        # first get products with exactly the same name then the user query
        if self.get_exact_query_set():
            for product in self.get_exact_query_set():
                self.product_list.append(product)
        # then get a larger list if needed
        while len(self.product_list) < 12:
            try:
                self.get_large_list(i)
                i += 1
            except:
                break

    def get_exact_query_set(self):
        """
        This method returns a queryset of products with the exact query for name in database
        """
        products = Product.objects.filter(formatted_name=self.formatted_query)
        return products

    def get_large_list(self, i):
        """
        This method gets the most relevant products to add in product_list
        """
        product = Product.objects.get(id=self.order_found_products()[i][0])
        if product not in self.product_list:
            self.product_list.append(product)

    def products_with_words(self):
        """
        This method returns products matching with each formatted words in the query
        They can be contained in the name or the brand of a product
        using formatted_name and formatted_brands coloumn of database
        """
        # find all products with one on the word in it
        q_objects = Q()
        for word in self.formatted_query.split():
            if word not in ['DE', 'DES', 'LE', 'LA', 'LES', 'AU', 'AUX', 'A']:
                q_objects.add(Q(formatted_name__contains=word), Q.OR)
                q_objects.add(Q(formatted_brands__contains=word), Q.OR)
        return Product.objects.filter(q_objects).distinct()

    def products_infos(self):
        """
        For those products, get name and brand in a same list
        """
        product_dict = {}
        for product in self.products_with_words():
            name_brand_string = product.formatted_name
            name_brand_string += " "
            name_brand_string += product.formatted_brands
            list_name_brand_string = name_brand_string.split()
            product_dict[product.id] = list_name_brand_string
        return product_dict

    def occurences(self):
        """
        Then find occurences of words in query and in name_brand_string
        (one occurence by word)
        """
        occurences = self.products_infos()
        for key, value in occurences.items():
            found = 0
            for word in self.formatted_query.split():
                if word in value:
                    found += 1
            occurences[key] = found
        return occurences

    def order_found_products(self):
        """
        Finally load products references in an ordered list
        """
        return sorted(self.occurences().items(), key=lambda t: t[1], reverse=True)
