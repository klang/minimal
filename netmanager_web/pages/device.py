from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, HiddenField, validators
from wtforms.validators import DataRequired
from wtforms_components import IntegerField


class AddDeviceConfigurationForm(FlaskForm):
    name = StringField('name')
    model = StringField('model')
    mbps = IntegerField('mbps')
    roles = StringField('roles')
    licenses = StringField('licenses')
    categories = StringField('categories')


class DeviceForm(FlaskForm):
    site_name = StringField('site_name',
                            description="site name",
                            validators=[validators.Regexp('^[A-Z0-9]{5,7}([-]?[A-Za-z0-9]{3,5}|)$',
                                                          flags=0,
                                                          message='site_name not allowed')])
    dev_cfg = StringField('dev_cfg', description="viable device configuration")
    # building = StringField('building',
    #                       description="3 letter building name",
    #                       validators=[validators.Regexp('[A-Z0-9]{3}', flags=0, message='3 letter building name')])
    df = StringField('df',
                     description="3 letter distribution frame - I01 for IDF01, M01 for MDF01",
                     validators=[validators.Regexp('[MIL][0-9]{2}',
                                                   flags=0,
                                                   message='3 letter distribution frame - I01 for IDF01, M01 for MDF01')])
    serial = StringField('serial', description="Chassis serial number")
    # stack_partner = StringField('stack_partner', description="use the assigned host as the primary device in a stack, this host should join")
    # auto_connect = BooleanField('auto_connect', description="When true, connections to preexisting site devices will be automatically generated")
    # wan_line = StringField('wan_line', description="for dmvpn/mpls roles, a SNOW wan name to retrieve wan details")
    submit_device = SubmitField('Add Device')


class AddDeviceForm(FlaskForm):
    site_name = HiddenField('site_name')
    dev_cfg = SelectField('dev_cfg', validators=[DataRequired()], id='dev_cfg', description="DeviceConfigurations")
    submit_add_device = SubmitField('Add Device')
