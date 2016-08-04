from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, SelectField
from wtforms_components import TimeField
from wtforms.validators import DataRequired

DAYS = [("Monday", "Monday"), ("Tuesday", "Tuesday"),( "Wednesday", "Wednesday"), ( "Thursday", "Thursday"), ("Friday", "Friday")]

class FilterForm(Form):
    fallterm = BooleanField('Fall Term Checkbox',  default=False, validators=[DataRequired()])
    springterm = BooleanField('Spring Term Checkbox', default=False, validators=[DataRequired()])
    searchquery = StringField('Search Query')
    
class ConflictForm(Form):
	toInclude = BooleanField("Register another conflict time", default = False)
	dayField = SelectField('Day of Conflict', choices = DAYS)
	startTime = TimeField('Start Time')
	endTime =  TimeField('End Time')