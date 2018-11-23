from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, BooleanField
from wtforms_components import IntegerField


class SnowForm(FlaskForm):
    site_name = StringField('site_name',
                            description="site name",
                            validators=[validators.Regexp('^[A-Z0-9]{5,7}([-]?[A-Za-z0-9]{3,5}|)$',
                                                          flags=0,
                                                          message='site_name must follow "^[A-Z0-9]{5,7}([-]?[A-Za-z0-9]{3,5}|)$"')])
    delete_if_exists = BooleanField('delete_site', description='should this site be deleted if it exists')
    category = IntegerField('category',
                            description='category of test_site',
                            default=4,
                            validators=[validators.AnyOf(values=[4],
                                                         message='category of a test_site is 4')])

    #delete_if_exists = BooleanField('delete_if_exists', message='should this site be deleted if it exists', default=False)
    kbps = IntegerField('kbps',
                        description='symmetric wan speed', default=20000,
                        validators=[validators.AnyOf(values=[20000, 25000,50000,75000,100000],
                                                     message='Any of 20000, 25000, 50000, 75000 or 100000')])
    submit_snow = SubmitField('Add Site to SNOW')
