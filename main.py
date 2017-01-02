# -*- coding:utf-8 -*-
import re
import sys
import os
from bs4 import BeautifulSoup
import requests

# 工具类 替换文本内容的一些标签和空白
class Tool:
    removeImg = re.compile('<img.*?>| {7}|')
    removeAddr = re.compile('<a.*?>|</a>')
    replaceBr = re.compile('<br><br>|<br>')
    replacePara = re.compile('<p.*?>')
    removeAllTag = re.compile('<.*?>')
    def repalce(self,x):
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceBr,"\n",x)
        x = re.sub(self.replacePara,"\n    ",x)
        x = re.sub(self.removeAllTag,"",x)
        return x.strip()

# 文件操作
class FileSetting:

    # 保存图片
    def save_img(self, url):
        image_name = url[-9:-4]
        image = requests.get(url)
        f = open(image_name + '.jpg', 'ab')
        f.write(image.content)
        f.close()

    # 创建文件夹
    def mkdir(self, path):
        path = path.strip()
        existence = os.path.exists(path)
        if not existence:
            print("建立文件夹"+path)
            os.makedirs(path)
            return True
        else:
            print(path+"存在")
            return False

    # 将文本内容写入文件
    def write_to_file(self, contents, file):
        for content in contents:
            file.write(content)

class BDTB:
    # 初始化
    def __init__(self, baseUrl, seeLZ):
        # 初始化工具类
        self.tool = Tool()
        self.fileSetting = FileSetting()
        # 基地址 和 url参数
        self.baseURL = baseUrl
        self.seeLZ = "?see_lz="+str(seeLZ)
        # 初始化文件和文件名
        self.file = None
        self.defaultTitle = u"百度贴吧"

    # 传入页码,获取该页的代码
    def get_page(self, page_num):
        try:
            url = self.baseURL + self.seeLZ + "&pn=" + str(page_num)
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            if hasattr(e, "reason"):
                print(u"链接百度贴吧失败,原因", e.reason)
                return None
        else:
            # print(response.text)
            return response.text

    # 获取标题
    def get_title(self, page):
        soup = BeautifulSoup(page,"lxml")
        result = soup.find('h3', class_="core_title_txt")
        # pattern = re.compile('<h3 class="core_title_txt .*?>(.*?)</h3>', re.S)
        # result = re.search(pattern, page)
        if result:
            title = result['title']
            return title
        else:
            print("没有匹配到标题")
            return None

    # 获得帖子的页数
    def get_page_num(self,page):
        pattern = re.compile(r'<li class="l_reply_num.*?<span.*?>(.*?)</span>.*?<span.*?>(\d*)</span>',re.S)
        result = re.search(pattern, page)
        if result:
            return result.group(2).strip()
        else:
            print ("没有匹配到页数")
            return None

    # 获得每层楼的内容
    def get_content(self,page):
        pattern = re.compile('<div id="post_content.*?>(.*?)</div>', re.S)
        items = re.findall(pattern, page)
        contents = []
        for item in items:
            content = "\n" + self.tool.repalce(item)+"\n"
            contents.append(content)
        return contents

    # 设置标题
    def set_file_title(self,title):
        if title is not None:
            self.file = open(title + ".txt", "w+")
        else:
            self.file = open(self.defaultTitle + ".txt","w+")
    # # 写入文件
    # def write_to_file(self,contents):
    #     for item in contents:
    #         self.file.write(item)

    # 获取每层楼的img的url
    def get_img(self, page):
        soup = BeautifulSoup(page, "lxml")
        images = soup.find_all('img', class_="BDE_Image")
        for image in images:
            img_url = image['src']
            self.fileSetting.save_img(img_url)

    #开始入口
    def start(self):
        index_page = self.get_page(1)
        page_num = self.get_page_num(index_page)
        title = self.get_title(index_page)
        if page_num == None:
            print("url无效")
            return
        try:
            print("帖子共" + str(page_num) + "页")
            print(u'开始保存', title)
            path = "/Users/ky/Desktop/tieba/" + str(title)
            self.fileSetting.mkdir(path)
            os.chdir(path)
            print("建立" + title + "的文本文件")
            self.set_file_title(title)
            for i in range(1, int(page_num)+1):
                page = self.get_page(i)
                print("正在写入第"+str(i)+"页数据")
                contents = self.get_content(page)
                self.fileSetting.write_to_file(contents, self.file)
                self.get_img(page)
        except IOError as r:
            print("写入异常", r)
        finally:
            print("写入完成")



# reload(sys)
# sys.setdefaultencoding('utf-8')

# print u"请输入帖子代号"
# baseURL = 'http://tieba.baidu.com/p/' + str(raw_input(u'http://tieba.baidu.com/p/'))
# seeLZ = raw_input("是否只获取楼主发言，是输入1，否输入0\n")
# floorTag = raw_input("是否写入楼层信息，是输入1，否输入0\n")
# bdtb = BDTB(baseURL,seeLZ,floorTag)
# bdtb.start()
# print("请输入帖子代号")
# baseURL = 'http://tieba.baidu.com/p/' + str(raw_input(u'http://tieba.baidu.com/p/'))
base_url = "http://tieba.baidu.com/p/2837228337"
bdtb = BDTB(base_url, 1)
bdtb.start()