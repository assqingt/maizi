#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
version:0.1
last_modify:2016/7/3
description:麦子学院视频下载
"""

import requests
import bs4
from collections import OrderedDict
from threading import Thread
import os
import time


class DownloadThread(Thread):
	def __init__(self,url,path):
		super().__init__()
		self.url = url
		self.path = path

	def run(self):
		res = requests.get(self.url).content
		with open(self.path,'wb') as f:
			f.write(res)

def get_url(base_url):
	urls=OrderedDict()
	origin = 'http://www.maiziedu.com'
	res = requests.get(base_url)
	soup = bs4.BeautifulSoup(res.content,'lxml')
	title = soup.find('h1',attrs={'class':'color33 font24 marginB10'}).get_text()
	ul = soup.find_all('ul')
	lis = ul[1].find_all('li')
	for li in lis:
		# urls[li.a.get_text()]= origin+li.a.get('href')
		urls[li.a.get_text().replace('.','_').replace(':','_')]= origin+li.a.get('href')
	return urls,title

def get_video_url(url):
	soup = bs4.BeautifulSoup(requests.get(url).content,'lxml')
	source =soup.find('source')
	return source.get('src')


def video_download(urls,title):
	threads=[]
	if not os.path.exists('video/'+title):
		os.mkdir('video/'+title)
	# for i,value in enumerate(urls.values()):
		# file_path='video/'+str(i+1)+'.mp4'
	for key,value in urls.items():
		file_path='video/'+title+'/'+key+'.mp4'
		down_thread = DownloadThread(value,file_path)
		down_thread.start()
		threads.append(down_thread)
	return threads


# def rename_video(urls):
# 	base_path = 'd:\\PyPro\\video_downloader\\video'
# 	files = os.listdir(base_path)
# 	for key,value in zip(urls.keys(),files):
# 		new_name = key.replace('.','_').replace(':','_')+'.mp4'
# 		os.rename(os.path.join(base_path,value),os.path.join(base_path,new_name))

if __name__== '__main__':
	'''
	base_url：要下载教程的目录界面url
	'''
	# base_url="http://www.maiziedu.com/course/307/"
	base_url="http://www.maiziedu.com/course/734/"

	start = time.time()
	urls,title = get_url(base_url)
	for key,value in urls.items():
		urls[key] = get_video_url(value)
	threads = video_download(urls,title)
	for thread in threads:
		thread.join()
	end = time.time()
	print(title+'下载完成,耗时:{:.2}s'.format(end-start))

	# rename_video(urls)
