import os
import logging
import boto3
import json
import API_data
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_from_directory
from dotenv import load_dotenv
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter
from pymongo import MongoClient

load_dotenv()  # load data from.env file
api_key = os.getenv("APIKey")  # grab the key from the file

# Initialize Flask app
app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info("app_info", "App Info, this can be anything you want", version="1.0.0")

# MongoDB Setup
mongo_uri = "mongodb://localhost:27017"  # Change this to your MongoDB URI
client = MongoClient(mongo_uri)
db = client['weather_app_db']  # Database name
collection = db['weather_data']  # Collection name

# Configure Flask logging
app.logger.setLevel(logging.INFO)  # Set log level to INFO
handler = logging.FileHandler('app.log')  # Log to a file
app.logger.addHandler(handler)

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

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
        'day': final_weather_data[0],
        'week': final_weather_data[3],
        'night': final_weather_data[1],
        'humidity': final_weather_data[2],
        'country': lon_lat_country[2],
        'city': city,
        'date': final_weather_data[4]
    }

    app.logger.info('searched for: ' + city)
    city_metric.labels(city_name=city).inc()

    # Save weather data to MongoDB
    collection.insert_one(weather)

    return render_template("index.html", weather=weather)

@app.route("/dynamodb", methods=["POST"])
def dynamodb():
    weather_d = request.form["arg"]
    dynamodb_client = boto3.client('dynamodb', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-1')
    dynamodb_client.put_item(
        TableName='weather_data', Item={'city': {'S': weather_d}}
    )
    return redirect('/')

@app.route('/telaviv', methods=["POST", "GET"])
def telaviv():
    city = 'tel aviv'
    lon_lat_country = API_data.lat_lon(city, api_key)
    if lon_lat_country == 0:
        return render_template("index.html", weather=None, error=1)

    final_weather_data = API_data.weather_data(lon_lat_country[1], lon_lat_country[0])
    if final_weather_data == 0:
        return render_template("index.html", weather=None, error=1)

    dynamodb_client = boto3.client('dynamodb', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-1')
    dynamodb_client.put_item(
        TableName='weather_data', Item={'city': {'S': str(final_weather_data)}}
    )
    return render_template('index.html')

@app.route('/metrics')
def metrics():
    return generate_latest()

@app.errorhandler(500)
def server_error(error):
    app.logger.exception('An exception occurred during a request.')
    return 'Internal Server Error', 500

@app.route('/history')
def download_file():
    return send_from_directory('./history', 'data.json', as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
