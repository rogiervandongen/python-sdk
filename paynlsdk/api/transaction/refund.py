import json

from marshmallow import Schema, fields, post_load, pre_load

from paynlsdk.api.requestbase import RequestBase
from paynlsdk.api.responsebase import ResponseBase
from paynlsdk.objects import ErrorSchema, RefundFailInfoSchema, RefundSuccessInfoSchema
from paynlsdk.validators import ParamValidator


class Response(ResponseBase):
    """
    Response object for the Transaction::refund API

    :param dict refunded_transactions: refunded transactions information
    :param dict failed_transactions: failed refunds information
    :param int amount_refunded: amount that was refunded
    :param str description: refunds description
    :param str refund_id: Refund ID. Please note this is NOT guaranteed. Value is only returned for IBAN based payments
    """
    def __init__(self,
                 refunded_transactions: dict={},
                 failed_transactions: dict={},
                 amount_refunded: int=None,
                 description: str=None,
                 refund_id: str=None,
                 *args, **kwargs):
        self.refunded_transactions = refunded_transactions
        self.failed_transactions = failed_transactions
        self.amount_refunded = amount_refunded
        self.description = description
        self.refund_id = refund_id
        super().__init__(**kwargs)

    def __repr__(self):
        return str(self.__dict__)

    def get_refunded_amount(self):
        """
        Get refunded amount
        :return: refunded amount
        :rtype: float
        """
        return self.response.amount_refunded / 100


class ResponseSchema(Schema):
    request = fields.Nested(ErrorSchema)
    refunded_transactions = fields.List(fields.Nested(RefundSuccessInfoSchema), allow_none=True, load_from='refundedTransactions')
    failed_transactions = fields.List(fields.Nested(RefundFailInfoSchema), allow_none=True, load_from='failedTransactions')
    amount_refunded = fields.Integer(load_from='amountRefunded', allow_none=True)
    description = fields.String(allow_none=True)
    refund_id = fields.String(load_from='refundId', allow_none=True, required=False)

    @pre_load
    def pre_processor(self, data):
        # Again, the API returns an empty string where it SHOULD return null or an empty list.
        if 'refundedTransactions' in data and ParamValidator.is_empty(data['refundedTransactions']):
            data['refundedTransactions'] = []
        elif 'refundedTransactions' in data and ParamValidator.not_empty(data['refundedTransactions']):
            #  v2.x has NO fields.Dict implementation like fields.List, so we'll have to handle this ourselves
            list = []
            for item in data['refundedTransactions']:
                list.append(item)
            data['refundedTransactions'] = list
        if 'failedTransactions' in data and ParamValidator.is_empty(data['failedTransactions']):
            data['failedTransactions'] = []
        elif 'failedTransactions' in data and ParamValidator.not_empty(data['failedTransactions']):
            #  v2.x has NO fields.Dict implementation like fields.List, so we'll have to handle this ourselves
            list = []
            for item in data['failedTransactions']:
                list.append(item)
            data['failedTransactions'] = list
        return data

    @post_load
    def create_response(self, data):
        #  This is NASTY. Perform conversion due to fields.Dict NOT taking nesteds in 2.x (aka undo preprocessing).
        #  This should be fixed in 3.x but that's a pre-release
        if 'refunded_transactions' in data:
            rs = {}
            for item in data['refunded_transactions']:
                print(item)
                rs[item.order_id] = item
            data['refunded_transactions'] = rs
        #  This is NASTY. Perform conversion due to fields.Dict NOT taking nesteds in 2.x (aka undo preprocessing).
        #  This should be fixed in 3.x but that's a pre-release
        if 'failed_transactions' in data:
            rs = {}
            for item in data['failed_transactions']:
                rs[item.order_id] = item
            data['failed_transactions'] = rs
        return Response(**data)


class Request(RequestBase):
    """
    Request object for the Refund::transaction API

    :param str transaction_id: Refund ID
    :param int amount: refund amount
    :param str description: refunds description
    :param str process_date: process date
    """
    def __init__(self,
                 transaction_id: str=None,
                 amount: int=None,
                 description: str=None,
                 process_date: str=None,
                 ):
        self.transaction_id = transaction_id
        self.amount = amount
        self.description = description
        self.process_date = process_date
        super().__init__()

    def requires_api_token(self):
        return True

    def requires_service_id(self):
        return False

    def get_version(self):
        return 13

    def get_controller(self):
        return 'Transaction'

    def get_method(self):
        return 'refund'

    def get_query_string(self):
        return ''

    def get_parameters(self):
        # Validation
        ParamValidator.assert_not_empty(self.transaction_id, 'transaction_id')
        # Get default api parameters
        rs = self.get_std_parameters()
        # Add own parameters
        rs['transactionId'] = self.transaction_id
        if ParamValidator.not_empty(self.amount):
            rs['amount'] = self.amount
        if ParamValidator.not_empty(self.description):
            rs['description'] = self.description
        if ParamValidator.not_empty(self.process_date):
            rs['processDate'] = self.process_date
        return rs

    @RequestBase.raw_response.setter
    def raw_response(self, raw_response):
        self._raw_response = raw_response
        # Do error checking.
        rs = json.loads(self.raw_response)
        schema = ResponseSchema(partial=True)
        response, errors = schema.load(rs)
        self.handle_schema_errors(errors)
        self._response = response

    @property
    def response(self) -> Response:
        """
        Return the API :class:`Response` for the validation request

        :return: The API response
        :rtype: paynlsdk.api.refund.transaction.Response
        """
        return self._response

    @response.setter
    def response(self, response: Response):
        # print('{}::respone.setter'.format(self.__module__ + '.' + self.__class__.__qualname__))
        self._response = response


