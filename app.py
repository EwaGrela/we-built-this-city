from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    make_response
)

from flask_sqlalchemy import SQLAlchemy
from models import City, Country, Visit
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.sql import collate
from datetime import datetime
import os


#os.environ['DATABASE_URL']
# engine =create_engine('postgres://hwfontyrjvhwuz:410dd886164ee538d1df30879bd63e481636b3e6ae88724b9fcc3eaab98c0ef9@ec2-54-195-246-59.eu-west-1.compute.amazonaws.com:5432/d5trn498dlkaff')
engine =create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)
session = Session()

app = Flask(__name__)


@app.route("/")
def home():
	return "This actually works"

@app.route("/counter")
def counter():
	visit = session.query(Visit).filter(Visit.visit_id==1).with_for_update(nowait=True, of=Visit).first()
	if visit is None:
		visit = Visit(visit_id=1, counter=1)
		session.add(visit)
		session.commit()
		return str(visit.counter)
	else:
		visit.counter +=1
		session.commit()
		return str(visit.counter)
	


@app.route("/cities", methods = ["GET", "POST"])
def all_cities():
	if request.method == "GET":
		return get_city()
	elif request.method == "POST":
		return post_city()

def get_city():
	cn = request.args.get('country_name')
	lim = request.args.get('per_page')
	offs = request.args.get('page')
	all_cities = session.query(City).order_by(City.city)
	if cn is None:
		if lim is None and offs is None:
			cities = all_cities.all()
		elif lim is not None and offs is None:
			cities = all_cities.limit(int(lim)).all()
		elif lim is not None and offs is not None:
			cities = all_cities.limit(int(lim)).offset((int(offs)-1)*int(lim)).all()
	else:
		country = session.query(Country)
		my_country = country.filter(Country.country==cn).one()
		country_id = my_country.country_id
		country_cities = all_cities.filter(City.country_id==country_id)
		if lim is None and offs is None:
			cities = country_cities.all()
		elif lim is not None and offs is None:
			cities = country_cities.limit(int(lim)).all()
		elif lim is not None and offs is not None:
			cities = country_cities.limit(int(lim)).offset((int(offs)-1)*int(lim)).all()
	c = [city.city for city in cities]
	return jsonify(c)

def post_city():
	data = request.get_json()
	cities = session.query(City).all()
	countries = session.query(Country).all()
	c = [city.city for city in cities]
	country_ids = sorted([country.country_id for country in countries])
	city_ids = sorted([city.city_id for city in cities])
	last = session.query(City).filter(City.city_id==city_ids[-1]).one().city_id
	if data["country_id"] in country_ids:
		new_city = City(city_id=(last+1), city =data["city_name"], country_id =data["country_id"], last_update=datetime.utcnow())
		session.add(new_city)
		session.commit()
		new_city = {"country_id" : new_city.country_id, "city_name": new_city.city, "city_id": new_city.city_id}
		new_city = jsonify(new_city)
		return new_city
	else:
		err = {"error": "Invalid country_id" }
		err = jsonify(err)
		return make_response(err, 400)


	
	return "OK"


if __name__ == '__main__':
	app.run(debug=True)