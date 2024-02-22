# A very simple Flask Hello World app for you to get started with...

from flask import Flask, jsonify, request
from re import compile
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from math import ceil

app = Flask(__name__)
app.config['TIMEOUT'] = 3000  # set the timeout value to 30 seconds

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/yelp_scraper')
def yelp_scraper():
    city = str(request.args.get('arg1'))
    state = str(request.args.get('arg2'))
    address_number = int(request.args.get('arg3'))
    address_street = str(request.args.get('arg4'))

    RESULT = 0
    DIVIDE = 1
    h3_count = 0
    hotels_count = 0
    while(True):
        results_URL = "https://www.yelp.com/search?find_desc=Hotels&find_loc={0}%2C+{1}&start={2}".format(city, state, hotels_count)
        results_HTML = requests.get(results_URL)
        results_soup = BeautifulSoup(results_HTML.text)

        h1_check = results_soup.find("h1")
        try:
            if (h1_check.text == "We're sorry, the page of results you requested is unavailable."):
                break
        except:
            pass

        h3s = results_soup.find_all("h3")

        break_check = 0
        for h3 in h3s:
            #print("count: ", h3_count)
            h3_count += 1
            if (h3_count > 5):
                break_check = 1
                break

            potential_partial_URL = h3.find("span").find("a")["href"]
            potential_URL = "https://yelp.com" + potential_partial_URL

            #print("\tpotential_URL: ", potential_URL)

            potential_HTML = requests.get(potential_URL)
            potential_soup = BeautifulSoup(potential_HTML.text)

            potential_address = potential_soup.find("address").find_all("p")
            potential_address_1 = potential_address[0].find("a").find("span")
            potential_address_2 = potential_address[1].find("span")

            potential_text_1 = potential_address_1.text
            potential_text_2 = potential_address_2.text

            #print("\tpotential_text_1: ", potential_text_1)
            #print("\tpotential_text_2: ", potential_text_2)
            #print("\tstr(address_number) + \" \" + address_street: ", str(address_number) + " " + address_street)
            #print("\tpotential_text_2[:-5]: ", potential_text_2[:-6])
            #print("\tcity + \", \" + state: ", city + ", " + state)
            #print("\tbool1: ", potential_text_1 == str(address_number) + " " + address_street)
            #print("\tbool2: ", potential_text_2[:-6] == city + ", " + state)

            if ((potential_text_1 == str(address_number) + " " + address_street) and (potential_text_2[:-6] == city + ", " + state)):
                soup = potential_soup

                reviews = soup.find("h1").find_next("span").find_next("span").text.split(" ")[0]

                #print("reviews: ", reviews)

                #print("ceil(int(reviews) / 10): ", ceil(int(reviews) / 10))

                DIVIDE = ceil(int(reviews) / 10)

                comment_count = 0
                for p in range(ceil(int(reviews) / 10)):
                    reviews_URL = potential_URL + "&start=" + str(p*10)
                    reviews_HTML = requests.get(reviews_URL)
                    reviews_soup = BeautifulSoup(reviews_HTML.text)

                    comments = reviews_soup.find_all("p", {"class" : compile("comment")})

                    prev_sentiment = -2
                    break_check2 = 0
                    for comment in comments:
                        #print("comment_count: ", comment_count)

                        text = comment.find_previous("div", {"class" : compile("five-stars")}).find_next("p", {"class" : compile("comment")}).text

                        # print("\t" + text)
                        analysis=TextBlob(text)
                        sentiment = analysis.sentiment.polarity
                        if (sentiment == prev_sentiment):
                            continue
                        prev_sentiment = sentiment
                        comment_count += 1
                        if (comment_count > 20):
                            break_check2 = 1
                            break

                        RESULT += sentiment
                        #print("\tsentiment: ", sentiment)
                    if (break_check2 == 1):
                        break_check = 1
                        break
                break_check = 1
                break
        if (break_check == 1):
            break
        hotels_count += 10
        if (hotels_count > 20):
            break

    message = {'result' : (float(RESULT) / float(DIVIDE))}
    return jsonify(message)
    #print("done!")
