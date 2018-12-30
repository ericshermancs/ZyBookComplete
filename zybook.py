import os,sys,re,time
import requests
import getpass
from pprint import pprint
import json
import hashlib
import datetime


def checksum(activity_id, ts, token):
	md5 = hashlib.md5()
	md5.update(f'content_resource/{activity_id}/activity'.encode('utf-8'))
	md5.update(ts.encode('utf-8'))
	md5.update(token.encode('utf-8'))
	return md5.hexdigest()

def login(email,password):
	url = 'https://zyserver.zybooks.com/v1/signin'

	data = {'email': email, 'password': password}

	r = requests.post(url=url,json=data)

	if not r.json()['success']:
		print('[ERROR] LOGIN FAILED')
		sys.exit()

	return r.json()

def get_books(token,user_id):
	url = f'https://zyserver.zybooks.com/v1/user/{user_id}/items?items=%5B%22zybooks%22%5D&auth_token={token}'
	r = requests.get(url)
	if not r.json()['success']:
		print('[ERROR] GETTING ZYBOOKS FAILED')
		sys.exit()

	return r.json()['items']['zybooks']
		
def get_chapters(token,zybook_code):
	url = f'https://zyserver.zybooks.com/v1/zybooks?zybooks=%5B%22{zybook_code}%22%5D&auth_token={token}'
	r = requests.get(url)
	if not r.json()['success']:
		print('[ERROR] GETTING CHAPTERS FAILED')
		sys.exit()

	return r.json()['zybooks']

def get_problems(token,zybook_code,chapter_number,section_number):
	url = f'https://zyserver.zybooks.com/v1/zybook/{zybook_code}/chapter/{chapter_number}/section/{section_number}?auth_token={token}'
	r = requests.get(url)
	#pprint(r.json())
	return r.json()

def solve_problem(token,zybook_code,problem):


	activity_id = problem['id']
	activity_type = problem['type']
	print(activity_type)
	payload = problem['payload']

	if activity_type == 'html':
		return
	url = f'https://zyserver.zybooks.com/v1/content_resource/{activity_id}/activity'
	headers = {
	    'Origin': 'https://learn.zybooks.com',
	    'Accept-Encoding': 'gzip, deflate, br',
	    'Accept-Language': 'en-US,en;q=0.9',
	    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
	    'Content-Type': 'application/json',
	    'Accept': 'application/json, text/javascript, */*; q=0.01',
	    'Referer': 'https://learn.zybooks.com/zybook/QCCSCI355TeitelmanFall2018/chapter/1/section/1',
	    'Connection': 'keep-alive',
	}


	now = datetime.datetime.now()
	timestamp = now.strftime("%Y-%m-%dT%H:%M.000")
	cs = checksum(activity_id, timestamp, token)


	parts = problem['parts']
	if parts == 0:
		data = {"part":0,"complete":True,"metadata":"{}","zybook_code":zybook_code,"auth_token": token ,"timestamp":timestamp,"__cs__": checksum(activity_id,timestamp,token)}
			
		pprint(data)

		r = requests.post(url=url,json=data,headers=headers)
		print(r.text)
	for part in range(parts):
		
		data = {"part":part,"complete":True,"metadata":"{}","zybook_code":zybook_code,"auth_token": token ,"timestamp":timestamp,"__cs__": checksum(activity_id,timestamp,token)}
		
		pprint(data)

		r = requests.post(url=url,json=data,headers=headers)
		print(r.text)

	
	

def main():
	email = input('Input email: ')
	password = getpass.getpass("Input password:")
	result = login(email,password)
	token = result['session']['auth_token']
	user_id = result['user']['user_id']
	books = get_books(token,user_id)
	total_types = set()
	for book in books:
		if book['user_zybook_role'] != 'Student':
			continue
		#pprint(book)
		zybook_code = book['zybook_code']
		chapters = get_chapters(token,zybook_code)
		for term in chapters:
			for chapter in term['chapters']:
				chapter_number = chapter['number']
				for section in chapter['sections']:
					section_number = section['number']
					problems = get_problems(token,zybook_code,chapter_number,section_number)
					for problem in problems['section']['content_resources']:
	
						solve_problem(token,zybook_code,problem)
					
	
if __name__ == '__main__':
	main()

