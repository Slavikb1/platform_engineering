# Flask Weather App ☀️☔️

This is a Flask (Python) application that uses api to fetch current and a week forcast weather on basis of city/country .

## Setup
- Install Dependencies
- Hit the following command
  - `pip install requirement.txt`
- Run
  - `python app.py`


## Functionality

- Takes City/Country Name as Input from the user.
- Use the api call
- Bring data and parse to JSON with costume function.
- Filter the JSON data and gives proper output. 

## Installation

Install with pip:

```
$ pip install -r requirements.txt
```

## Flask Application Structure 
```
.
├── app.py
├── README.md
├── requirements.txt
├── static
│   ├── weather2.jpg
│   └── weather.jpg
└── templates
    └── index.html

2 directories, 6 files



```

## Run Flask
### Run flask for develop
```
$ python app.py
```
In flask, Default port is `5000`

Swagger document page:  `http://127.0.0.1:5000`


## Reference

Offical Website
- [Flask](http://flask.pocoo.org/)
