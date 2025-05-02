from flask import Flask, jsonify
import pandas as pd
import numpy as np
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# connect to the SQLite file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the tables in the db
Base = automap_base()
Base.prepare(engine, reflect=True)

# link classes to tables
measure = Base.classes.measurement
station = Base.classes.station

# create a session to use for queries
session = Session(engine)

app = Flask(__name__)

@app.route('/')
def home():
    return (
        "<h1>Hawaii Climate API</h1>"
        "<ul>"
        "<li><a href='/api/v1.0/precipitation'>Precipitation</a></li>"
        "<li><a href='/api/v1.0/stations'>Stations</a></li>"
        "<li><a href='/api/v1.0/tobs'>Temperature Obs</a></li>"
        "<li><a href='/api/v1.0/start/end'>Start/End Temps</a></li>"
        "</ul>"
        "<p style='color:red;'>Use MMDDYYYY format for dates in the URL</p>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    last_date = dt.date(2017, 8, 23)
    prev_year = last_date - dt.timedelta(days=365)

    # get all prcp data from last year
    results = session.query(measure.date, measure.prcp).filter(measure.date >= prev_year).all()
    session.close()

    # convert to dictionary with date as key
    rain = {date: prcp for date, prcp in results}
    return jsonify(rain)

@app.route("/api/v1.0/stations")
def stations():
    # get all station codes
    results = session.query(station.station).all()
    session.close()

    # flatten result and return as list
    return jsonify(list(np.ravel(results)))

@app.route("/api/v1.0/tobs")
def tobs():
    # just using last year's data from most active station
    last_date = dt.date(2017, 8, 23)
    prev_year = last_date - dt.timedelta(days=365)

    results = session.query(measure.tobs).filter(
        measure.station == 'USC00519281',
        measure.date >= prev_year
    ).all()
    session.close()

    return jsonify(list(np.ravel(results)))

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end=None):
    sel = [func.min(measure.tobs), func.max(measure.tobs), func.avg(measure.tobs)]

    if not end:
        start_dt = dt.datetime.strptime(start, "%m%d%Y")
        result = session.query(*sel).filter(measure.date >= start_dt).all()
    else:
        start_dt = dt.datetime.strptime(start, "%m%d%Y")
        end_dt = dt.datetime.strptime(end, "%m%d%Y")
        result = session.query(*sel).filter(
            measure.date >= start_dt,
            measure.date <= end_dt
        ).all()
    
    session.close()
    return jsonify(list(np.ravel(result)))

if __name__ == '__main__':
    app.run()
