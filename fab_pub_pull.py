import sys, os
import csv
import re

from datetime import datetime

from bs4 import BeautifulSoup

import requests

FAB_PUB_URL = "https://hcie.csail.mit.edu/fabpub/"

HEADERS = ["Year", "Paper Title", "Abstract", "Authors", "DOI", "Paper PDF", "Video URL", "Project Page", "Conference"]

OUTPUT_DIR = "./output/"
SAVE_OUTPUT = True

PRINT_OUTPUT = False

DEBUG_MODE = False
debug_print = lambda *args : print(*args) if DEBUG_MODE else None


text_lambda = lambda item : item.text.strip() if item != None else None
href_lambda = lambda item : item['href'] if item != None else None

conf_re = re.compile(r'(\([^\)]*\))')
conf_lambda = lambda conf : conf.replace("(", "").replace(")", "") if conf != None  else None

def get_fab_pub_results_csv():
    csv_headers = HEADERS
    csv_values = []

    now = datetime.now()
    page = requests.get(FAB_PUB_URL)
    text = page.text
    soup = BeautifulSoup(text, 'html5lib')
    items = soup.find_all('div', {'class': 'portfolio'})
    current_year = "-1"
    for item in items:
        page_header = text_lambda(item.find('h1', {'class': 'page-header'}))
        if (page_header != None):
            current_year = page_header
            debug_print("Current Year", current_year)
            continue
        paper = text_lambda(item.find('span', {'class': 'papertitle'}))
        if (paper != None):
            paper_year = current_year
            paper_title = paper
            paper_authors = text_lambda(item.find('span', {'class': 'paperauthors'}))
            paper_abstract = text_lambda(item.find('span', {'class': 'paperdetails'}))
            paper_doi = href_lambda(item.find('a', {'class': 'btn-doi'}))
            paper_video = href_lambda(item.find('a', {'class': 'btn-vdo'}))
            paper_page = href_lambda(item.find('a', {'class': 'btn-pages'}))
            paper_pdf = href_lambda(item.find('a', {'class': 'btn-pdf'}))

            match_conf = conf_re.findall(paper_title)
            paper_conf = conf_lambda(match_conf[-1]) if match_conf else None

            paper_item = [paper_year, paper_title, paper_abstract, paper_authors, paper_doi, paper_pdf, paper_video, paper_page, paper_conf]
            debug_print("Paper", paper_item)

            csv_values.append(paper_item)
    # sort by data year ascending
    csv_values.sort(key=lambda item: item[0])
    return [csv_headers, csv_values]

def save_output_csv(output_filename, output_header, output_data, output_dir=OUTPUT_DIR):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_filename = output_dir + "/" + output_filename
    path_to_output_file = output_filename.rsplit('/', 1)[0]
    # print(path_to_output_file)
    if not os.path.exists(path_to_output_file):
        os.makedirs(path_to_output_file)
    with open(output_filename, "w") as out_file:
        writer = csv.writer(out_file)
        writer.writerow(output_header)
        for item in output_data:
            writer.writerow(item)
        print("     >> Output saved to file: " + output_filename)


def main():
    now = datetime.now()
    date_time = now.strftime("%Y_%m_%d_%H-%M")
    output_filename = "fabpubs-" + date_time + ".csv"
    [csv_headers, csv_values] = get_fab_pub_results_csv()

    if (PRINT_OUTPUT):
        print(csv_headers, csv_values)

    if (SAVE_OUTPUT):
        save_output_csv(output_filename, csv_headers, csv_values, OUTPUT_DIR)


if __name__ == '__main__':
    main()
