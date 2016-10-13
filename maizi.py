#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
version:0.2
last_modify:2016/8/21
description:麦子学院视频下载
"""

import requests
import bs4
import threading
from threading import Thread
import os
import re
from contextlib import closing



class ProgressBar(object):
	def __init__(self, title, count=0.0, run_status=None, fin_status=None, total=100.0, unit='', sep='/', chunk_size=1.0):
		super(ProgressBar, self).__init__()
		self.info = "[%s] %s %.2f %s %s %.2f %s"
		self.title = title
		self.total = total
		self.count = count
		self.chunk_size = chunk_size
		self.status = run_status or ""
		self.fin_status = fin_status or " " * len(self.status)
		self.unit = unit
		self.seq = sep

	def __get_info(self):
		# 【名称】状态 进度 单位 分割线 总数 单位
		_info = self.info % (self.title, self.status, self.count/self.chunk_size, self.unit, self.seq, self.total/self.chunk_size, self.unit)
		return _info

	def refresh(self, count=1, status=None):
		self.count += count
		# if status is not None:
		self.status = status or self.status
		end_str = "\r"
		if self.count >= self.total:
			end_str = '\n'
			self.status = status or self.fin_status
		print(self.__get_info(), end=end_str)



class DownloadThread(Thread):
	def __init__(self,url,path,filename):
		super().__init__()
		self.url = url
		self.path = path
		self.filename = filename

	def run(self):
		with closing(requests.get(self.url, stream=True)) as res:
			chunk_size = 4096
			content_size = int(res.headers['content-length'])
			progress = ProgressBar(self.filename, total=content_size, unit="KB", chunk_size=chunk_size, run_status="正在下载", fin_status="下载完成")
			with open(self.path,'wb') as f:
				for chunk in res.iter_content(chunk_size=chunk_size):
					f.write(chunk)
					progress.refresh(count=len(chunk))

def get_url(base_url):
	urls={}
	origin = 'http://www.maiziedu.com'
	res = requests.get(base_url)
	soup = bs4.BeautifulSoup(res.content,'lxml')
	title = soup.find('h1',attrs={'class':'color33 font24 marginB10'}).get_text()
	ul = soup.find_all('ul')
	lis = ul[1].find_all('li')
	for li in lis:
		urls[li.a.get_text().replace('.','_').replace(':','_')]= origin+li.a.get('href')

	return urls,title

def get_video_url(url):
	# soup = bs4.BeautifulSoup(requests.get(url).content,'lxml')
	# source =soup.find('source')
	# return source.get('src')
	res = requests.get(url).text
	pattern = 'lessonUrl = "(.*?)"'
	url = re.findall(pattern,res)[0]
	return url


def video_download(urls,title):
	threads=[]
	if not os.path.exists('video/'+title):
		os.makedirs('video/'+title)
	for key,value in urls.items():
		file_path='video/'+title+'/'+key+'.mp4'
		if not os.path.exists(file_path):
			down_thread = DownloadThread(value,file_path,key)
			threads.append(down_thread)
	return threads


if __name__== '__main__':
	'''
	base_url：要下载教程的目录界面url
	'''
	base_url="http://www.maiziedu.com/course/552/"

	urls,title = get_url(base_url)
	for key,value in urls.items():
		urls[key] = get_video_url(value)
	print(urls)
	threads = video_download(urls,title)

	for thread in threads:
		thread.start()










