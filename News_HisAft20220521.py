#  ___coding=UTF-8___
# 本文本主要用于历史新闻联播下载，因网页改版，仅支持2022年5月21日以后的新闻联播，请知悉

import time
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
from queue import Queue
import threading
import datetime

start_date = 1 # 从今天之前第几天开始，此处需修改
end_date = 30 # 截止至今天前第几天，此处需修改

thread_count = 5     # 创建5个线程

path = '/Users/stone//Desktop/ls/' #可根据实际情况改变，后期可加入识别文件夹地址是否存在，或新建该地址。
None_Url = 'https://tv.cctv.com/lm/xwlb/day/{}.shtml'

date_urls = []
file_names = []

class DownloadThread(threading.Thread):
    def __init__(self, queue: Queue):
        super().__init__(daemon=True)
        self.queue = queue

    def run(self):
        while not self.queue.empty():
            day_job = self.queue.get()
            day_name = str(day_job[0])
            day_url = str(day_job[1])

            r = requests.get(day_url, headers = {'User-Agent' : UserAgent().random} ,timeout = 30)
            soup = BeautifulSoup(r.content,"lxml")
            li_list = soup.find_all('li') #找到所有当日新闻列表
           
            md = path + day_name + '.md'
            with open (md,'w') as f:

                for li in li_list: 
                    li_url = li.a['href'] #获取子Url
                    name_con = requests.get(li_url, headers = {'User-Agent' : UserAgent().random},timeout = 30)
                    name_soup = BeautifulSoup(name_con.content,'lxml')

                    col_name = name_soup.find(class_='tit').text.replace("[视频]",'') #获取标题
                    f.write('## ' + col_name) #写入文档
                    f.write('\r\n') #空行

                    paras = name_soup.find(class_='content_area').find_all('p') #找到所有当日新闻列表
                    for para in paras:
                        if para.find('strong'):
                            p = ('### ' + para.text)
                            p = p.replace("### 央视网消息（新闻联播）：",'')
                        else:
                            p = (para.text)     
                        f.write(p) #写入内容
                        f.write('\r\n\r\n') #空行

            f.close()       
            print('{}日新闻已下载'.format(str(day_name)))

def lists_format(start_date, end_date):  #  格式化所有日期链接
    for d in range(start_date,end_date):
        Target_Time = datetime.date.today() - datetime.timedelta(start_date)
        file_name = str(Target_Time).replace('-','') #找到当日的日期作为文件名
        Url = None_Url.format(file_name)
        date_urls.append(Url)
        file_names.append(file_name)
        start_date += 1

    return date_urls,file_names


def days_queue():     # 创建队列，安排链接入组
    q = Queue()
    for i in range(len(date_urls)):
        cpt_url = date_urls[i]
        cpt_name = file_names[i]
        q.put([cpt_name, cpt_url])

    return q


def create_threading(queue):     # 创建线程
    thread_list = []
    for i in range(thread_count):
        thread = DownloadThread(queue)
        thread.start()
        thread_list.append(thread)

    for thread in thread_list:
        thread.join()


def main():
    lists_format(start_date, end_date)    
    queue = days_queue()
    create_threading(queue)
    time.sleep(5)

if __name__ == '__main__':
    main()
