#!/usr/bin/env python

"""This module is called to get substitutes for the foodSearch app"""

import time
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Category, Favorite, Product

def fct_sort_dict(value):
    """
    Function returning the 'nb' value from a dictionnary
    It is used to sort products infos dictionnary in
    get_most_relevant_products method of ResultsParser clas
    """
    return value['nb']

class ResultsParser:
    """
    This class parses products in database to find the most relevant substitute
    ordered by nutriscore
    """

    def __init__(self, product_id, current_user):
        start_time = time.time()
        self.product = Product.objects.get(id=product_id)
        self.current_user = current_user
        self.all_results = self.products_same_categories()
        self.relevant_results_queryset = self.get_results_queryset()
        self.results_infos = self.get_results_dict_with_favorite_info()

        if self.relevant_results_queryset.count() > 6:
            self.paginate = True
        else:
            self.paginate = False

    def products_same_categories(self):
        """
        This method gets substitutes from same catgories than the product searched.
        Are kept only the 2 last catgegories which are the most specific
        Are kept only products with a better nutriscore
        (or nustriscore A if searched product has a nutriscore A)
        It calls a method compare_products_categories which count occurences
        of categories between searched product and substitute
        """
        results = []
        loaded_products_ids = []
        # found categories linked to this product
        found_categories = Category.objects.filter(products__id=self.product.id)
        nb_found_categories = found_categories.count()

        # get 3 most specifics categories of the product (last 3)
        if nb_found_categories > 3:
            specific_categories = found_categories[nb_found_categories-3: nb_found_categories]
        else:
            specific_categories = found_categories

        if self.product.nutrition_grade_fr == 'a':
            #for each category of the product asked
            for category in specific_categories:
                # for product in this category
                compared_products = Product.objects.filter(categories__reference=category.reference)
                for compared_prod in compared_products:
                    if compared_prod.nutrition_grade_fr == self.product.nutrition_grade_fr:
                        self.compare_products_categories(results,
                                                         loaded_products_ids,
                                                         compared_prod,
                                                         found_categories)
        else:
            #for each category of the product asked
            for category in specific_categories:
                # for product in this category
                compared_products = Product.objects.filter(categories__reference=category.reference)
                for compared_prod in compared_products:
                    if compared_prod.nutrition_grade_fr < self.product.nutrition_grade_fr:
                        self.compare_products_categories(results,
                                                         loaded_products_ids,
                                                         compared_prod,
                                                         found_categories)
        return results

    @staticmethod
    def compare_products_categories(results,
                                    loaded_products_ids,
                                    compared_prod,
                                    found_categories):
        """
        This method returns a dictionnary with substitute's id and occurences
        of categories between searched product and substitute
        """
        # avoid duplication
        if compared_prod.id not in loaded_products_ids:
            # get common categories for each product and occurences with the searched product
            count_same_categories = 0 #count nb of categories in common
            common_categories = [] #id of those categories
            for compared_category in Category.objects.filter(products__id=compared_prod.id):
                if compared_category in found_categories:
                    if compared_category.id not in common_categories:
                        common_categories.append(compared_category.id)
                        count_same_categories += 1
            # save product as already treated, avoid duplications
            loaded_products_ids.append(compared_prod.id)
            # get informations in dictionnary contained in the list results
            results.append({'id':compared_prod.id, 'nb':count_same_categories})

    def get_most_relevant_products(self):
        """
        This method sorts results with the most accurences of categories
        We chose to keep the 24 first of them
        """
        # get the 24 firsts most relevant products in an ordered queryset
        results = sorted(self.all_results, key=fct_sort_dict, reverse=True)
        results24 = results[0:24]
        return results24

    def get_results_queryset(self):
        """
        This method get queryset of the products obtained with[]
        get_most_relevant_products method
        """
        q_objects = Q()
        for item in self.get_most_relevant_products():
            q_objects.add(Q(id=item['id']), Q.OR)
        result_queryset = Product.objects.filter(q_objects).order_by('nutrition_grade_fr')
        return result_queryset

    def get_results_dict_with_favorite_info(self):
        """
        This method add the information if the product was saved as favorite or not
        in a dictionnary: {product : True/False}
        """
        # result in dictionnary with key=object & value=boolean(product already in favorite)
        results_infos = []
        for result in self.relevant_results_queryset:
            if self.current_user.is_authenticated:
                if Favorite.objects.filter(substitute=result, user=self.current_user).exists():
                    results_infos.append({result: "saved"})
                else:
                    results_infos.append({result: "unsaved"})
            else:
                results_infos.append({result: "unsaved"})
        return results_infos

    def paginator(self, page):
        """
        This method returns results per page (6 results per page)
        """
        if self.paginate:
            paginator = Paginator(self.results_infos, 6)
            page_results = paginator.get_page(page)
        else:
            page_results = self.results_infos
        return page_results
