import requests
import xml.etree.ElementTree as ET

country_codes = [
    "US",  # united states
    "IN",  # india
    "CN",  # china
    "DK",  # denmmak
]

namespaces = {
    "soap": "http://schemas.xmlsoap.org/soap/envelope/",
    "m": "http://www.oorsprong.org/websamples.countryinfo",
}

# SOAP request URL
url = "http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso"


for country_code in country_codes:
    # structured XML
    payload = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
                <soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
                    <soap:Body>
                        <CountryIntPhoneCode xmlns=\"http://www.oorsprong.org/websamples.countryinfo\">
                            <sCountryISOCode>{country_code}</sCountryISOCode>
                        </CountryIntPhoneCode>
                    </soap:Body>
                </soap:Envelope>"""
    # headers
    headers = {"Content-Type": "text/xml; charset=utf-8"}
    # POST request
    response = requests.post(url, headers=headers, data=payload)

    # prints the response
    # print(response.text)
    # print(response)

    root = ET.fromstring(text=response.text)
    result_element = root.find(".//m:CountryIntPhoneCodeResult", namespaces).text
    print(f"Country Code for {country_code} is {result_element}")
