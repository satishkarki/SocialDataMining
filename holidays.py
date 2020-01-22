from flask import Flask, render_template,url_for, redirect, jsonify, request, session
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired
from flask_pymongo import PyMongo
import os
import requests
import json

app = Flask(__name__)

from pymongo import MongoClient

#Database connectivity
client=MongoClient("mongodb+srv://kaveesha:BDATGeorgian@cluster0-xs3bw.mongodb.net/test?retryWrites=true&w=majority")
db=client.get_database('annualholidays')
days=db.allholidays
days.count_documents({})
print(days.count_documents({}))

#Get data from the API
r = requests.get('https://calendarific.com/api/v2/holidays?&api_key=85f2bc8e6fcfa1b9a3b8adeaf0b1ab687f98bbe4&country=US&year=2020')

data=r.json() #dictionary
# print (type(data))
main_holiday=data.get("response") #dictionary
# print(type(main_holiday))
# print(main_holiday)
main_data=main_holiday.get("holidays") #list
# print(type(main_data))
# print(main_data)

#Write the retreieved data to a .json file
with open('happyholidays.json', 'w') as json_file:
    json.dump(main_data, json_file)
with open('happyholidays.json','r+') as up:
    data_read=json.load(up)
#Delete existing data from the database to avoid duplicates
days.delete_many({})
#Insert data into MongoDB
days.insert_many(data_read)

app.config['SECRET_KEY'] = os.urandom(24)


#=============================================================
#Form class from WTForms to handle adding and updating the database
#=============================================================
class AddForm(FlaskForm):
	name = StringField('name', validators = [InputRequired()])
	description = StringField('description', validators = [InputRequired()])
	iso = StringField('iso', validators=[InputRequired()])
	year = StringField('year', validators=[InputRequired()])
	month = StringField('month', validators=[InputRequired()])
	day = StringField('day', validators=[InputRequired()])
	type = StringField('type', validators=[InputRequired()])
	locations = StringField('locations', validators=[InputRequired()])
	#states = StringField('states', validators=[InputRequired()])

#===============================
#List all the holidays at home page
#===============================
@app.route('/home')
def index():
	holiday_list = days.find()
	return render_template("result.html",holiday_list=holiday_list)

#===============================
#Helper function to handle Bson
#===============================
import json
from bson.objectid import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

#===================================
#Create Document in the collection
#===================================

@app.route('/add', methods=["GET","POST"])
def add():
	form = AddForm()
	if form.validate_on_submit():
		name_field = form.name.data
		description_field = form.description.data
		iso_field = form.iso.data
		year_field = form.year.data
		month_field = form.month.data
		day_field = form.day.data
		type_field = form.type.data
		locations_field = form.locations.data
		#states_field = form.states.data
		data= ({'name':name_field, 'description': description_field, 'date':{'iso': iso_field},
				'date':{'datetime':{'year': year_field}}, 'date':{'datetime':{'month': month_field}}, 'date':{'datetime':{'day': day_field}},
				'type':type_field, 'locations': locations_field})
		holiday = days
		holiday.insert(data)
		return JSONEncoder().encode(data)
	return render_template("add.html", form = form)

#===================================
#Updating form
#===================================

@app.route('/updateform')
def updateform():
	id = request.args.get('id')
	holiday = days
	result_id = holiday.find_one({'_id':ObjectId(id)})
	form = AddForm(name=result_id['name'], description=result_id['description'], iso=result_id['date']['iso'],
				   year=result_id['date']['datetime']['year'], month=result_id['date']['datetime']['month'], day=result_id['date']['datetime']['day'],
				   type=result_id['type'][0], locations=result_id['locations'])
	return render_template("update.html", form=form, id = id)

#===================================
#Updating Document in the collection
#===================================
from bson import json_util
@app.route('/update/<id>', methods=["POST"])
def update(id):
	holiday = days
	form = AddForm()
	if form.validate_on_submit():
		result = holiday.update_many({'_id':ObjectId(id)},{'$set':{'name':form.name.data, 'description': form.description.data, 'iso': form.iso.data,
															  'year': form.year.data, 'month': form.month.data, 'day': form.day.data,
															  'type': form.type.data, 'locations': form.locations.data}})
	return render_template("update.html",id=id,form=form)

#===================================
#deleting Document in the collection
#===================================

@app.route('/delete/<id>')
def delete(id):
	holiday = days
	delete_record = holiday.delete_one({'_id':ObjectId(id)})
	return redirect(url_for('index'))



if __name__=='__main__':
	app.run(debug=True)




