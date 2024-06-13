import os
import logging
import boto3
import json
import API_data
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_from_directory
from dotenv import load_dotenv
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, generate_latest



load_dotenv()  # load data from .env file
api_key = os.getenv("APIKey")  # grab the key from the file

# initialize flask app, create object of class Flask
app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info("app_info", "App Info, this can be anything you want", version="1.0.0")


def data_history(city_name):
    data = {'Date': datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 'City': city_name}
    path = './history/data.json'
    if not os.path.exists(path):
        with open(path, 'a') as f:
            json.dump([data], f)
    elif not os.path.getsize(path) > 0:
        with open(path, 'a') as f:
            json.dump([data], f)
    else:
        with open(path, 'r') as f:
            temp = json.load(f)
            temp.append(data)
        with open(path, 'w') as f:
            json.dump(temp, f)


# Configure Flask logging
app.logger.setLevel(logging.INFO)  # Set log level to INFO
handler = logging.FileHandler('app.log')  # Log to a file
app.logger.addHandler(handler)

#view_metric = Counter('view', 'Product view', ['product'])
#buy_metric = Counter('buy', 'Product buy', ['product'])

city_metric = Counter('city', 'Cities view', ['city_name'])

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
        'day': final_weather_data[0],  # 7
        'week': final_weather_data[3],  # 7
        'night': final_weather_data[1],  # 7
        'humidity': final_weather_data[2],  # 7
        'country': lon_lat_country[2],  # 1
        'city': city,  # 1
        'date': final_weather_data[4]  # 7
    }
    
#    city_metric = Counter('city', 'Cities view', ['city_name'])

    app.logger.info('searched for: ' + city)
    city_metric.labels(city_name=city).inc()
    
    data_history(city)

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

#    weather_data = weather(city)
    dynamodb_client = boto3.client('dynamodb', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-east-1')
    dynamodb_client.put_item(
        TableName='weather_data', Item={'city': {'S': str(final_weather_data)}}
    )
    return render_template('index.html')

#@app.route('/view/<id>')
#def view_product(id):
#    view_metric.labels(product=id).inc()
#    return "View %s" % id

#@app.route('/buy/<id>')
#def buy_product(id):
#    buy_metric.labels(product=id).inc()
#    return "Buy %s" % id

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
