# Integrations


## HubSpot

[API Docs](https://developers.hubspot.com/docs/api/overview)
[Python SDK](https://github.com/HubSpot/hubspot-api-python)

`pip install hubspot-api-client`


``` py
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate
from hubspot.crm.contacts.exceptions import ApiException

api_client = HubSpot(access_token='your_access_token')

# or set your access token later
# api_client = HubSpot()
# api_client.access_token = 'your_access_token'

try:
    simple_public_object_input_for_create = SimplePublicObjectInputForCreate(
        properties={"email": "email@example.com"}
    )
    api_response = api_client.crm.contacts.basic_api.create(
        simple_public_object_input_for_create=simple_public_object_input_for_create
    )
except ApiException as e:
    print("Exception when creating contact: %s\n" % e)
```

## Mailchimp

[API Docs](https://mailchimp.com/developer/marketing/)
[Python SDK](https://github.com/mailchimp/mailchimp-marketing-python)


``` py
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError

try:
  client = MailchimpMarketing.Client()
  client.set_config({
    "api_key": "YOUR_API_KEY",
    "server": "YOUR_SERVER_PREFIX"
  })

  response = client.batches.start({"operations": [{"method": "POST", "path": "/lists"}]})
  print(response)
except ApiClientError as error:
  print("Error: {}".format(error.text))
```

## Salesforce

[API Docs](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm)
[Python SDK](https://github.com/simple-salesforce/simple-salesforce)

`pip install simple-salesforce`

Supported integrations to third-party systems such as Mailchimp for both internal use & for customer-facing data products


``` py
from simple_salesforce import Salesforce
import requests

session = requests.Session()
# manipulate the session instance (optional)
sf = Salesforce(
   username='user@example.com',
   password='password',
   organizationId='OrgId',
   session=session
)

sf.Contact.create({'LastName':'Smith','Email':'example@example.com'})
sf.Contact.delete('003e0000003GuNXAA0')
```

## Google Analytics

[API Docs](https://developers.google.com/analytics/devguides/reporting/data/v1)
[Python SDK](https://github.com/googleapis/google-api-python-client)

`pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`

## Google Sheets

[API Docs](https://developers.google.com/sheets/api/guides/concepts)
[Python SDK](https://github.com/burnash/gspread)

`pip install gspread`