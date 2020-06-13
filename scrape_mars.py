
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


    # Tweet place holder while I figure out the twitter scrape here ./testPython/twitter Test.ipynb
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
    factsDf.columns = (['Mars Metrics','Measurements'])
    factsDf.set_index('Mars Metrics')

    htmlOutput = factsDf.to_html()

# # https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars
# # The website is failing to load in two browsers.  Seems like a bad thing
#     hemisphere_image_urls = [
#         {"title": "Valles Marineris Hemisphere", "img_url": "..."},
#         {"title": "Cerberus Hemisphere", "img_url": "..."},
#         {"title": "Schiaparelli Hemisphere", "img_url": "..."},
#         {"title": "Syrtis Major Hemisphere", "img_url": "..."},
#     ]

    # Scraping Wikipedia
    url_jpl = 'https://en.wikipedia.org/wiki/Chrysler_Hemi_engine'
    browser.visit(url_jpl)
    newHtml = browser.html
    soup = BeautifulSoup(newHtml, 'html.parser')
    images = soup.findAll('img')

    # creating a list of images
    extImgList = []
    count =0
    for image in images:
      extractImage = images[count]
      extractImageSrc = extractImage['src']
      extImgList.append(extractImageSrc)
      count = count +1

    # selecting the ones I like
    extractImageSrc0 = extImgList[15]
    extractImageSrc1 = extImgList[3]
    extractImageSrc2 = extImgList[16]
    extractImageSrc3 = extImgList[6]
 
    link0 = "https:" + extractImageSrc0
    link1 = "https:" + extractImageSrc1
    link2 = "https:" + extractImageSrc2
    link3 = "https:" + extractImageSrc3

    hemisphere_image_urls = [
        {"title": "5 7 Hemi", "img_url": link0},
        {"title": "Hemi in 300C", "img_url": link1},
        {"title": "6 1 Hemi", "img_url": link2},
        {"title": "FiredomeV8", "img_url": link3},
    ]



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
    return render_template('index.html', marsInfoDb=marsInfoDb, hemisphere_image_urls=hemisphere_image_urls)







if __name__ == "__main__":
    app.run(debug=True)

