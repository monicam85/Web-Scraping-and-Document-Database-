"""
"""
from splinter import Browser
from bs4 import BeautifulSoup
import re
import pandas as pd
import pymongo

def getNews():
    startBrowser()
    url = 'https://mars.nasa.gov/news'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    result = soup.find(attrs={"class": "list_text"})

    with browser:
        try:
            # Identify and return title of news
            news_title = result.a.text
            # Identify and return news paragraph
            news_p = result.find(attrs={"class": "article_teaser_body"}).text

            # Run only if news title, and paragraph are available
            if (news_title and news_p):

                # Dictionary to be inserted as a MongoDB document
                post = {
                    'title': news_title,
                    'news_p': news_p,
                }
        except Exception as e:
            print(e)  
    return post

def getFeaturedImage():
    startBrowser()
    img_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    img_url_base= img_url[:24]
    featured_image_url =[]

    browser.visit(img_url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    browser.click_link_by_partial_text('FULL IMAGE')
    browser.is_element_present_by_text('fancybox-image', wait_time=4)
    with browser:
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        featured_image_url = soup.find('img', attrs={"class": "fancybox-image"})['src']
        featured_image_url = img_url_base + featured_image_url
    return featured_image_url

def getWeather():
    startBrowser()
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(weather_url)
    with browser:
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        mars_weather = soup.find(text=re.compile('Sol'))
    return mars_weather

def getFacts():
    startBrowser()
    mars_facts_url = 'https://space-facts.com/mars/'
    results = pd.read_html(mars_facts_url, attrs={'id': 'tablepress-mars'}, flavor=['bs4'])
    keys=[]
    values =[]
    for key, value in results[0]._values:
        keys.append(key.strip(':'))
        values.append(value)
    mars_facts = dict(zip(keys, values))
    return mars_facts

def getHemisphereImages():
    startBrowser()
    img_hemis_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    img_hemis_url_base = img_hemis_url[:29]
    hemisphere_image_urls = []
    browser.visit(img_hemis_url)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    links_found = soup.find_all(attrs={"class": 'description'})

    with browser:
        for link in links_found:
            try:
                title = link.a.text
                browser.click_link_by_partial_text(title)
                curr_html = browser.html
                soup = BeautifulSoup(curr_html, 'html.parser')
                result = [x['src'] for x in soup.findAll('img', attrs={"class": "wide-image"})]
                img_url = img_hemis_url_base + result[0]
                img_dict = {'title': title, 'img_url': img_url}
                hemisphere_image_urls.append(img_dict)
            except Exception as e:
                print(e)
            finally:
                browser.back()
    return hemisphere_image_urls

def startBrowser():
    global browser
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=True)

def scrape():
    news = getNews()
    feature_image = getFeaturedImage()
    weather = getWeather()
    facts = getFacts()
    hemisphere_images = getHemisphereImages()

    scraped = {'news': news,
    'feature_image': feature_image,
    'weather': weather,
    'facts': facts,
    'hemisphere_images': hemisphere_images
    }
    return scraped


if __name__ == '__main__':
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)

    # Define database and collection
    db = client.mars_mission_db
    collection = db.items

    scrape()

