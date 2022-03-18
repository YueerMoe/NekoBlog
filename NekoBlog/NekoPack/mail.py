import base64
import hmac
import json
from urllib.parse import quote_plus
import uuid
from urllib.parse import urlencode
import requests
import datetime


def percent_encode(enc_data: str):
    res = quote_plus(enc_data.encode('utf8'), '')
    res = res.replace('+', '%20')
    res = res.replace('*', '%2A')
    res = res.replace('%7E', '~')
    return res


with open("NekoBlog/config/mail.html", "r", encoding="utf-8") as f:
    mail = f.read()
with open("NekoBlog/config/mail.json", "r", encoding="utf-8") as f:
    cfg = json.loads(f.read())


def get_signature(sign_data: dict, method: str):
    sorted_data = sorted(sign_data.items(), key=lambda x: x[0])
    can_string = ''
    for k, v in sorted_data:
        can_string += '&' + percent_encode(k) + '=' + percent_encode(v)

    string_to_sign = method + '&%2F&' + percent_encode(can_string[1:])
    h = hmac.new(bytes(cfg['key'], encoding="utf8"), bytes(string_to_sign, encoding="utf8"),
                 digestmod='sha1')
    return base64.b64encode(h.digest())


def request_api(req_data: dict):
    req_data['ali']['Signature'] = get_signature(req_data, 'POST')
    data = urlencode(req_data)
    header = {"content-type": "application/x-www-form-urlencoded"}
    return requests.post('https://dm.aliyuncs.com/', data=data, headers=header).text


def send_mail(html_body: str, to_address: str, from_name: str, subject: str):
    mail_data = {
        'AccessKeyId': cfg['ali']['AccessKeyId'],
        'AccountName': cfg['ali']['AccountName'],
        'Action': 'SingleSendMail',
        'AddressType': '1',
        'Format': 'JSON',
        'HtmlBody': html_body,
        'FromAlias': from_name,
        'RegionId': 'cn-hangzhou',
        'ReplyToAddress': 'false',
        'SignatureMethod': 'HMAC-SHA1',
        'SignatureNonce': f'{uuid.uuid4()}',
        'SignatureVersion': '1.0',
        'Subject': subject,
        'Timestamp': f'{datetime.datetime.utcnow().isoformat()[:-7]}' + 'Z',
        'ToAddress': to_address,
        'Version': '2015-11-23'
    }
    return request_api(mail_data)
