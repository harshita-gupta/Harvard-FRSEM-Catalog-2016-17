from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class FilterForm(Form):
    fallterm = BooleanField('fallterm',  default=False, validators=[DataRequired()])
    springterm = BooleanField('springterm', default=False, validators=[DataRequired()])
    searchquery = StringField('searchquery')