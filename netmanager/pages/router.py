from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, IntegerField, SelectField, BooleanField


class RouterConfigForm(FlaskForm):
    router = SelectField('Router', description="router", choices=[('C4321', 'Cisco 4321')])
    switch = SelectField('Switch', description="switch", choices=[('3650X-12', '3650X-12P')])
    aps = SelectField('APs', choices=[(0,0), (1,1), (2,2), (3,3)],
                      validators=[validators.NumberRange(min=0, max=3)], coerce=int)
    riverbed = BooleanField('Riverbed', description='optional')
    snow = IntegerField('Snow', description="SNOW site id")
    region = SelectField('Region', choices=[('eu-west-1', 'Ireland'),
                                            ('eu-west-2', 'London'),
                                            ('eu-west-3', 'Paris'),
                                            ('eu-central-1', 'Frankfurt')])
    serial = StringField('Serial', description='Serial number for each device to be configured')
    submit_button = SubmitField('Submit Form')

