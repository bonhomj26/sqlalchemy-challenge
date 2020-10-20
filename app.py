import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify

# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Flask Setup
app = Flask(__name__)


# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


# `/api/v1.0/precipitation`

#  * Convert the query results to a dictionary using `date` as the key and `prcp` as the value.

#  * Return the JSON representation of your dictionary.


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the dates and precipitation values
    results =   session.query(Measurement.date, Measurement.prcp)\
                       .order_by(Measurement.date)\
                       .all()

    
    # Convert to list of dictionaries to jsonify
    prcp_list = []

    for date, prcp in results:
        list_dict = {}
        list_dict[date] = prcp
        prcp_list.append(list_dict)

    session.close()

    return jsonify(prcp_list)


# * `/api/v1.0/stations`

#  * Return a JSON list of stations from the dataset. 

@app.route("/api/v1.0/stations")
def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)

    stations = {}

    # Query all stations
    results = session.query(Station.station, Station.name).all()
    for s,name in results:
        stations[s] = name

    session.close()
 
    return jsonify(stations)



# * `/api/v1.0/tobs`
# * Query the dates and temperature observations of the most active
# station for the last year of data.
  
# * Return a JSON list of temperature observations (TOBS) for the 
# previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Retrieve the last date contained in the dataset and date from one year ago
    last_date_result = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') \
                    - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query for the dates and temperature values
    results =   session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= last_date_result).\
                order_by(Measurement.date).all()

    # Convert to list of dictionaries to jsonify
    json_date_list = []

    for date, tobs in results:
        list_dict = {}
        list_dict[date] = tobs
        json_date_list.append(list_dict)

    session.close()

    return jsonify(json_date_list)



# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

# * Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
#   for a given start or start-end range.


@app.route("/api/v1.0/<start>")
def start_range(start):
    """TMIN, TAVG, and TMAX per date starting from a starting date.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    # Create a session (link) from Python to the DB
    session = Session(engine)

    return_json_list = []

    results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs))\
                        .filter(Measurement.date >= start)\
                        .group_by(Measurement.date).all()

    for date, min, avg, max in results:
        list_dict = {}
        list_dict["Date"] = date
        list_dict["TMIN"] = min
        list_dict["TAVG"] = avg
        list_dict["TMAX"] = max
        return_json_list.append(list_dict)

    session.close()    

    return jsonify(return_json_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end_range(start,end):
    """TMIN, TAVG, and TMAX per date for a date range.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    # Create a session (link) from Python to the DB
    session = Session(engine)

    range_list = []

    results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs))\
                        .filter(and_(Measurement.date >= start, Measurement.date <= end))\
                        .group_by(Measurement.date).all()

    for date, min, avg, max in results:
        list_dict = {}
        list_dict["Date"] = date
        list_dict["TMIN"] = min
        list_dict["TAVG"] = avg
        list_dict["TMAX"] = max
        range_list.append(list_dict)

    session.close()    

    return jsonify(range_list)

if __name__ == '__main__':
    app.run(debug=True)