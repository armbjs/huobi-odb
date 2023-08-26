import redis
import datetime
import pytz
import time
from datetime import datetime
import json
import requests
import warnings
import concurrent.futures
import os

warnings.filterwarnings("ignore", category=DeprecationWarning)

def format_timestamp_in_ms(timestamp_in_ms):
    local_timezone = pytz.timezone("Asia/Seoul")
    timezone_aware_dt = datetime.fromtimestamp(timestamp_in_ms / 1000, tz=local_timezone)
    datetime_str = timezone_aware_dt.strftime('%Y-%m-%d_%H:%M:%S_%f%z')
    return datetime_str

def format_timestamp_in_s(timestamp_in_s):
    local_timezone = pytz.timezone("Asia/Seoul")
    timezone_aware_dt = datetime.fromtimestamp(timestamp_in_s, tz=local_timezone)
    datetime_str = timezone_aware_dt.strftime('%Y-%m-%d_%H:%M:%S_%f%z')
    return datetime_str

def get_huobi_symbols(key):
    # huobi_spot_symbol_url = "https://api.huobi.pro/v1/common/symbols"
    # huobi_spot_symbol_data = requests.get(huobi_spot_symbol_url).json()['data']
    # huobi_spot_symbols_list = []
    # for i in huobi_spot_symbol_data:
    #     currency = [i['base-currency'], i['quote-currency']]
    #     huobi_spot_symbols_list.append(currency) #\
    value = my_redis.hget('TEST:GET_CURRENCY_LIST:HUOBI', f'HUOBI-{key}')
    value_str = value.decode('utf-8')
    value_list = json.loads(value_str)
    return value_list

def process_huobi_orderbook(currency_pair):

    global count
    global count_all
    global count_all_time_elapsed
    count_all_time_elapsed = count_all_time - count_time

    order_currency, payment_currency = currency_pair

    try:
        count += 1
        huobi_orderbook_url = f"https://api.huobi.pro/market/depth?symbol={order_currency}{payment_currency}&type=step0"
        huobi_orderbook_url_re = requests.get(huobi_orderbook_url).json()

        huobi_orderbook_url_tick = huobi_orderbook_url_re['tick']
        huobi_orderbook_url_ask = huobi_orderbook_url_tick['asks']
        huobi_orderbook_url_bid = huobi_orderbook_url_tick['bids']
        huobi_orderbook_url_local_ts = time.time()
        huobi_orderbook_url_local_at = format_timestamp_in_s(huobi_orderbook_url_local_ts)
        huobi_orderbook_url_ts = huobi_orderbook_url_tick['ts']
        huobi_orderbook_url_ts_at = format_timestamp_in_ms(huobi_orderbook_url_ts)

        huobi_orderbook_url_ask_dict = {}
        huobi_orderbook_url_bid_dict = {}
        for i in huobi_orderbook_url_ask:
            huobi_orderbook_url_ask_dict[str(i[0])] = {"price": str(i[0]), "quantity": i[1], "bid_or_ask": "ask"}
        for i in huobi_orderbook_url_bid:
            huobi_orderbook_url_bid_dict[str(i[0])] = {"price": str(i[0]), "quantity": i[1], "bid_or_ask": "bid"}

        my_redis.set(f"TEST:ORDERBOOK:HUOBI_SPOT:{order_currency.upper()}_{payment_currency.upper()}_ASK", json.dumps(huobi_orderbook_url_ask_dict))
        my_redis.set(f"TEST:ORDERBOOK:HUOBI_SPOT:{order_currency.upper()}_{payment_currency.upper()}_BID", json.dumps(huobi_orderbook_url_bid_dict))
        my_redis.set(f"TEST:ORDERBOOK:HUOBI_SPOT:{order_currency.upper()}_{payment_currency.upper()}_LOCAL_TIMESTAMP_IN_MS", huobi_orderbook_url_local_ts)
        my_redis.set(f"TEST:ORDERBOOK:HUOBI_SPOT:{order_currency.upper()}_{payment_currency.upper()}_LOCAL_UPDATED_AT", huobi_orderbook_url_local_at)
        my_redis.set(f"TEST:ORDERBOOK:HUOBI_SPOT:{order_currency.upper()}_{payment_currency.upper()}_TIMESTAMP_IN_MS", huobi_orderbook_url_ts)
        my_redis.set(f"TEST:ORDERBOOK:HUOBI_SPOT:{order_currency.upper()}_{payment_currency.upper()}_UPDATED_AT", huobi_orderbook_url_ts_at)

        count_time_finish = time.time()
        count_time_elapsed = count_time_finish - count_time
        count_doing_time = count_time_elapsed / count
        print(f"한바퀴 : {count_all}회({round(count_all_time_elapsed ,3)}초)  |  종목 당 : {count}회({round(count_doing_time, 3)}초)  |  전체 : {round(count_time_elapsed, 3)}초")

    except Exception as e:
        if str(e) == "'tick'":
            pass
        else:
            print(f"에러 코드: {type(e).__name__}, 메시지: {str(e)}")
            time.sleep(62)


if __name__ == "__main__" :

    huobi_key = os.getenv("key", "default_value")

    redis_username = 'armbjs'
    redis_password = "xkqfhf12"
    redis_ssl_type = True
    redis_host_url = 'vultr-prod-3a00cfaa-7dc1-4fed-af5b-19dd1a19abf2-vultr-prod-cd4a.vultrdb.com'
    redis_port_number = '16752' 
    redis_db_number = '0' 
    redis_ssl_ca_path = ''
    redis_ssl_ca_data = """-----BEGIN CERTIFICATE-----
    MIIEQTCCAqmgAwIBAgIUPBb5Gq1hSw0AFMU+nPTXOUOe3cwwDQYJKoZIhvcNAQEM
    BQAwOjE4MDYGA1UEAwwvMDFiNjNkODgtYjBhNS00ZmM2LWFlMzgtYTczMmU2YjBj
    NjZjIFByb2plY3QgQ0EwHhcNMjMwMzExMTQxMjA5WhcNMzMwMzA4MTQxMjA5WjA6
    MTgwNgYDVQQDDC8wMWI2M2Q4OC1iMGE1LTRmYzYtYWUzOC1hNzMyZTZiMGM2NmMg
    UHJvamVjdCBDQTCCAaIwDQYJKoZIhvcNAQEBBQADggGPADCCAYoCggGBALTMQ3tS
    QkLiFK1zP1Oi4KgURR92Y189XdTW8rQE5hmU2Hry1gJomEl3edhWbndQV88RaDcH
    DIHu+K3p3BVx+bQbLe5vgaCjZvH/0p/5aZ6+oZj7inMXNlKKw4+ogivaNmHyu+pu
    qpkIU6L9cKxsGogDqR6VxM3s4naVwAmjQ5TpeUnm3ApiqWa0EsF3a24h4S+2JS1r
    C8g8LnaDkUx2Cp0LnFRQ8zhXSXdjfd/FkY/G5pdjB+SISXZBRej15nVwXN5XuznI
    l7zcArjLUAYg6mNKEAKv5oKSWjQ2DTS799bp4Oib+MbkcRVToqt/zk/iSnNsgIBp
    uAnYbOwuhYbxLA3GMU4X9MzOatik2V7vcCGnC8IouApEYskRvtIGHjakrdauI6VA
    PGn2mGpaLzO0oSycOR2QW9rgTO3Tu9j04DXGUiCeoOrX51IfCsBEUJ+jubkSksmB
    S/KXNhlc0yEP23dnipmzT32iAYVBM05u/MqsRQMVHjYm7ZnXWZM71sRC9QIDAQAB
    oz8wPTAdBgNVHQ4EFgQUv9JmneMA34BCyaSBzfByrZtRfMkwDwYDVR0TBAgwBgEB
    /wIBADALBgNVHQ8EBAMCAQYwDQYJKoZIhvcNAQEMBQADggGBAHyjQuXmdktM0TgF
    FScsTIbhFzZjwZIG63NfgUX6b94jMRzfqaF/AWvR5dsKO4eLnZkn6Ow/6dl+hCO7
    KpfgQ6iyH1tHTEVXsgndubY7PmoZsX+lBJJWxKhY+SNEeKZrptLzB0TgnUqECtg6
    qfBMrWzm1WvYFinLd/qn9qEpVYdKm97WMvN2dHcRdV3h92mtsKlw6PSt64pyBUqG
    Tb5JjMgXY15kFPuPS4pT6fE7KF4SMuhKNrJtbozdIyim4NhBozwURx6tjCYnAGNK
    LxbpGfGn6HHmTFxBVQeeUHLTQTQeTxUlSmPeCBzmLHw5o1+syRV1+Su2xPfCMZsp
    lZ8rCAU4JrCxGP6DGjhiJPT9B6UO4xHdTzVkQh4gHHrHrz/3XUKaBQQ4epJnvboH
    M4XhhhhnMikEWJKiBYvYA8GGxVkkaEgqyZsNMygWGm+7nvnRAJt1u4R/Cs8c/V7k
    VXCwXqiFNDPgWNXDYV+Zw2Yxw6bLfYaQjl38HnUlF1x0zN94yg==
    -----END CERTIFICATE-----
    """
    my_redis = redis.StrictRedis(host=redis_host_url, username=redis_username, port=redis_port_number, db=redis_db_number, password=redis_password, ssl=redis_ssl_type)

    count_time = time.time()
    count_all_time_elapsed = time.time()
    count = 0
    count_all = -1

    while True:
        try:

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(process_huobi_orderbook, get_huobi_symbols(huobi_key))
            count_all_time = time.time()
            count_all += 1

        except Exception as e:
            print(f"에러 코드: {type(e).__name__}, 메시지: {str(e)}")
