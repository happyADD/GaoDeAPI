import json
from time import sleep

import apiget as geoget

# 打开并读取文件
with open('cities.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

formatted_data = []
current_region = None
current_province = None

for line in lines:
    line = line.strip()
    if not line:
        continue
    if line.endswith("地区"):
        current_province = line
        continue
    elif line != '\n':
        province = line.split(' ')[0]
        cities = line.split(' ')[1].split('、')
        for city in cities:
            city_str = city + "市"
            formatted_data.append(province + city_str)

city_locations = []

for item in formatted_data:
    print(item)
    # 获取地理信息
    info_dict = geoget.geo_code2location(item)
    # 创建一个字典，将城市名称和地理信息组合起来
    city_dict = {"city": item, "adcode": info_dict['adcode'], "location": info_dict['location']}
    # 将字典添加到列表中
    city_locations.append(city_dict)

with open('city_locations.txt', 'w', encoding='utf-8') as file:
    cnt = 1
    for item in city_locations:
        file.write(str(cnt) + "," + str(item['adcode']) + "," + item['city'] + "," + item['location'][0] + "," +
                   item['location'][1] + "\n")
        cnt += 1
