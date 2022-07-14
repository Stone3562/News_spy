# *** encoding = utf-8 ***

from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup

path = '/Users/stone/Desktop/'

Meta_Url = 'https://tv.cctv.com/lm/xwlb/'
ua = {'User-Agent': UserAgent().random}
r = requests.get(Meta_Url, headers=ua, timeout=30)

soup = BeautifulSoup(r.content, "lxml")
file_name = soup.find(class_='rilititle').find('p').text.replace('-', '')  # 找到当日的日期作为文件名
li_list = soup.find(class_='rililist newsList').select('ul > li')  # 找到所有当日新闻列表

md = path + file_name + '.md'
with open(md, 'w') as f:
    for li in li_list:
        li_url = li.a['href']  # 获取子Url
        name_con = requests.get(li_url, headers={'User-Agent': UserAgent().random}, timeout=30)
        name_soup = BeautifulSoup(name_con.content, 'lxml')

        col_name = name_soup.find(class_='tit').text.replace("[视频]", '')  # 获取标题
        f.write('## ' + col_name)  # 写入文档
        f.write('\r\n')  # 空行

        paras = name_soup.find(class_='content_area').find_all('p')  # 找到所有当日新闻列表
        for para in paras:
            if para.find('strong'):
                p = ('### ' + para.text)
                p = p.replace("### 央视网消息（新闻联播）：", '')
            else:
                p = para.text
            f.write(p)  # 写入内容
            f.write('\r\n\r\n')  # 空行

print('文件保存成功')
