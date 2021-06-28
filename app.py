import numpy as np
import sqlalchemy
import datetime as dt
from datetime import datetime
from datetime import date, timedelta
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base ()
#reflecting the tables
Base.prepare(engine,reflect=True)
#connecting with each table
Measurement = Base.classes.measurement
Station = Base.classes.station
#getting the link
session = Session(engine)

#calling the flask
app = Flask(__name__)

@app.route("/")
def Home():
    """List all available api routes."""
    return (
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&lt;start&gt;<br>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>")
    

#defyining the call for precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    #getting the max day
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    max_date= datetime.strptime(max_date, '%Y-%m-%d')
    first_time= max_date-timedelta(days=366)
    #the last 12 months of precipitation
    year= session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= first_time).order_by(Measurement.date).all()
    #closing the session
    session.close()
    # Convert list of tuples into normal list
    precip = []
    for date, prcp in year:
        p_dict = {}
        p_dict["Date"] = date
        p_dict["Precipitation"] = prcp
        precip.append(p_dict)
    return jsonify(precip)

#creating the station 
@app.route("/api/v1.0/stations")
def stations():
    # Create session from Python to DB
    session = Session(engine)
    # Query list of stations
    list_stations=session.query(Station.station).all()
    session.close()
    # Convert list of tuples into normal list
    stations = list(np.ravel(list_stations))
    return jsonify(stations)

#creating the tob
@app.route("/api/v1.0/tobs")
def tobs():
    # Create session from Python to DB
    session = Session(engine)
    # Query most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).order_by(func.count(Measurement.tobs).desc()).all()
    most_active_stations = active_stations[0][0]
    # Defining Last year
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    max_date= datetime.strptime(max_date, '%Y-%m-%d')
    first_time= max_date-timedelta(days=366)
    # Query the last 12 months of temperature observation data for this station
    tempatures = session.query(Measurement.tobs).filter(Measurement.station == most_active_stations ).filter(Measurement.date >= first_time).order_by(Measurement.date).all()
    session.close()
    # Convert list of tuples into normal list
    yt_obs = list(np.ravel(tempatures))
    return jsonify(yt_obs)
 
#creating the start route    
@app.route('/api/v1.0/<start>')
def start(start = None):
    # Create session from Python to DB
    session = Session(engine)
    # Selection
    start_select = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    start_select = list(start_select)
    return jsonify(start_select)

#creating the connection with the start and end    
@app.route('/api/v1.0/<start>/<end>')
def end(start = None, end = None):
    # Create session from Python to DB
    session = Session(engine)
    # Selection
    end_select = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).group_by(Measurement.date).all()
    end_select  = list(end_select )
    return jsonify(end_select)    

if __name__ == '__main__':
    app.run(debug=True)
