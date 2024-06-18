import os
import boto3
import json
import API_data
from datetime import datetime
from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, send_from_directory
from dotenv import load_dotenv

load_dotenv()  # load data from .env file
api_key = os.getenv("APIKey")  # grab the key from the file

# initialize flask app, create object of class Flask
app = Flask(__name__)

# MongoDB configuration
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.weather_db  # Use the appropriate database name
searches_collection = db.searches  # Collection to store searches

@app.route("/", methods=['POST', 'GET'])  # GET is used to request data from a specified resource
def index():  # POST is used to send data to a server to create/update a resource.
    if request.method == 'GET':
        return render_template("index.html", weather="")

    city = request.form['Search']

    lon_lat_country = API_data.lat_lon(city, api_key)
    if lon_lat_country == 0:
        app.logger.error('error: no_data')
        return render_template("index.html", weather=None, error=1)

    final_weather_data = API_data.weather_data(lon_lat_country[1], lon_lat_country[0])
    if final_weather_data == 0:
        app.logger.error('error: no_data')
        return render_template("index.html", weather=None, error=1)

    weather = {
        'day': final_weather_data[0],  # 7
        'week': final_weather_data[3],  # 7
        'night': final_weather_data[1],  # 7
        'humidity': final_weather_data[2],  # 7
        'country': lon_lat_country[2],  # 1
        'city': city,  # 1
        'date': final_weather_data[4]  # 7
    }

    # Save the search to MongoDB
    search_entry = {
        'city': city,
        'country': lon_lat_country[2],
        'search_time': datetime.now().isoformat()
    }
    searches_collection.insert_one(search_entry)

    return render_template("index.html", weather=weather)


@app.errorhandler(500)
def server_error(error):
    app.logger.exception('An exception occurred during a request.')
    return 'Internal Server Error', 500


if __name__ == "__main__":
    app.run(host="0.0.0.0")
