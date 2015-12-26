import unittest
from utils import *
from scraper import GroceryDetailInfoParser, SaintBuryGroceryData, GroceryListParser, SaintBuryGroceryScraper
import json
import hashlib

__author__ = 'monica'


class TestGroceryListParser(unittest.TestCase):

    def setUp(self):
        self.product_list_parser = GroceryListParser()

    def test_not_found(self):
        html_content = read_file_content("./fixtures/product_list_case1.txt")
        product_list = []
        self.product_list_parser.feed(html_content, product_list)
        self.assertEqual(len(product_list), 0, "There shall be no product list found")

    def test_found1(self):
        html_content = read_file_content("./fixtures/product_list_case2.txt")
        product_list = []
        self.product_list_parser.feed(html_content, product_list)
        self.assertEqual(len(product_list), 1, "There shall be only one item found")

    def test_found2(self):
        html_content = read_file_content("./fixtures/product_list_case3.txt")
        product_list = []
        self.product_list_parser.feed(html_content, product_list)
        self.assertEqual(len(product_list), 2, "There shall be two items found")


class TestGroceryDetailInfoParser(unittest.TestCase):

    def setUp(self):
        self.product_parser = GroceryDetailInfoParser()

    def test_title(self):
        html_content = read_file_content("./fixtures/product_title_case1.txt")
        self.product_parser.feed(html_content)
        self.assertEqual(self.product_parser.title, "")
        html_content = read_file_content("./fixtures/product_title_case2.txt")
        self.product_parser.feed(html_content)
        self.assertEqual(self.product_parser.title, "title1")

    def test_unit_price(self):
        html_content = read_file_content("./fixtures/product_unit_price_case1.txt")
        self.product_parser.feed(html_content)
        self.assertEqual(self.product_parser.unit_price, -1)
        html_content = read_file_content("./fixtures/product_unit_price_case2.txt")
        self.product_parser.feed(html_content)
        self.assertEqual(self.product_parser.unit_price, 3.5)

    def test_size(self):
        html_content = read_file_content("./fixtures/product_size_case1.txt")
        self.product_parser.feed(html_content)
        self.assertEqual(self.product_parser.size, "")
        html_content = read_file_content("./fixtures/product_size_case2.txt")
        self.product_parser.feed(html_content)
        self.assertEqual(self.product_parser.size, "666g")

    def test_description(self):
        html_content = read_file_content("./fixtures/product_desc_case1.txt")
        self.product_parser.feed(html_content)
        self.assertEqual(self.product_parser.description, "")
        html_content = read_file_content("./fixtures/product_desc_case2.txt")
        self.product_parser.feed(html_content)
        self.assertEqual(self.product_parser.description, "test")

    def tearDown(self):
        pass


class TestSaintBuryGroceryScraper(unittest.TestCase):

    def test_scraper_result(self):
        """
        A integration test
        """
        test_url = "http://hiring-tests.s3-website-eu-west-1.amazonaws.com/" \
                                "2015_Developer_Scrape/5_products.html"
        test_grocery_data = SaintBuryGroceryData()
        test_grocery_list_parser = GroceryListParser()
        test_grocery_item_parser = GroceryDetailInfoParser()
        test_grocery_scraper = SaintBuryGroceryScraper(test_url, test_grocery_data, test_grocery_list_parser,
                                                  test_grocery_item_parser)
        test_grocery_scraper.start()
        export_data_content = json.dumps(test_grocery_data.data, indent=4)
        compared_content = read_file_content("./fixtures/example_data.json")
        self.assertEqual(hashlib.sha1(export_data_content).hexdigest(), hashlib.sha1(compared_content).hexdigest())

if __name__ == '__main__':
    unittest.main()
