import time
import requests
import datetime, csv
import random, os
import queue
import traceback
from threading import Thread

class User_profile():
    def __init__(self):
        csv_name = "./profile/profile_" + str(datetime.datetime.now().strftime('%Y%m%d')) + ".csv"
        os.mknod(csv_name)
        self.f = open(csv_name, 'a')
        self.write = csv.writer(self.f)
        self.write.writerow(["user_id", "user_name", "last_online_time", "batch_id", "join_date", "is_premium", "scrap_date"])
        self.my_queue = queue.Queue()
        self.time1 = time.time()
        self.yu = 0

    def get_last_user_id(self):
        x = datetime.datetime.now() - datetime.timedelta(days=1)
        batch_id = x.strftime('%Y%m%d')
        with open("max_user.csv") as f:
            reader = csv.reader(f)
            rows = [row for row in reader]
            for row in rows[1:]:
                if row[2] == batch_id:
                    last_user_id = row[0]
                    return int(last_user_id)

    def gene_user_id(self):
        max_user_id = self.get_last_user_id()
        gap_value = int(max_user_id/50000)
        for i in range(50000):
            self.my_queue.put(int(gap_value*(i+random.random())))

    def get_onlinestatus(self, user_id):
        url = "https://api.roblox.com/users/" + str(user_id) + "/onlinestatus"
        headers = {
            'authority': 'api.roblox.com',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        # response = requests.get(url=url, headers=headers, proxies={'https': 'http://10.153.89.47:7890'})
        response = requests.get(url=url, headers=headers)
        result = response.json()
        last_online_time = result["LastOnline"]
        return last_online_time

    def is_premium(self, user_id):
        url = "https://groups.roblox.com/v1/users/"+user_id+"/groups/primary/role"
        headers = {
            'authority': 'groups.roblox.com',
            'sec-ch-ua': '"Chromium";v="92", "Not A;Brand";v="99", "Google Chrome";v="92"',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'origin': 'https://www.roblox.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.roblox.com/',
            'accept-language': 'zh-CN,zh;q=0.9'
        }
        # response = requests.get(url=url, headers=headers, proxies={'https': 'http://10.153.89.47:7890'})
        response = requests.get(url=url, headers=headers)
        result = response.text
        if result == "null":
            return 0
        else:
            return 1

    def get_profile(self, user_id):
        url = "https://users.roblox.com/v1/users/" + user_id
        headers = {
            'authority': 'users.roblox.com',
            'sec-ch-ua': '"Chromium";v="92", "Not A;Brand";v="99", "Google Chrome";v="92"',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'origin': 'https://www.roblox.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.roblox.com/',
            'accept-language': 'zh-CN,zh;q=0.9'
        }
        # response = requests.get(url=url, headers=headers, proxies={'https': 'http://10.153.89.47:7890'})
        response = requests.get(url=url, headers=headers)
        if "errors" in response.text:
            print(response.text)
            time.sleep(0.25)
            return False
        else:
            result = response.json()
            user_name = result['name']
            join_date = result['created'][:10]
            return [user_name, join_date]

    def handle_one_user(self):
        while True:
            try:
                if self.my_queue.qsize() == 0:
                    print(time.time()-self.time1)
                    break
                user_id = self.my_queue.get()
                user_id = str(user_id)
                time.sleep(0.15)
                profile = self.get_profile(user_id)
                if profile:
                    last_oneline_time = self.get_onlinestatus(user_id)
                    is_premium = self.is_premium(user_id)
                    data_list = []
                    data_list.append(user_id)
                    data_list.append(profile[0])
                    data_list.append(last_oneline_time)
                    data_list.append(datetime.datetime.now().strftime('%Y%m%d%H'))
                    data_list.append(profile[1])
                    data_list.append(is_premium)
                    data_list.append(int(time.time()))
                    print(data_list)
                    self.write.writerow(data_list)
                else:
                    print("未爬取到id:"+user_id)
            except:
                print(traceback.format_exc())

if __name__ == "__main__":
    while True:
        if datetime.datetime.now().hour == 3:
            user_profile = User_profile()
            user_profile.gene_user_id()
            for i in range(2):
                Thread(target=user_profile.handle_one_user).start()
            time.sleep(3600)
        else:
            time.sleep(60)
