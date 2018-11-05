import json

from marshmallow import Schema, fields, pre_load, post_load

from paynlsdk.api.requestbase import RequestBase
from paynlsdk.api.responsebase import ResponseBase
from paynlsdk.objects import ErrorSchema, Merchant, MerchantSchema, Service, ServiceSchema,\
    PaymentOption, PaymentOptionSchema, CountryOption, CountryOptionSchema
from paynlsdk.validators import ParamValidator


class Response(ResponseBase):
    def __init__(self,
                 merchant: Merchant=None,
                 service: Service=None,
                 settings: dict=None,
                 payment_options: dict=None,
                 country_options: dict=None,
                 *args, **kwargs):
        self.merchant = merchant
        self.service = service
        self.settings = settings
        self.payment_options = payment_options
        self.country_options = country_options
        super().__init__(**kwargs)

    def __repr__(self):
        return self.__dict__.__str__()


class ResponseSchema(Schema):
    request = fields.Nested(ErrorSchema)
    merchant = fields.Nested(MerchantSchema, required=False)
    service = fields.Nested(ServiceSchema, required=False)
    settings = fields.Dict(required=False, allow_none=True)
    payment_options = fields.List(fields.Nested(PaymentOptionSchema), required=False, load_from='paymentOptions')
    country_options = fields.List(fields.Nested(CountryOptionSchema), required=False, load_from='countryOptionList')
    #payment_profiles = fields.List(fields.Nested(PaymentOptionSchema), required=False, load_from='paymentProfiles')

    @pre_load
    def pre_processor(self, data):
        if ParamValidator.is_empty(data['paymentOptions']):
            del data['paymentOptions']
        elif 'paymentOptions' in data and ParamValidator.not_empty(data['paymentOptions']):
            #  v2.x has NO fields.Dict implementation like fields.List, so we'll have to handle this ourselves
            list = []
            for i, item in data['paymentOptions'].items():
                list.append(item)
            data['paymentOptions'] = list
        if ParamValidator.is_empty(data['countryOptionList']):
            del data['countryOptionList']
        elif 'countryOptionList' in data and ParamValidator.not_empty(data['countryOptionList']):
            #  v2.x has NO fields.Dict implementation like fields.List, so we'll have to handle this ourselves
            list = []
            for i, item in data['countryOptionList'].items():
                list.append(item)
            data['countryOptionList'] = list
        return data

    @post_load
    def create_response(self, data):
        #  This is NASTY. Perform conversion due to fields.Dict NOT taking nesteds in 2.x (aka undo preprocessing).
        #  This should be fixed in 3.x but that's a pre-release
        if 'payment_options' in data:
            dict = {}
            for item in data['payment_options']:
                dict[item.id] = item
            data['payment_options'] = dict
        if 'country_options' in data:
            dict = {}
            for item in data['country_options']:
                dict[item.id] = item
            data['country_options'] = dict
        return Response(**data)


class Request(RequestBase):
    def __init__(self, payment_method_id: int=None):
        self.payment_method_id = payment_method_id
        super().__init__()

    def requires_api_token(self):
        return True

    def requires_service_id(self):
        return True

    def get_version(self):
        return 12

    def get_controller(self):
        return 'Transaction'

    def get_method(self):
        return 'getServicePaymentOptions'

    def get_query_string(self):
        return ''

    def get_parameters(self):
        # Get default api parameters
        dict = self.get_std_parameters()
        # Add own parameters
        if ParamValidator.not_empty(self.payment_method_id):
            dict['paymentMethodId'] = self.payment_method_id
        return dict

    @RequestBase.raw_response.setter
    def raw_response(self, raw_response):
        self._raw_response = raw_response
        # Do error checking.
        dict = json.loads(self.raw_response)
        schema = ResponseSchema(partial=True)
        self._response, errors = schema.load(dict)
        self.handle_schema_errors(errors)

    @property
    def response(self) -> Response:
        """
        Return the API :class:`Response` for the validation request

        :return: The API response
        :rtype: paynlsdk.api.transaction.getservicepaymentoptions.Response
        """
        return self._response

    @response.setter
    def response(self, response: Response):
        # print('{}::respone.setter'.format(self.__module__ + '.' + self.__class__.__qualname__))
        self._response = response

