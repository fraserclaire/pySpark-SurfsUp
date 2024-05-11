# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import pandas as pd
import datetime
from datetime import datetime, timedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Input date of interest ('%Y-%m-%d'): /api/v1.0/<start><br/>"
        f"Input date range of interest ('%Y-%m-%d'): /api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    most_recent_date = datetime.strptime(most_recent, '%Y-%m-%d').date()
    # Calculate the date one year from the last date in data set.
    minus_one_year = most_recent_date - timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    last_year = session.query(measurement.date, measurement.prcp).filter(measurement.date > minus_one_year).all()
    last_year

    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    pandas_last_year = pd.DataFrame(last_year, columns=['date', 'precipitation'])
    pandas_last_year

    # Sort the dataframe by date
    sorted_pd_last_year = pandas_last_year.sort_values(by='date')
    sorted_pd_last_year
    columns = ['date', 'precipitation']
    diction = pandas_last_year[columns].to_dict(orient='records')
    return jsonify(diction)

@app.route("/api/v1.0/stations")
def stations():
    unique_stations = session.query(measurement.station).group_by(measurement.station).all()
    station_list = list(np.ravel(unique_stations))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    most_recent_date = datetime.strptime(most_recent, '%Y-%m-%d').date()
    # Calculate the date one year from the last date in data set.
    minus_one_year = most_recent_date - timedelta(days=365)
    
    most_active_station = session.query(measurement.station, func.count()).group_by(measurement.station).order_by(func.count().desc()).all()[0][0]
    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    last_year_temps = session.query(measurement.date, measurement.tobs).filter(measurement.date > minus_one_year, measurement.station == most_active_station).all()
    last_year_temps

    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    pandas_last_year_temps = pd.DataFrame(last_year_temps, columns=['date', 'temperature'])
    columns=['date', 'temperature']
    diction2 = pandas_last_year_temps[columns].to_dict(orient='records')
    return jsonify(diction2)

@app.route("/api/v1.0/<start_date>")
def get_start(start_date):
    start_data = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date == start_date).all()
    start_data_df = pd.DataFrame(start_data, columns=['TMIN', 'TMAX', 'TAVG'])
    columns=['TMIN', 'TMAX', 'TAVG']
    diction3 = start_data_df[columns].to_dict(orient='records')
    return jsonify(diction3)

@app.route("/api/v1.0/<start_date>/<end_date>")
def startend(start_date, end_date):
    start_data = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date.between(start_date, end_date)).all()
    start_data_df = pd.DataFrame(start_data, columns=['TMIN', 'TMAX', 'TAVG'])
    columns=['TMIN', 'TMAX', 'TAVG']
    diction4 = start_data_df[columns].to_dict(orient='records')
    return jsonify(diction4)


if __name__ == '__main__':
    app.run(debug=True)