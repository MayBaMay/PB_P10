"""Test Query parser class"""
#!/usr/bin/env python
from django.test import TestCase
from ..models import Product
from ..query_parser import QueryParser

class FilterFoundProductsTestCase(TestCase):
    """Test Query parser class"""

    def setUp(self):
        """"Set up testCase"""
        Product.objects.create(id=31,
                               name="Fàke product for db",
                               formatted_name="FAKE PRODUCT FOR DB",
                               brands="brand fake",
                               formatted_brands="BRAND FAKE",
                               reference='1')
        Product.objects.create(id=32,
                               name="Second fake prôduct",
                               formatted_name="SECOND FAKE PRODUCT",
                               brands="the wrong one",
                               formatted_brands="THE WRONG ONE",
                               reference='2')
        Product.objects.create(id=33, name="product",
                               formatted_name="PRODUCT",
                               brands="not bad",
                               formatted_brands="NOT BAD",
                               reference='3')
        self.exact_query = "product"
        self.query_name = "fàke product"
        self.query_name_brands = "fake prôduct brand"
        self.one_result_query = "Sécond"

    def test_upper_no_accent(self):
        """test upper_no_accent method"""
        parser = QueryParser(self.query_name_brands)
        self.assertEqual(parser.upper_no_accent(self.query_name_brands), 'FAKE PRODUCT BRAND')
        parser = QueryParser(self.one_result_query)
        self.assertEqual(parser.upper_no_accent(self.one_result_query), 'SECOND')

    def test_get_exact_query_set(self):
        """test get_exact_query_set method"""
        parser = QueryParser(self.query_name_brands)
        self.assertFalse(parser.get_exact_query_set().exists())
        parser = QueryParser(self.exact_query)
        self.assertEqual(parser.get_exact_query_set().count(), 1)

    def test_get_large_list(self):
        """test get_large_list method"""
        parser = QueryParser(self.exact_query)
        parser.get_large_list(0)
        self.assertEqual(parser.product_list[0].id, 31)
        parser = QueryParser(self.query_name)
        parser.get_large_list(0)
        self.assertEqual(parser.product_list[0].id, 31)
        parser = QueryParser(self.query_name_brands)
        parser.get_large_list(0)
        self.assertEqual(parser.product_list[0].id, 31)
        parser = QueryParser(self.one_result_query)
        parser.get_large_list(0)
        self.assertEqual(parser.product_list[0].id, 32)

    def test_get_final_list(self):
        """test get_final_lis methodt"""
        parser = QueryParser(self.exact_query)
        parser.get_final_list()
        self.assertEqual(parser.product_list[0].id, 33)
        self.assertEqual(len(parser.product_list), 3)

    def test_products_with_words(self):
        """test products_with_words method"""
        parser = QueryParser(self.query_name)
        self.assertEqual(parser.products_with_words().count(), 3)
        parser = QueryParser(self.query_name_brands)
        self.assertEqual(parser.products_with_words().count(), 3)
        parser = QueryParser(self.one_result_query)
        self.assertEqual(parser.products_with_words().count(), 1)

    def test_products_infos(self):
        """test products_infos method"""
        parser = QueryParser(self.query_name)
        self.assertEqual(parser.products_infos()[31],
                         ["FAKE", "PRODUCT", "FOR", "DB", "BRAND", "FAKE"])
        self.assertEqual(parser.products_infos()[32],
                         ["SECOND", "FAKE", "PRODUCT", "THE", "WRONG", "ONE"])
        self.assertEqual(parser.products_infos()[33], ["PRODUCT", "NOT", "BAD"])
        parser = QueryParser(self.query_name_brands)
        self.assertEqual(parser.products_infos()[31],
                         ["FAKE", "PRODUCT", "FOR", "DB", "BRAND", "FAKE"])
        self.assertEqual(parser.products_infos()[32],
                         ["SECOND", "FAKE", "PRODUCT", "THE", "WRONG", "ONE"])
        self.assertEqual(parser.products_infos()[33],
                         ["PRODUCT", "NOT", "BAD"])
        parser = QueryParser(self.one_result_query)
        self.assertEqual(parser.products_infos()[32],
                         ["SECOND", "FAKE", "PRODUCT", "THE", "WRONG", "ONE"])

    def test_occurences(self):
        """test occurences method"""
        parser = QueryParser(self.query_name)
        self.assertEqual(parser.occurences()[31], 2)
        self.assertEqual(parser.occurences()[32], 2)
        self.assertEqual(parser.occurences()[33], 1)
        parser = QueryParser(self.query_name_brands)
        self.assertEqual(parser.occurences()[31], 3)
        self.assertEqual(parser.occurences()[32], 2)
        self.assertEqual(parser.occurences()[33], 1)
        parser = QueryParser(self.one_result_query)
        self.assertEqual(parser.occurences()[32], 1)

    def test_order_found_products(self):
        """test order_found_products method"""
        parser = QueryParser(self.query_name_brands)
        self.assertEqual(parser.order_found_products()[0], (31, 3))
        self.assertEqual(parser.order_found_products()[1], (32, 2))
        self.assertEqual(parser.order_found_products()[2], (33, 1))
        parser = QueryParser(self.one_result_query)
        self.assertEqual(parser.order_found_products()[0], (32, 1))
