# Use the comma.ai API with Home Assistant to keep tabs on your EON
### Description: Gets data from via the comma API. Nothing special runs on the EON, which means this works on 100% stock openpilot and chffrplus!
Method: REST calls to athena.comma.ai which then gets templated out into different home assistant entities.

***Only a single EON is supported. Can be modified and/or duplicated to suit however many you want.***

### Where to put the yaml files.
This as designed as if you are using a split configuration in Home Assistant, but can be adapted to a unified setup. Put the yaml files in your sensors folder. Set the secrets in your secrets.yaml and restart the server. Take care not to modify quotes or hyphens. The jwt doesn't get refreshed automatically, so you'll still have to change this when it resets and then restart the server.

### How to setup the secrets.yaml file
The secrets are: **comma_eon_https_url** and **comma_eon_jwt**

The url secret should be formatted like this. Replace dongle_id with your EON's dongle_id:
`comma_eon_https_url: "https://athena.comma.ai/dongle_id"`

The jwt should be like this. Get it from https://jwt.comma.ai/:
`comma_eon_jwt: "JWT abc123yourjwttokenhereblahblahabc123yourjwttokenhereblahblahabc123yourjwttokenhereblahblahabc123yourjwttokenhereblahblah"`
