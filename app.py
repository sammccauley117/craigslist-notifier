#!/usr/bin/python3
import sqlite3
import requests, os.path
from bs4 import BeautifulSoup
from flask import Flask
from twilio.rest import Client

# Variable initializations
DB_FILE = './posts.db'
SEARCH_URL = 'https://sfbay.craigslist.org/search/roo?sort=pricedsc&postedToday=1&search_distance=10&postal=94043&min_price=1700&max_price=2300&availabilityMode=0'
app = Flask(__name__)

# Create the sqlite database file if it doesn't already exist
if not os.path.isfile(DB_FILE):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE posts
        (pid integer, title text, link text, price integer, location text)''')


def text(message):
    '''Uses the Twilio API to send a text'''
    print('texting {}'.format(message))
    try:
        client = Client(os.environ.get('TWILIO_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))
        message = client.messages.create(
            body = message,
            from_ = os.environ.get('TWILIO_NUMBER'),
            to = os.environ.get('MY_NUMBER'))
    except:
        print('Twilio error')


@app.route('/check_posts')
def main():
    '''Main function that checks to see if there are new posts to be texted'''
    # Establish connection to the database
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    # Get craigslist posts
    source = requests.get(SEARCH_URL).text
    soup = BeautifulSoup(source, 'html.parser')
    posts = soup.findAll('li', {'class': 'result-row'})

    # Check if any posts are new and tweet them out
    for post in posts:
        # Extract data for each post
        pid = int(post['data-pid'])
        title = post.find('a', {'class': 'result-title'}).get_text().replace('\'','"')
        link = post.find('a', {'class': 'result-title'}, href=True)['href']
        price = int(post.find('span', {'class': 'result-price'}).get_text().replace('$',''))
        location = post.find('span', {'class': 'result-hood'}).get_text()
        location = location[2:-1].title() # Remove parentheses and capitalize the first letters

        # Check if the PID is new. If so, the post needs to be texted to the user and
        # added to the database
        query = """SELECT * FROM posts WHERE pid={}""".format(pid)
        cursor.execute(query)
        row = cursor.fetchone()
        if row is None:
            # Post is new, text it out
            message = '{}\n{}'.format(title, link)
            text(message)

            # Add it to the database
            query = """INSERT INTO posts VALUES ({}, "{}", "{}",
                {}, "{}")""".format(pid, title, link, price, location)
            try:
                cursor.execute(query)
            except:
                print('Bad Query: {}'.format(query))

    # Save sqlite changes
    connection.commit()
    connection.close()

    return ('', 204)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
