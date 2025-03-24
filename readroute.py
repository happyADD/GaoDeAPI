from time import sleep
import apiget as geoget

city_locations = []
with open('city_locations.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        id = line.split(' ')[0]
        city = line.split(',')[2]
        location = [line.split(',')[3],line.split(',')[4].split('\n')[0]]
        a = 1
        city_location = {"id": id, "city": city, "location": location}
        city_locations.append(city_location)

city_num = len(city_locations)

routes = []
total_num = city_num * (city_num - 1) / 2
now_num = 0
fail_num = 0

print(f"读取到{city_num}个城市，共有{total_num}条路线，预计发送请求{total_num * 3:.0f}次")
sleep(1)

for i in range(city_num):
    for j in range(i + 1, city_num):
        path = geoget.location2route(city_locations[i]['location'], city_locations[j]['location'])
        route = {"src":city_locations[i]['city'], "dst":city_locations[j]['city'],"route":path}
        if route is not None:
            print(f"从{route['src']}到{route['dst']},距离{int(path['distance'])/1000:.2f}Km,大约用时{int(path['distance'])/110000:.2f}小时")
            routes.append(route)
            now_num += 1
            print(f"进度{now_num}/{total_num:.0f},出错{fail_num}个")

            with open('routes.txt', 'a', encoding='utf-8') as file:
                file.write(f"{city_locations[i]['id']}->{city_locations[j]['id']},{int(path['distance'])/1000:.2f}\n")
            with open('routes_detail.txt', 'a', encoding='utf-8') as file:
                file.write(f"---\n{city_locations[i]['id']}:{city_locations[i]['city']}->{city_locations[j]['id']}:{city_locations[j]['city']},{int(path['distance'])/1000:.2f}\n{path['steps']}")

        else:
            fail_num += 1
            print(f"{route['src']} 到 {route['dst']} 路线查找出错")

