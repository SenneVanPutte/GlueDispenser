import requests
import json
import urllib

import os

import hashlib

#Documentation in https://piwigo.org/demo/tools/ws.htm

class PhotoDB():
	def __init__(self):
		self.url = 'https://photodb.iihe.ac.be/piwigo/ws.php?format=json'
		self.user = 'Senne'
		self.pwd = '$Achanger'
		self.cookies = None
		self.known_albums = {}
		
		self.log_in()
		self.load_albums()

	## Communication functions
	def post_req(self, request, **kwargs):
		#api_req = requests.get(self.url+request)
		if self.cookies is None: 
			api = requests.post(self.url, request, **kwargs)
		else: 
			api = requests.post(self.url, request, cookies=self.cookies, **kwargs)
		response = json.loads(api.content.decode('utf-8'))
		return api, response
	
	def get_req(self, request, **kwargs):
		#api_req = requests.get(self.url+request)
		if self.cookies is None: 
			api = requests.post(self.url, request, **kwargs)
		else: 
			api = requests.post(self.url, request, cookies=self.cookies, **kwargs)
		response = json.loads(api.content.decode('utf-8'))
		if 'fail' in response['stat']: print(response)
		return api, response
	
	def read_response(self, response):
		if 'ok' in resp['stat']: print('success')
		else:
			print('fail, response below')
			print(resp)
		
	def log_in(self):
		print('PhotoDB: logging in')
		data = {
			"method": "pwg.session.login", 
			"username": self.user, 
			"password": self.pwd
		}
		api, resp = self.post_req(data)
		self.cookies = api.cookies
	
	def clear_cookies(self):
		self.cookies = None

	## Album functions
	def find_album_id(self, album_name):
		#if not album_name in self.known_albums: self.load_albums()
		
		try:
			return self.known_albums[album_name]['id']
		except KeyError:
			return -1
				
	def load_albums(self):
		print('PhotoDB: loading albums')
		self.known_albums = {}
		
		data = {
			"method"   : "pwg.categories.getList",
			"recursive": True,
		}
		api, resp = self.get_req(data)
		
		for key in resp['result']['categories']:
			name = str(key['name'])
			id = int(key['id'])
			status = str(key['status'])
			try:
				parent = int(key['id_uppercat'])
			except TypeError:
				parent = None
			self.known_albums[name] = {
				'id' : id,
				'status': status,
				'parent': parent,
			}
		
	def create_album(self, album_name, status='public', parent=20, verbose=False):
		if verbose: print('PhotoDB: creating album '+album_name)
		data = {
			"method": "pwg.categories.add",
			"name"  : album_name,
			"parent": parent,
			"status": status
		}
		api, resp = self.get_req(data)
		if verbose: self.read_response(resp)

		self.load_albums()
		
	def create_album_recursive(self, album_path, status='public', verbose=False):
		'''
		create albums of style 'dir1/subdur1/subsubdir3/...'
		Every folder name needs to be unique
		'''
		self.load_albums()
		dirs = album_path.split('/')
		exist = []
		ids = []
		for idx,dir in enumerate(dirs):
			if self.find_album_id(dir) > 0: exist.append(True)
			else: exist.append(False)
			ids.append(self.find_album_id(dir))
			
			if idx == 0: continue
			if not exist[idx-1] and exist[idx]: 
				raise IOError('PhotoDB: recursive album failed, album "'+dirs[idx]+'", in path "'+album_path+'" exists')
		
		parent = 20
		for idx,dir in enumerate(dirs):
			curr_id = self.find_album_id(dir)
			if idx > 0:
				tmp_parent = self.find_album_id(dirs[idx-1])
				if tmp_parent > 0: parent = tmp_parent 
			
			if curr_id < 0:
				self.create_album(dir, status=status, parent=parent, verbose=verbose)
				
	#def delete_album(self, album_name)
	
	## Picture functions
	def upload_image(self, picture_path, target_album, verbose=False):
		# Load picture (and see if it exists)
		binary_image = open(picture_path, 'rb')
		
		# Check album, make if not there
		album_name = target_album.split('/')[-1]
		album_id = self.find_album_id(album_name)
		if album_id < 0:
			self.create_album_recursive(target_album, verbose=verbose)
		album_id = self.find_album_id(album_name)
		
		# Prepare request info 
		data = {
			"method"   : "pwg.images.addSimple",
			"category" : album_id,
		}
		
		header = {
			"Content_Type": "form-data"
		}
		
		files = {
			'image': binary_image
		}
		
		# Post image
		api, response = self.post_req(data, headers=header, files=files)
		if verbose: self.read_response(response)
			
	
		
		
		
		

if __name__ == '__main__':
	db = PhotoDB()
	#db.log_in()
	#db.load_albums()
	#db.load_albums()
	# db.load_albums()
	# db.load_albums()
	# db.create_album('Senne_Tests_Album_Creation1', status='private')
	# db.create_album('Senne_Tests_Album_Creation2', status='private')
	# db.create_album('Senne_Tests_Album_Creation3', status='private')
	#db.create_album_recursive('ffrrddrr/Senne_Tests_Album_Creation-2/rfgt/gfch', status='private')
	#db.create_album_recursive('Senne_Tests/picture_upload_test', status='private')
	#db.upload_picture('/c/Users/LitePlacer/Desktop/pVf_water_50-160.png', 'Senne_Tests/picture_upload_test')
	db.upload_picture('C:\\Users\\LitePlacer\\Documents\\liteplacer-glue-no-timeout\\images\\webcam\\2021_Apr_21\\I-Pigtail_x_-24.0_y_101.5_z_0.0_2021_Apr_21_at_18_31_03.png', 'Senne_Tests/picture_upload_test')
	#print db.find_album_id('Senne_Tests_Album_Creation2')
	
	