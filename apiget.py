from typing import Dict, Any

import requests
import xmltodict
import time

my_api_key = '00f41521d8354a9e6efdd13861111c91'
sub_api_key = ''

def ip_location(api_key=my_api_key, ip=''):
    url = f"https://restapi.amap.com/v5/ip?key={api_key}&keywords=北京"
    response = requests.get(url)
    if response.status_code == 200:
        location_data = response.json()
        if location_data['status'] == '1':
            return location_data['location']
        else:
            print(f"Error: {location_data['info']}")
            return None
    else:
        print(f"HTTP Error: {response.status_code}")
        return None


api_key = '00f41521d8354a9e6efdd13861111c91'
location = ip_location(api_key)
if location:
    print(f"IP定位的地理位置为: {location}")


def keywords_search(keyword: str, api_key: str = my_api_key) -> list:
    url = f"https://restapi.amap.com/v5/place/text?keywords={keyword}&types=141201&key={api_key}"
    response = requests.get(url)
    res_json = response.json()
    return res_json['pois']


def geo_code2location(address: str, api_key: str = my_api_key) -> dict[str, list]:
    url = f"https://restapi.amap.com/v3/geocode/geo?address={address}&output=XML&key={api_key}"
    response = requests.get(url)
    res_dict = xmltodict.parse(response.text)
    status = res_dict['response']['status']
    info = res_dict['response']['info']
    if status != '1':
        print(f"Warning,error code: {status},error message: {info}")
        if info == "CUQPS_HAS_EXCEEDED_THE_LIMIT":
            print("Out of QPS,sleeping")
            time.sleep(0.5)
            print("sleeping done")
            return geo_code2location(address, api_key)
        elif info == "DAILY_QUERY_OVER_LIMIT":
            print("Key is up to limit!")
            exit(-1)
    print(res_dict)

    if res_dict['response']['count'] == '0':
        with open("error_log.txt", "a") as f:
            f.write(f"{address}未成功查询地理信息")
            return None
    elif res_dict['response']['count'] == '1':
        location = res_dict['response']['geocodes']['geocode']['location'].split(',')
        adcode = res_dict['response']['geocodes']['geocode']['adcode']
    else:
        location = res_dict['response']['geocodes']['geocode'][0]['location'].split(',')
        adcode = res_dict['response']['geocodes']['geocode'][0]['adcode']
    return {'adcode': adcode, 'location': location}


"""
# 油电混动车
# 车牌号自己家的
# 允许使用轮渡
# strategy驾驶策略：默认速度优先
0：速度优先（只返回一条路线），此路线不一定距离最短
1：费用优先（只返回一条路线），不走收费路段，且耗时最少的路线
2：常规最快（只返回一条路线）综合距离/耗时规划结果
32：默认，高德推荐，同高德地图APP默认
33：躲避拥堵
34：高速优先
35：不走高速
36：少收费
37：大路优先
38：速度最快
39：躲避拥堵＋高速优先
40：躲避拥堵＋不走高速
41：躲避拥堵＋少收费
42：少收费＋不走高速
43：躲避拥堵＋少收费＋不走高速
44：躲避拥堵＋大路优先
45：躲避拥堵＋速度最快
# waypoints 途径点，list [x,y] 
"""


def location2route(location1: list, location2: list, strategy: int = 0, waypoints: list = [],
                   api_key: str = my_api_key) -> float:
    """https://lbs.amap.com/api/webservice/guide/api/newroute"""
    params = f"key={api_key}&strategy={strategy}&ferry=0"
    url = f"https://restapi.amap.com/v5/direction/driving?origin={location1[0]},{location1[1]}&destination={location2[0]},{location2[1]}&" + params
    response = requests.get(url)
    res_dict = response.json()
    status = res_dict['status']
    info = res_dict['info']
    if status != '1':
        print(f"Warning,error code: {status},error message: {info}")
        if info == "CUQPS_HAS_EXCEEDED_THE_LIMIT":
            print("Out of QPS,sleeping")
            time.sleep(0.5)
            print("sleeping done")
            return location2route(location1, location2, strategy, waypoints, api_key)
        elif info == "DAILY_QUERY_OVER_LIMIT":
            print("Key is up to limit!")
            exit(-1)
        elif info == "'INVALID_PARAMS'":
            print(f"invalid params: {info}")
            exit(-1)
    print(res_dict)

    return res_dict['route']['paths'][0]


def route_calculate(address_A: str, address_B: str, api_key: str = my_api_key) -> str:
    location_A = geo_code2location(address_A, api_key)
    location_B = geo_code2location(address_B, api_key)
    if location_A is None :
        with open("error_log.txt", "a") as f:
            f.write(f"function:route_calculate, {address_A}未成功查询")
            return None
    if location_B is None:
        with open("error_log.txt", "a") as f:
            f.write(f"function:route_calculate, {address_B}未成功查询")
            return None
    path = location2route(geo_code2location(address_A)['location'], geo_code2location(address_B)['location'])
    distance = path['distance']
    steps = path['steps']
    time_span = int(distance) / 110000.0
    string = f"从{address_A}到{address_B}，距离{int(distance) / 1000.0:.2f}千米,预计用时{time_span:.2f}小时\n"
    print(string)
    cnt = 0
    for step in steps:
        cnt += 1
        string += str(cnt) + " " + step['instruction'] + '\n'
    return string


if __name__ == '__main__':
    print(route_calculate("北京市北京市", "海南省三亚市"))
