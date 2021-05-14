import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import urllib.request

#First Part
links = []

url_home = 'http://books.toscrape.com/'
response = requests.get(url_home)

if response.ok:
    soup = BeautifulSoup(response.text, 'html.parser')
    nav = soup.find('ul', {'class': 'nav nav-list'}).findAll('li')
    for lis in nav:
        a = lis.find('a')
        link = a['href']
        links.append('http://books.toscrape.com/' + link)
del links[0]

# Boucle for each Category
link_category = []
links_category = []
for link_category in links:
    cat_response = requests.get(link_category)

    if cat_response.ok:
        cat_soup = BeautifulSoup(cat_response.text, 'html.parser')
        nbr = cat_soup.find('form', {'class': 'form-horizontal'}).find('strong').text

        range_page = (int(nbr) // 20)+1
        if int(nbr) <= 20:
            links_category.append(link_category)

        else:
            for nbr_page in range(1, range_page + 1):
                links_category.append(link_category.replace('index.html', 'page-') + str(nbr_page) + '.html')


# Loops for books by category
book_urls = []
for link_cat in links_category:
    books_response = requests.get(link_cat)
    if books_response.ok:
        books_soup = BeautifulSoup(books_response.text, 'html.parser')
        divs = books_soup.findAll('div', {'class': 'image_container'})
    for div_url in divs:
        a = div_url.find('a')
        link = a['href']
        link = link.lstrip('./')
        book_urls.append('http://books.toscrape.com/catalogue/' + link)

with open('P2_1_urls.txt', 'w') as file:
    for book_url in book_urls:
        file.write(book_url + '\n')

# Second Part
with open('P2_1_urls.txt', 'r') as inf:
    with open('P2_2_books.csv', 'w', newline='', encoding='utf-8-sig') as outfile:
        fieldnames = ['category', 'title', 'product_page_url', 'universal_product_code', 'price_including_tax', 'price_excluding_tax','number_available', 'product_description','review_rating','image_url']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        for row in inf:
                url = row.strip()
                response = requests.get(url)
                if response.ok:
                   image_url = []
                   soup = BeautifulSoup(response.text, 'html.parser')
                   title = soup.h1.text
                   universal_product_code = soup.find('td').text

                   category = soup.find('div', {'class': 'container-fluid page'}).findAll('li')[2].text.strip()
        
                   start_rating = soup.find('p', {'class': 'star-rating'})
                   review_rating = start_rating['class'][1]
                   
                   image = soup.find('div', {'class': 'item active'}).find('img')
                   image_link = image['src']
                   image_title = image['alt'].strip('/').replace('/', '')

                   image_link = 'https://books.toscrape.com/'+ image_link.strip('./')
                   urllib.request.urlretrieve(image_link, "books_images/"+image_title+".jpg")

                   list_p = soup.find('article', {'class': 'product_page'}).findAll('p')
                   product_description = list_p[3].text

                   tds = soup.findAll('td')
                   price_including_tax = tds[3].text.strip('Â')
                   price_excluding_tax = tds[2].text.strip('Â')
                   number_available = tds[5].text

                   writer.writerow({'category': category, 'title': str(title), 'product_page_url': str(url), 'universal_product_code': str(universal_product_code), 'price_including_tax': str(price_including_tax), 'price_excluding_tax': str(price_excluding_tax), 'number_available': str(number_available), 'product_description': str(product_description), 'review_rating': str(review_rating), 'image_url': str(image_link)})

df = pd.read_csv('P2_2_books.csv', index_col=False, names=['category', 'title', 'product_page_url', 'universal_product_code', 'price_including_tax', 'price_excluding_tax','number_available', 'product_description','review_rating','image_url'])
df.to_csv('P2_3_BooksDF.csv')
