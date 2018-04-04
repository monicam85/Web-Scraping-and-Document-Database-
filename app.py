from flask_pymongo import PyMongo
from flask import Flask, render_template, jsonify, redirect
import scrape_mars

# create instance of Flask app
app = Flask(__name__)

mongo = PyMongo(app)

@app.route('/')
def index():
    mars_mission = mongo.db.mars_mission.find_one()
    return render_template('index.html', mars_mission=mars_mission)

@app.route('/scrape')
def scrape():
    mars_mission = mongo.db.mars_mission
    data = scrape_mars.scrape()
    mars_mission.update(
        {},
        data,
        upsert=True
    )
    return redirect("http://localhost:5000/", code=302)


if __name__ == "__main__":
    app.run()
