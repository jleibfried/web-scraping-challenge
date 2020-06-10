
import requests
import pymongo
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, render_template

# Create an instance of our Flask app.
app = Flask(__name__)

# Create connection variable
conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)

# Route that will trigger the scrape function
@app.route("/")
def scrape():

    url = 'https://mars.nasa.gov/news/'

    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'lxml'
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Retrieve the parent divs for all articles
    firstTitle = soup.find('div', class_='content_title').text
    
    firstGraf = soup.find('div', class_="rollover_description_inner").text
    
    # Testing code
    # firstTitle = "line of dialogue"



    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    url_jpl = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url_jpl)

    try:    
        browser.click_link_by_partial_text('FULL IMAGE')

    except:
        print("Scraping Complete")
    

    newHtml = browser.html
    soup = BeautifulSoup(newHtml, 'html.parser')


    images = soup.findAll('img')
    # images.find(class_=)

    extractImage = images[3]
    extractImageSrc = extractImage['src']

    featured_image_url = 'https://www.jpl.nasa.gov' + extractImageSrc



    mars_weather = 'Sol 1801 (Aug 30, 2017), Sunny, high -21C/-5F, low -80C/-112F, pressure at 8.82 hPa, daylight 06:09-17:55'



    url = 'https://space-facts.com/mars/'

    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'html'
    soup = BeautifulSoup(response.text, 'html.parser')

    # Code from here
    # https://pythonprogramminglanguage.com/web-scraping-with-pandas-and-beautifulsoup/
    # https://stackoverflow.com/questions/50633050/scrape-tables-into-dataframe-with-beautifulsoup

    table = soup.find_all('table')[0]
    table_rows = table.find_all('tr')
    l = []
    for tr in table_rows:
        td = tr.find_all('td')
        row = [tr.text for tr in td]
        l.append(row)
    factsDf = pd.DataFrame(l)

    htmlOutput = factsDf.to_html()

# # https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars
# # The website is failing to load in two browsers.  Seems like a bad thing
#     hemisphere_image_urls = [
#         {"title": "Valles Marineris Hemisphere", "img_url": "..."},
#         {"title": "Cerberus Hemisphere", "img_url": "..."},
#         {"title": "Schiaparelli Hemisphere", "img_url": "..."},
#         {"title": "Syrtis Major Hemisphere", "img_url": "..."},
#     ]



    # Connect to a database. Will create one if not already available.
    db = client.marsdb

    # Drops collection if available to remove duplicates
    db.marsdb.drop()

    # Building DB
    db.marsdb.insert_many(
     [
        {
        "Title":    firstTitle,
        "Paragraph": firstGraf,
        "Image": featured_image_url,
        "Tweet":mars_weather,
        "Table":htmlOutput
        }
     ]
    )

   


    # sending info to index.html
    marsInfoDb = list(db.marsdb.find())
    print (marsInfoDb)
    return render_template('index.html', marsInfoDb=marsInfoDb, firstTitle=firstTitle)







if __name__ == "__main__":
    app.run(debug=True)

