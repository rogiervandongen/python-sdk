# python-sdk

- [Installation](#installation)
- [Requirements](#internal-api-implementation)
- [Internal API implementation](#requirements)
- [Quick start and examples](#quick-start-and-examples)
- [Error handling](#error-handling)

---

### Installation

This SDK can be installed through pip.

Pip is the package manager for Python.

For more information on how to use/install pip, please visit: [https://pypi.org/project/pip/](https://pypi.org/project/pip/)

To install the Pay.nl Python sdk into your project, simply

	$ pip install paynlsdk

### Requirements

The Pay.nl Python SDK works on Python 3.7 and is dependent on the requests package and the marshmallow package (v2.x only)
When installing through pip these dependencies will automatically be detected and installed

### Internal API implementation
Not all function arguments will be completely described for every case.
When using the utility/quick start classes all parameters are available, so take a look at the method arguments there for more options.
They are basically self explanatory

Every API implementation has it's own Request and Response class, which can be found in the various *paynlsdk.api.xxx.yyy* modules.
Every one of the modules contain at least a Request and a Response class.
For example, the Transaction.info API can be located in the *paynlsdk.api.transation.info* module and will contain both a
*paynlsdk.api.transaction.info.Request* and a *paynlsdk.api.transaction.info.Response* class 
Usually these modules will also contain a specific (marshmallow) Schema implementation that defines the response mapping from JSON. 

For every call, a response object will be returned.
Using the *print(result)* statement, or by investigating the *paynlsdk.objects* module, you can find out what attributes are available.
Every result will contain a *request* object, which essentially gives insight on the success or failure of the request.
This object is also used to throw a *paynlsk.exceptions.ErrorException* in case the request failed.
The rest of the *response* object will contain the information as returned by the PAYL API

Again, refer to the *paynlsdk.objects* module to investigate the various objects contained in the response.
The exact contents of the response objects itself are defined in all the *paynlsdk.api.xxx.yyy.Response* classes



### Quick start and examples
Do note this quick start only makes use of the quick-call utility methods.
If you're more familiar with Python, you *could* use the full API request/response implementations in the paynlsdk.api namespace

Set configuration (this is a MUST and should always be done before doing anything with the SDK)
```
from paynlsdk.api.client import APIAuthentication
APIAuthentication.service_id = 'SL-xxxx-xxxx'
APIAuthentication.api_token = '<yourtokenhere>'
```

Turn on debugging output for the API Client
Note: this uses "print"
```
from paynlsdk.api.client import APIClient
APIClient.print_debug = True
```

Get banks (ideal banks only)
```
from paynlsdk.client.transaction import Transaction
result = Transaction.get_banks()
print(result)
```

Get service for a payment method id 
```
from paynlsdk.client.transaction import Transaction
result = Transaction.get_service(10)
print(result)
```

Retrieving transaction info 
```
from paynlsdk.client.transaction import Transaction
result = Transaction.info(<yourtransactionidhere>)
print(result)
```

Retrieving transaction status 
```
from paynlsdk.client.transaction import Transaction
result = Transaction.status(<yourtransactionidhere>)
print(result)
```

Refunding (part of) a transaction.
```
from paynlsdk.client.refund import Refund
result = Refund.transaction(<transactionidhere>, <amountincents>, <description>)
print(result)
```

Retrieving refund info
Note: refund ids come in the form of 'RF-xxxx-xxxx'
```
from paynlsdk.client.refund import Refund
result = Refund.info('RF-xxxx-xxxx')
print(result)
```

Starting a transaction
```
from paynlsdk.client.transaction import Transaction
saledata = SalesData()
saledata.invoice_date = datetime(2018,10,30)
saledata.delivery_date = datetime(2018,11,1)
saledata.order_data.append(OrderData(product_id='XYZ', product_type='ARTICLE', description='XYZ description', price=900, quantity=1, vat_code='H', vat_percentage=21))

enduser = TransactionEndUser(language='nl', initials='A', last_name='Jansen', gender='m', dob=datetime(1970,1,2),
                             phone_number='0612345678', email_address='someone@somewhere.com', iban='<ibannumber>',
                             address=Address(street_name='Street', street_number='1', zip_code='1234AB', city='Rotterdam', country_code='NL', country_name='Nederland'),
                             invoice_address=Address(street_name='Street', street_number='1', zip_code='1234AB', city='Rotterdam', country_code='NL', country_name='Nederland'),
                             company=Company(name='Wizard Inc', coc_number='12345678', vat_number='NL123456789B01', country_code='NL')
                             )

sinfo1 = {'amount': 250, 'ip_address': '192.168.0.1', 'finish_url': 'https://somedomain.com', 'payment_option_id': 436,
          'transaction': TransactionData(description='order 9999 at Wizard Inc', order_number='9999', order_exchange_url='https://somedomain.nl/exchange.php'),
          'stats_data': TransactionStartStatsData(extra1='IDX 9999'),
          'end_user': enduser,
          'sale_data': saledata,
          'test_mode': True
          }

result = Transaction.start(**sinfo1)
print(result)
```

### Error handling
You should always wrap your calls in an exception handler.
The SDK only contains two internal exceptions:
- paynlsdk.exceptions.ErrorException

  If, for any reason, an error arises in the communication or internally in the API, this exception will be thrown
- paynlsdk.exceptions.SchemaException

  If, for any reason, the schema mapping (using marshmallow), shall fail , this exception is thrown

Note: it can always happen that any other standard exceptions are thrown.
These are most likely to happen outside of the SDK but should also be handled.
