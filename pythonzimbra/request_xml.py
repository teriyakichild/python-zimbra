""" Request handling and generation (XML version) """

import xml.dom.minidom
from pythonzimbra.exceptions.request import RequestHeaderContextException, \
    NoXMLNSGiven
from pythonzimbra.tools import xmlserializer
from request import Request


class RequestXml(Request):
    """ Zimbra SOAP request generation and handling
    """

    request_type = "xml"

    # The XML request we're building up
    request_doc = None

    # Header context
    context_node = None

    # Body node
    body_node = None

    # Are we doing batch requests?
    batch_request = False

    # If so, keep the current request id
    batch_request_id = None

    def __init__(self):

        """ Create a new request.
        """

        self.request_doc = xml.dom.minidom.Document()
        root_node = self.request_doc.createElementNS(
            'http://www.w3.org/2003/05/soap-envelope',
            'soap:Envelope'
        )
        root_node.setAttribute(
            "xmlns:soap",
            "http://www.w3.org/2003/05/soap-envelope"
        )

        header_node = self.request_doc.createElement('soap:Header')

        self.context_node = self.request_doc.createElement('context')
        self.context_node.setAttribute('xmlns', 'urn:zimbra')

        format_node = self.request_doc.createElement('format')
        format_node.setAttribute('type', 'xml')

        self.context_node.appendChild(format_node)

        header_node.appendChild(self.context_node)

        root_node.appendChild(header_node)

        self.body_node = self.request_doc.createElement('soap:Body')

        root_node.appendChild(self.body_node)

        self.request_doc.appendChild(root_node)

    def set_context_params(self, params):

        # Call parent method

        super(RequestXml, self).set_context_params(params)

        for key, value in params.iteritems():

            tmp_node = self.request_doc.createElement(key)

            xmlserializer.dict_to_dom(tmp_node, value)

            self.context_node.appendChild(tmp_node)

    def _create_batch_node(self, namespace, onerror):

        self.batch_node = self.request_doc.createElement("BatchRequest")
        self.batch_node.setAttribute("xmlns", namespace)
        self.batch_node.setAttribute("onerror", onerror)

        self.body_node.appendChild(self.batch_node)

    def add_request(self, request_name, request_dict, namespace=None):

        """ Add a request.

        This adds a request to the body or to the batchrequest-node if batch
        requesting is enabled.

        :param request_name: The name of the request
        :param request_dict: The request parameters as a serializable dict.
        Check out xmlserializer documentation about this.
        :param namespace: The XML namespace of the request. (Please don't use
        the request_dict to specify it, use this parameter)
        :returns: The current request id (if batch processing) or None
        :rtype: int or None
        """

        request_node = self.request_doc.createElement(request_name)
        xmlserializer.dict_to_dom(request_node, request_dict)

        if not self.batch_request:

            if not namespace:
                raise NoXMLNSGiven(
                    'You have added a request without specifying a XML '
                    'namespace, but you are not in batch request mode.'
                )

            request_node.setAttribute('xmlns', namespace)

            self.body_node.appendChild(request_node)

            return None

        request_id = self.batch_request_id

        request_node.setAttribute('requestId', str(request_id))

        self.batch_node.appendChild(request_node)

        self.batch_request_id += 1

        return request_id

    def get_request(self):

        return self.request_doc.toxml()