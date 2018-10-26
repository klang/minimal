@app.route('/devices', methods=('GET', 'POST'))
def devices():
    url = "https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/devices"
    try:
        r = get_url(url)
        data = json.loads(r.text)
    except requests.exceptions.HTTPError as e:
        flash('{} - {} - has disappeared '.format(e.response.status_code, url), 'error')
        data = []
    print(data)

    data.append({"name": "string", "ip": "string", "roles": "string", "dev_cfg": "string", "site": "string"})
    data.append({"name": "string", "ip": "string", "roles": "string", "dev_cfg": "string", "site": "string"})
    data.append({"name": "string", "ip": "string", "roles": "string", "dev_cfg": "string", "site": "string"})
    return render_template('devices.html', devices=data)


    @app.route('/scratch', methods=('GET', 'POST'))
    def scratch():
        #if requests.method == 'POST':
        form = AddSiteForm()
        form.validate_on_submit()
        f2 = putSiteForm()
        if form.is_submitted():
            data = get_site(form.site_name.data)
            print(data)
            return render_template('scratch.html', form=form, form2=f2, sites=[data])
        return render_template('scratch.html', form=form, form2=f2)


    @app.route('/advanced-sites', methods=('GET', 'POST'))
    def advanced_sites():
        url = "https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/sites"
        try:
            r = get_url(url)
            data = json.loads(r.text)
        except requests.exceptions.HTTPError as e:
            flash('{} - {} - has disappeared '.format(e.response.status_code, url), 'error')
            data = []
        print(data)
        if len(data) == 1:
            print("WARNING: adding a bit of fake data for site")
            data.append({'name': 'sample 1', 'networks': 'string', 'email_ips': 'string', 'sccm_ips': 'string', 'tp_subnets': 'string', 'vtp_domain': 'string', 'vtp_enc_key': 'string'})
            data.append({'name': 'sample 2', 'networks': 'string', 'email_ips': 'string', 'sccm_ips': 'string', 'tp_subnets': 'string', 'vtp_domain': 'string', 'vtp_enc_key': 'string'})
        vlans = {}
        for site in data:
            url = "https://virtserver.swaggerhub.com/steffenschumacher/netmanager/1.0.0/sites/{}/vlans".format(site['name'])
            try:
                r = get_url(url)
                subdata = json.loads(r.text)
                if len(subdata) == 1:
                    print("WARNING: adding a bit of fake data for vlans at site")
                    subdata.append({'vlan': 1, 'kind': 'string', 'description': 'string'})
                    subdata.append({'vlan': 2, 'kind': 'string', 'description': 'string'})
                    subdata.append({'vlan': 3, 'kind': 'string', 'description': 'string'})
            except requests.exceptions.HTTPError as e:
                subdata = []
            vlans[site['name']] = subdata

        return render_template('advanced-sites.html', sites=data, vlans=vlans)


        @app.route('/site', methods=('GET', 'POST'))
    def site():
        form = searchSiteForm()
        form.validate_on_submit()
        if form.is_submitted():
            print(request.form)
            submitted_device_configuration = None
            if 'submit_button' not in request.form and 'add_device' in request.form:
                print("ADD DEVICE")

            if 'submit_button' not in request.form and 'add_device_config' in request.form:
                print("add device configuration")
                submitted_device_configuration = request.form.to_dict(flat=True)
                submitted_device_configuration.pop('csrf_token', None)
                print("SUBMITTED CONFIG", submitted_device_configuration)
            data = get_site(form.site.data)
            print("\nSITE ", data)
            data['device_configurations'].append({'name': 'string', 'model': 'string', 'mbps': 0, 'roles': ['string1', 'string2', 'string3'], 'licenses': ['string1', 'string2', 'string3'], 'categories': [0,1,2,3]})
            data['device_configurations'].append({'name': 'string', 'model': 'string', 'mbps': 0, 'roles': ['string1', 'string2', 'string3'], 'licenses': ['string1', 'string2', 'string3'], 'categories': [0,1,2,3]})
            data['device_configurations'].append({'name': 'string', 'model': 'string', 'mbps': 0, 'roles': ['string1', 'string2', 'string3'], 'licenses': ['string1', 'string2', 'string3'], 'categories': [0,1,2,3]})
            if submitted_device_configuration:
                data['device_configurations'].append(submitted_device_configuration)


            add_device = AddDevice(site_name = form.site.data)
            choices = [(device['name'], device['name']) for device in data['device_configurations']]
            add_device.dev_cfgs.choices = choices


            print("\nEXTRA DEVICE CONFIGURATIONS ", [d for d in data['device_configurations']])
            vlans = get_vlans(form.site.data)
            vlans.append({'vlan': 1, 'kind': 'string', 'description': 'string'})
            vlans.append({'vlan': 2, 'kind': 'string', 'description': 'string'})
            vlans.append({'vlan': 3, 'kind': 'string', 'description': 'string'})
            print("\nEXTRA VLANS ", vlans)
            devices = get_devices(form.site.data)
            print("\nEXTRA DEVICES ", devices)
            devices.append({'name': 'string', 'ip': 'string', 'roles': 'string', 'dev_cfg': 'string', 'site': 'string', 'serial': 'string'})
            devices.append({'name': 'string', 'ip': 'string', 'roles': 'string', 'dev_cfg': 'string', 'site': 'string', 'serial': 'string'})
            devices.append({'name': 'string', 'ip': 'string', 'roles': 'string', 'dev_cfg': 'string', 'site': 'string', 'serial': 'string'})
            return render_template('site-search.html', form=form, vlans=vlans, devices=devices, data=data, add_device=add_device)
        return render_template('site-search.html', form=form)
