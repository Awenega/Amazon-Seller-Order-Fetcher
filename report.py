import time, json, requests, zlib, re, xmltodict
from spApi import get_headers
import xml.etree.ElementTree as elementTree

MARKETPLACEID_IT = "APJ6JRA9NG5V4"     
MARKETPLACEID_ES = "A1PA6795UKMFR9"     
MARKETPLACEID_DE = "A1RKKUPIHCS9HS"
HOST = "sellingpartnerapi-eu.amazon.com"

def remove_xml_namespaces(data):
    pattern = r'xmlns(:ns2)?="[^"]+"|(ns2:)|(xml:)'
    replacement = ""
    if not isinstance(data, str):
        pattern = pattern.encode()
        replacement = replacement.encode()
    return re.sub(pattern, replacement, data)

def mws_xml_to_dict(data):
    data = remove_xml_namespaces(data)
    data = data.replace('\u2019','')
    xmldict = xmltodict.parse(data, encoding="iso-8859-1", dict_constructor=dict, force_cdata=False)
    finaldict = xmldict.get(list(xmldict.keys())[0], xmldict)
    return finaldict

def isXml(value):
    try:
        elementTree.fromstring(value)
    except elementTree.ParseError:
        return False
    return True

def create_body(startDate, endDate, marketplaces):
    body = {}
    body['dataStartTime'] = startDate
    body['dataEndTime'] = endDate
    body['marketplaceIds'] = marketplaces
    body['reportType'] = "GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
    return json.dumps(body)

def check_if_error(response):
    if "errors" in response:
        print(f"ERROR: {response}")
        return True
    else:
        return False

def getReportId(startDate, endDate):
    print(f"Request order report from: {startDate} to: {endDate}")
    
    method = "POST"
    path = f"/reports/2021-06-30/reports"
    body = create_body(startDate, endDate, [MARKETPLACEID_IT, MARKETPLACEID_ES, MARKETPLACEID_DE])
    request_parameters, canonical_uri, request_url = body, path, "https://" + HOST + path
    headers = get_headers(method,canonical_uri,'')
    response = requests.post(url=request_url,headers=headers, data=request_parameters).json()
    
    return response['reportId'] if not check_if_error(response) else response

def getReportDocumentId(reportId):
    method = "GET"
    path = f"/reports/2021-06-30/reports/{reportId}"
    canonical_uri = path
    request_url = "https://" + HOST + path
    headers = get_headers(method,canonical_uri,'')

    while True:
        response = requests.get(url=request_url,headers=headers).json()
        report_status = response['processingStatus']
        if report_status == 'DONE':
            print("Report is ready!")
            print(response)
            return response['reportDocumentId'] if not check_if_error(response) else response
        elif report_status == 'IN_PROGRESS':
            print("Report is in progress. Waiting...")
            time.sleep(5)
        elif report_status == 'IN_QUEUE':
            print("Report is in queue. Waiting...")
            time.sleep(10)
        else:
            print("Report generation failed!")
            break
    
def getReportDocumentURL(reportDocumentId):
    method = "GET"
    path = f"/reports/2021-06-30/documents/{reportDocumentId}"
    canonical_uri = path
    request_url = "https://" + HOST + path
    headers = get_headers(method,canonical_uri,'')
    response = requests.get(url=request_url,headers=headers).json()
    return response
    
def getDocument(response):
    url = response['url']
    contentDocument = requests.get(url).content
    document = bytearray(contentDocument)

    if "compressionAlgorithm" in response:
        document = zlib.decompress(document, 15 + 32)
    decoded_document = document.decode('iso-8859-1')

    if isXml(decoded_document):
        document = mws_xml_to_dict(remove_xml_namespaces(decoded_document))
    return document
    