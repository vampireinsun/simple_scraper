"""
An example of solution for scraping the content from certain web sites.
Use build-in HTMParser to parse the html page

Assumption:
The rules of scraping the data from the testing page are always based on the curent format of this testing pages.
- Use the value of "class" attribute for certain element is key rule for this implementation rather than relying on
certain document structure or certain path.
- Because the current testing page only has one page, there will be unknown format for this and no implementation for
handling multiple pages in this solution.

"""
from utils import *
from HTMLParser import HTMLParser
import json
import argparse
import os

__author__ = 'monica'


SAINT_BURY_GROCERY_SCRAPE_URL = "http://hiring-tests.s3-website-eu-west-1.amazonaws.com/" \
                                "2015_Developer_Scrape/5_products.html"


class GroceryListParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.product_links = []

        self.product_tag_path = ""
        self.current_tag_path = ""

    def feed(self, data, product_list):
        self.product_links = product_list
        HTMLParser.feed(self, data)

    def handle_starttag(self, tag, attributes):
        self.current_tag_path = self.current_tag_path + ":" + tag

        if tag == "div":
            return_attr_value = return_value_via_key(attributes, "class")
            if return_attr_value is not None:
                if return_attr_value == "productInfo":
                    self.product_tag_path = self.current_tag_path

        if tag == "a":
            if self.current_tag_path.startswith(self.product_tag_path) and self.product_tag_path != "":
                return_attr_value = return_value_via_key(attributes, "href")
                if return_attr_value is not None:
                    self.product_links.append(return_attr_value)

    def handle_endtag(self, tag):
        pos = self.current_tag_path.rfind(tag)
        self.current_tag_path = self.current_tag_path[:pos-1]

        if len(self.current_tag_path) < len(self.product_tag_path):
            self.product_tag_path = ""


class GroceryDetailInfoParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_stack = []

        self.title = ""
        self.unit_price = -1
        self.unit_price_str = ""
        self.size = ""
        self.description = ""

        self.product_summary_tag_path = ""
        self.current_tag_path = ""

        self.is_title_part = False
        self.is_price_part = False

        self.previous_tag = ""
        self.previous_attributes = {}
        self.previous_data = ""

        self.current_tag = ""
        self.current_attributes = {}
        self.current_data = ""

        self.is_description_scope = False
        self.is_size_scope = False

    def feed(self, data):
        self.title = ""
        self.unit_price = -1
        self.unit_price_str = ""
        self.size = ""
        self.description = ""
        HTMLParser.feed(self, data)

    def handle_starttag(self, tag, attributes):
        self.current_tag_path = self.current_tag_path + ":" + tag

        self.current_data = self.current_data.strip(" \t\n")

        self.previous_data = self.current_data
        self.previous_tag = self.current_tag
        self.previous_attributes = self.current_attributes

        self.current_tag = tag
        self.current_attributes = attributes
        self.tag_stack.append(tag)
        self.current_data = ""

        if tag == "div":
            return_attr_value = return_value_via_key(attributes, "class")
            if return_attr_value is not None:
                if return_attr_value == "productSummary":
                    self.product_summary_tag_path = self.current_tag_path

                if return_attr_value == "productText":
                    if self.previous_tag == "h3":
                        return_attr_value1 = return_value_via_key(self.previous_attributes, "class")
                        if return_attr_value1 is not None:
                            if return_attr_value1 == "productDataItemHeader":
                                if self.previous_data == "Description":
                                    self.is_description_scope = True
                                if self.previous_data == "Size":
                                    self.is_size_scope = True

        if tag == "h1":
            if self.current_tag_path.startswith(self.product_summary_tag_path) and self.product_summary_tag_path != "":
                self.is_title_part = True

        if tag == "p":
            return_attr_value = return_value_via_key(attributes, "class")
            if return_attr_value is not None:
                if return_attr_value == "pricePerUnit" and \
                        self.current_tag_path.startswith(self.product_summary_tag_path) \
                        and self.product_summary_tag_path != "":
                    self.is_price_part = True

    def handle_endtag(self, tag):
        self.is_price_part = False
        self.is_title_part = False

        if tag == "div":
            self.is_description_scope = False
            self.is_size_scope = False

        pos = self.current_tag_path.rfind(tag)
        self.current_tag_path = self.current_tag_path[:pos-1]

        if len(self.current_tag_path) < len(self.product_summary_tag_path):
            self.product_summary_tag_path = ""

    def handle_data(self, data):

        clear_text = str(data).strip(" \t\n")
        self.current_data = self.current_data + data

        if self.is_title_part:
            self.title += clear_text

        if self.is_price_part:
            clear_text = clear_text.strip("/")
            clear_text = clear_text.strip("\xc2\xa3")
            if clear_text != "":
                try:
                    self.unit_price = float(clear_text)
                except ValueError:
                    self.unit_price = -1

        if self.is_description_scope:
            self.description += clear_text

        if self.is_size_scope:
            self.size += clear_text


class SaintBuryGroceryData(object):

    def __init__(self):
        self.data = {"results": [], "total": 0}
        self.new_item = {}

    def add_new_item(self):
        self.new_item = {}
        self.data["results"].append(self.new_item)

    def add_item_property(self, key, value):
        self.new_item[key] = value

    def statistic(self):
        total = 0.00
        for item in self.data["results"]:
            if "unit_price" in item:
                total += item["unit_price"]
        self.data["total"] = format(total, ".2f")


class SaintBuryGroceryScraper (object):

    def __init__(self, start_url, data_collector, grocery_list_parser, grocery_item_parser):
        self.start_url = start_url
        self.product_list = []
        self.data_collector = data_collector
        self.grocery_list_parser = grocery_list_parser
        self.grocery_item_parser = grocery_item_parser

    def start(self):
        data = request_content_from_http(self.start_url)
        self.grocery_list_parser.feed(data, self.product_list)
        for item in self.product_list:
            self.data_collector.add_new_item()
            item_data = request_content_from_http(item)
            self.grocery_item_parser.feed(item_data)
            self.data_collector.add_item_property("title", self.grocery_item_parser.title)
            self.data_collector.add_item_property("size", self.grocery_item_parser.size)
            self.data_collector.add_item_property("unit_price", self.grocery_item_parser.unit_price)
            self.data_collector.add_item_property("description", self.grocery_item_parser.description)
        self.data_collector.statistic()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='The script for scraping the content of grocery from saintbury sample website.')

    parser.add_argument(
        '-u', '--url', help='The URL you want to scrape data from.', default=SAINT_BURY_GROCERY_SCRAPE_URL)

    parser.add_argument(
        '-o', '--output', help='The file you want to export the data to', required=True)

    check_arguments = True

    args = parser.parse_args()

    output_path = args.output.replace(os.path.basename(args.output), "")
    if not os.path.exists(output_path):
        check_arguments = False
        parser.error("The location (%s) for storing the output data does not exist!" % output_path)

    if os.path.exists(args.output):
        print("The output file(%s) has been existed, it will be overwritten." % args.output)

    if check_arguments:
        grocery_data = SaintBuryGroceryData()
        grocery_list_parser = GroceryListParser()
        grocery_item_parser = GroceryDetailInfoParser()
        grocery_scraper = SaintBuryGroceryScraper(args.url, grocery_data, grocery_list_parser,
                                                  grocery_item_parser)
        grocery_scraper.start()
        export_data_content = json.dumps(grocery_data.data, indent=4)
        write_to_file(args.output, export_data_content)
        print export_data_content
