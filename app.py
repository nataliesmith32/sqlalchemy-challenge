import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

##Setting up the prcp route
@app.route("/api/v1.0/precipitation")
def precipitation():

# Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Precipitation Data"""
# Query all Precipitation
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= "2016-08-23").\
        all()

    session.close()

# Convert the prcp data list to a dictionary
    all_prcp = []
    for date, prcp  in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
               
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

##Setting up the station route
@app.route("/api/v1.0/stations")
def stations():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Stations"""
    # Query all Stations
    results = session.query(station.station).\
                 order_by(station.station).all()

    session.close()

    # Convert list of tuples into list to work with
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

##Setting up the TOBS route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all TOBS"""
    # Query TOBS
    results = session.query(measurement.date, measurement.tobs, measurement.prcp).\
                filter(measurement.date >= '2016-08-23').\
                filter(measurement.station=='USC00519281').\
                order_by(measurement.date).all()

    session.close()

    # Convert the tobs data list to a dictionary
    all_tobs = []
    for prcp, date, tobs in results:
        tobs_dict = {}
        tobs_dict["prcp"] = prcp
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

##Setting up the start date routes for first half of calculations  
@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #set up sel 
    sel = [func.min(measurement.tobs), 
            func.avg(measurement.tobs), 
            func.max(measurement.tobs)]

    #convert enteries into proper date formatting
    start_date_dt = dt.datetime.strptime(start_date, '%Y-%m-%d')

    """Return a list of min, avg and max tobs for a start date"""
    # Query all tobs
    results = session.query(*sel).\
                filter(measurement.date >= start_date_dt).all()

    session.close()

    # Create a dictionary from the row data and append to a list of start_date_tobs
    start_date_tobs = []
    for min, avg, max in results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["Minimum Temperature"] = min
        start_date_tobs_dict["Average Temperature"] = avg
        start_date_tobs_dict["Maximum Temperature"] = max
        start_date_tobs.append(start_date_tobs_dict) 
    
    return jsonify(start_date_tobs)

@app.route("/api/v1.0/<start_date>/<end_date>")
def all_dates(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #set up sel 
    sel = [func.min(measurement.tobs), 
            func.avg(measurement.tobs), 
            func.max(measurement.tobs)]

    #convert enteries into proper date formatting
    start_date_dt = dt.datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = dt.datetime.strptime(end_date, "%Y-%m-%d")

    """Return a list of min, avg and max tobs for start and end dates"""
    # Query all tobs

    results = session.query(*sel).\
                filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    session.close()
  
    # Create a dictionary from the row data and append to a list of start_end_date_tobs
    alldates_tobs = []
    for min, avg, max in results:
        alldates_tobs_dict = {}
        alldates_tobs_dict["Minimum Temperature"] = min
        alldates_tobs_dict["Average Temperature"] = avg
        alldates_tobs_dict["Maximum Temperature"] = max
        alldates_tobs.append(alldates_tobs_dict) 
    

    return jsonify(alldates_tobs)

if __name__ == "__main__":
    app.run(debug=True)