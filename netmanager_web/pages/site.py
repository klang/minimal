from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators, IntegerField


# there must be a way to auto generate this stuff
class AddSiteForm(FlaskForm):
    site_name = StringField('site_name', description="Name of new site - must exist in SNOW, to extract the site category etc")
    users = IntegerField('users',
                         default=5,
                         description="Number of expected users",
                         validators=[validators.NumberRange(min=5,
                                                            max=30,
                                                            message='Must be between %(min) and %(max)')])
    ipphones = IntegerField('ipphones',
                            default=1,
                            description="Number physical IP Phones",
                            validators=[validators.NumberRange(min=1,
                                                               max=200,
                                                               message='Must be between %(min) and %(max)')])
    submit_add_site = SubmitField('Create new site')


class PutSiteForm(FlaskForm):
    name = StringField('name')
    networks = StringField('networks')
    email_ips = StringField('email_ips')
    sccm_ips = StringField('sccm_ips')
    tp_subnets = StringField('tp_subnets')
    vtp_domain = StringField('vtp_domain')
    vtp_enc_key = StringField('vtp_enc_key')
    # device_configurations = FieldList(FormField(DeviceConfigurationForm), min_entries=1)
    # device_configurations = HiddenField('device_configurations')
    # submit_button = SubmitField('Submit Form')


class SearchSiteForm(FlaskForm):
    site_name = StringField('site_name',
                            validators=[validators.Regexp('^[A-Z0-9]{5,7}([-]?[A-Za-z0-9]{3,5}|)$',
                                        flags=0,
                                        message='site_name not allowed')])
    submit_search_site = SubmitField('Find Site')
