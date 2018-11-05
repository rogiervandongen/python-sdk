import json

from marshmallow import Schema, fields, post_load, pre_load

from paynlsdk.api.requestbase import RequestBase
from paynlsdk.api.responsebase import ResponseBase
from paynlsdk.objects import ErrorSchema, Connection, ConnectionSchema, EndUser, EndUserSchema,\
    PaymentDetails, PaymentDetailsSchema, StornoDetails, StornoDetailsSchema,\
    SalesData, SalesDataSchema, StatsDetails, StatsDetailsSchema
from paynlsdk.validators import ParamValidator


class Response(ResponseBase):
    def __init__(self,
                 connection: Connection=None,
                 enduser: EndUser=None,
                 sale_data: SalesData=None,
                 payment_details: PaymentDetails=None,
                 storno_details: StornoDetails=None,
                 stats_details: StatsDetails=None,
                 transaction_id: str=None,
                 *args, **kwargs):
        self.connection = connection
        self.enduser = enduser
        self.sale_data = sale_data
        self.payment_details = payment_details
        self.storno_details = storno_details
        self.stats_details = stats_details
        self.transaction_id = transaction_id
        super().__init__(**kwargs)

    def is_paid(self):
        return self.payment_details.state_name == 'PAID'

    def is_pending(self):
        return self.payment_details.state_name == 'PENDING' or self.payment_details.state_name == 'VERIFY'

    def is_cancelled(self):
        return self.payment_details.state <= 0

    def is_authorized(self):
        return self.payment_details.state == 95

    def is_being_verified(self):
        return self.payment_details.state_name == 'VERIFY'

    def is_refunded(self, allow_partial_refunds: bool = True):
        if self.payment_details.state_name == 'REFUND':
            return True
        elif allow_partial_refunds and self.payment_details.state_name == 'PARTIAL_REFUND':
            return True
        else:
            return False

    def is_partially_refunded(self):
        return self.payment_details.state_name == 'PARTIAL_REFUND'

    def get_id(self):
        return self.transaction_id

    def approve(self):
        raise NotImplementedError("TODO")

    def decline(self):
        raise NotImplementedError("TODO")

    def void(self):
        raise NotImplementedError("TODO")

    def capture(self):
        raise NotImplementedError("TODO")

    def get_amount(self):
        """
        Get transaction amount in EURO
        :return: transaction amount in EURO
        :rtype: float
        """
        return self.payment_details.amount / 100

    def get_paid_amount(self):
        """
        Get paid transaction amount in EURO
        :return: paid transaction amount in EURO
        :rtype: float
        """
        return self.payment_details.paid_amount / 100

    def get_currency_amount(self):
        """
        Get transaction amount in payment currency
        :return: transaction amount in payment currency
        :rtype: float
        """
        return self.payment_details.currency_amount / 100

    def get_paid_currency(self):
        """
        Get currency of transaction
        :return: currency
        :rtype: string
        """
        return self.payment_details.paid_currency

    def get_paid_currency_amount(self):
        """
        Get paid transaction amount in payment currency
        :return: paid transaction amount in payment currency
        :rtype: float
        """
        return self.payment_details.paid_currency_amount / 100

    def get_refunded_amount(self):
        """
        Get refunded transaction amount in EURO
        :return: refunded transaction amount in EURO
        :rtype: float
        """
        # return self.payment_details.refund_amount / 100
        raise NotImplementedError("TODO")

    def get_refunded_currency_amount(self):
        """
        Get refunded transaction amount in payment currency
        :return: refunded transaction amount in payment currency
        :rtype: float
        """
        # return self.payment_details.refund_currency_amount / 100
        raise NotImplementedError("TODO")

    def get_account_holder_name(self):
        """
        Get account holder name for transaction
        :return: transaction account holder name
        :rtype: str
        """
        return self.payment_details.identifier_name

    def get_account_number(self):
        """
        Get account number or masked creditcard number for transaction
        :return: transaction account number
        :rtype: str
        """
        return self.payment_details.identifier_public

    def get_account_hash(self):
        """
        Get account hash for transaction (account number or masked creditcard number)
        :return: transaction account hash
        :rtype: str
        """
        return self.payment_details.identifier_hash

    def get_payment_method_name(self):
        """
        Get payment method name for transaction
        :return: transaction payment method name
        :rtype: str
        """
        return self.payment_details.payment_profile_name

    def get_description(self):
        """
        Get description for transaction
        :return: transaction description
        :rtype: str
        """
        return self.payment_details.description

    def get_extra1(self):
        """
        Get extra1 field for transaction (statsdetails)
        :return: transaction extra1 field value
        :rtype: str
        """
        return self.stats_details.extra1

    def get_extra2(self):
        """
        Get extra2 field for transaction (statsdetails)
        :return: transaction extra2 field value
        :rtype: str
        """
        return self.stats_details.extra2

    def get_extra3(self):
        """
        Get extra3 field for transaction (statsdetails)
        :return: transaction extra3 field value
        :rtype: str
        """
        return self.stats_details.extra3

    def __repr__(self):
        return str(self.__dict__)


class ResponseSchema(Schema):
    request = fields.Nested(ErrorSchema, required=True)
    connection = fields.Nested(ConnectionSchema, required=True)
    enduser = fields.Nested(EndUserSchema, required=True)
    sale_data = fields.Nested(SalesDataSchema, required=False, load_from='saleData')
    payment_details = fields.Nested(PaymentDetailsSchema, required=True, load_from='paymentDetails')
    storno_details = fields.Nested(StornoDetailsSchema, required=False, load_from='stornoDetails')
    stats_details = fields.Nested(StatsDetailsSchema, required=False, load_from='statsDetails')

    @pre_load
    def pre_processor(self, data):
        # No-op yet (see complex subtypes)
        return data

    @post_load
    def create_response(self, data):
        return Response(**data)


class Request(RequestBase):
    def __init__(self, transaction_id: str=None, entrance_code: str=None):
        self.transaction_id = transaction_id
        self.entrance_code = entrance_code
        super().__init__()

    def requires_api_token(self):
        return True

    def requires_service_id(self):
        return False

    def get_version(self):
        return 12

    def get_controller(self):
        return 'Transaction'

    def get_method(self):
        return 'info'

    def get_query_string(self):
        return ''

    def get_parameters(self):
        # Validation
        ParamValidator.assert_not_empty(self.transaction_id, 'transaction_id')
        # Get default api parameters
        dict = self.get_std_parameters()
        # Add own parameters
        dict['transactionId'] = self.transaction_id
        if ParamValidator.not_empty(self.entrance_code):
            dict['entranceCode'] = self.entrance_code
        return dict

    @RequestBase.raw_response.setter
    def raw_response(self, raw_response):
        self._raw_response = raw_response
        dict = json.loads(self.raw_response)
        schema = ResponseSchema(partial=True)
        self._response, errors = schema.load(dict)
        #  Map transaction ID on response
        self.response.transaction_id = self.transaction_id
        self.handle_schema_errors(errors)

    @property
    def response(self) -> Response:
        """
        Return the API :class:`Response` for the validation request

        :return: The API response
        :rtype: paynlsdk.api.transaction.info.Response
        """
        return self._response

    @response.setter
    def response(self, response: Response):
        # print('{}::respone.setter'.format(self.__module__ + '.' + self.__class__.__qualname__))
        self._response = response

