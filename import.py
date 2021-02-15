#server = ec2-67-202-63-147.compute-1.amazonaws.com
#database = dfhovs0hu91unn
import csv, os, webbrowser, requests
import json
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__, template_folder='template')

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
    
#Set up a secret key. Hide them secretes
secretKey = 'stay out'


# Set up database
app.config['SQLALCHEMY_DATABASE_URI']=os.getenv("DATABASE_URL")
app.config['SECRET_KEY']=secretKey

db = SQLAlchemy(app)

class Books(db.Model):
    __tablename__="Books"
    
    book_id = db.Column(db.Integer, primary_key=True)
    isbn_10 = db.Column(db.String, unique=True)
    isbn_13 = db.Column(db.String, unique=True)
    title = db.Column(db.String, unique=False)
    author = db.Column(db.String, unique=False)
    year = db.Column(db.Integer, unique=False)
    api_link = db.Column(db.String, unique=False)
    review_count = db.Column(db.Integer, unique=False)
    average_rating = db.Column(db.Float, unique=False)
    description = db.Column(db.String, unique=False)

    def __init__(self, isbn_10, isbn_13, title, author, year, api_link, review_count, average_rating, description):
        self.isbn_10 = isbn_10
        self.isbn_13 = isbn_13
        self.title = title
        self.author = author
        self.year = year
        self.api_link = api_link
        self.review_count = review_count
        self.average_rating = average_rating
        self.description = description
        
def get_feature(data, attribute, default_value):
    return data.get(attribute) or default_value
    
@app.route("/")
def index():
    with open('books.csv', 'r') as csvfile:
        itemsBook = csv.reader(csvfile, delimiter=",")
        
        linecounter = 1
        
        for row in itemsBook:
            #This is to skip the header line in the csv file
            if linecounter == 1:
                linecounter+= 1
            else:
                #Set the variables in the csv
                isbn_10 = row[0]
                title = row[1]
                author = row[2]
                year = row[3]
                #Add api that you need to set up
                getURL = 'https://www.googleapis.com/books/v1/volumes?isbn:' + isbn_10 + '&key=AIzaSyDxkZ_cVbWh9pdIzlwLIsaan9bpZmNQ6Xg'
                
                #Execute the JSON request
                res = requests.get(getURL)
                book = res.json()

               #Getting the average rating
                if res.status_code == 200:
                   if get_feature(book, 'items', 0) == 0:
                       rating = 0
                       api_link = None
                       rateCount = 0
                       description = 'No description has been provided for this book.'
                       
                   else:
                        rating = get_feature(book['items'][0]['volumeInfo'],'averageRating',0)
                        api_link = get_feature(book['items'][0],'selfLink',None)
                        rateCount = get_feature(book['items'][0]['volumeInfo'],'ratingsCount',0)
                        description = get_feature(book['items'][0]['volumeInfo'],'description','No description has been provided for this book.')
                        
                        if get_feature(book['items'][0]['volumeInfo'],'industryIdentifiers',0) == 0:
                            isbn_13 = "Not Found"
                        else:
                            #This will loop through the books that have more than one id and find ISBN_13
                            identifiers = book['items'][0]['volumeInfo']['industryIdentifiers']
                            #Set a default value if there is no ISBN_13
                            isbn_13 = "Not Found"
                            #Loop the ids and write in the isbn_13 value if it is located
                            for ids in identifiers:
                                if ids['type'] == 'ISBN_13':
                                    isbn_13 = ids['identifier']
                bookRow = Books(isbn_10, isbn_13, title, author, year, api_link, rateCount, rating, description)
                db.session.add(bookRow)
                db.session.commit()
                
        linecounter += 1
        
    return(getURL)   

URL = index()

# =============================================================================
# if __name__ =='__main__':
#     app.run(debug=True)                
#                        
# =============================================================================

