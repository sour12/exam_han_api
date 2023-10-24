import sys
import requests
import json
from datetime import datetime

# my info
api_key = sys.argv[1]
secret_key = sys.argv[2]
cano = sys.argv[3]
acnt_prdt_cd = sys.argv[4]

base_url = 'https://openapi.koreainvestment.com:9443'

token_json = "token.json"

# 토큰 저장하기
def save_token(res):
    with open(token_json, 'w') as file:
        json.dump(res, file)

# (만료되지 않은) 토큰 불러오기
def read_token():
    try:
        with open(token_json, 'r') as file:
            res = json.load(file)
    except FileNotFoundError:
        return None
    exp_date = res.get("access_token_token_expired")
    now_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    if (exp_date < now_date):
        return None
    return res.get("access_token")

def get_token():
    token = read_token()
    if token is None:
        # 토큰 발급 받기
        headers = {
            "content-type":"application/json"
            }
        body = {
            "grant_type":"client_credentials",
            "appkey":api_key, 
            "appsecret":secret_key,
            }
        url = base_url + '/oauth2/tokenP'
        res = requests.post(url, headers=headers, data=json.dumps(body)).json()
        save_token(res)
        token = res.get("access_token")
    return token

def get_cur_price(ticker):
    headers = {
        "content-type":"application/json",
        "appkey":api_key, 
        "appsecret":secret_key,
        "authorization":f"Bearer {access_token}",
        "tr_id":"FHKST01010100",
        }
    params = {
        "fid_cond_mrkt_div_code":"J",
        "fid_input_iscd": ticker
        }
    url = base_url + '/uapi/domestic-stock/v1/quotations/inquire-price'
    res = requests.get(url, headers=headers, params=params).json()['output']
    return res.get("stck_prpr")

# 보유 현금 조회
def get_my_cash():
    headers = {
        "content-type":"application/json",
        "appkey":api_key,
        "appsecret":secret_key, 
        "authorization":f"Bearer {access_token}",
        "tr_id":"TTTC8908R", # 실전:TTTC8434R / 모의:VTTC8434R
        "custtype":"P",
        }
    params = {
        "CANO": cano,                   
        "ACNT_PRDT_CD": acnt_prdt_cd,
        "PDNO": "005930",
        "ORD_UNPR": "00054500",
        "ORD_DVSN": "00",
        "CMA_EVLU_AMT_ICLD_YN": "N",
        "OVRS_ICLD_YN": "N",
    }
    url = base_url + "/uapi/domestic-stock/v1/trading/inquire-psbl-order"
    res = requests.get(url, headers=headers, params=params).json()['output']
    return res.get("ord_psbl_cash")


# 토큰 가져오기
access_token = get_token()

# 나의 잔고 가져오기
my_cash = get_my_cash()
print("나의 계좌잔고 : {} 원".format(my_cash))

# 현재가 가저오기
samsung = get_cur_price('005930')
kakao = get_cur_price('035720')
print("삼성   현재가 : {}".format(samsung))
print("카카오 현재가 : {}".format(kakao))
