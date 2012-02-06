from connector.elfinder.exceptions import ParameterError, ElFinderCommandError
from connector.settings import ELFINDER_ROOT, ELFINDER_URL, ELFINDER_THUMB, ELFINDER_THUMB_URL

from datetime import datetime
import os
import hashlib
import mimetypes as mimes
import re

class BaseCommand(object):
	'''The Base Command Abstract Class'''
	def __init__(self, **kwargs):
		#if re.match(r'^[A-Za-z_]+[A-Za-z0-9]*$', '_ajkau8hq')
		self.success = False
		self.errors = []
		self.result = {}
		self.can_execute = False
		self.result_type = 'application/json'
		self.headers = None
		self.required = []
		self.optional = []
		self.req = kwargs['request']
		for k, v in self.req.params.items():
			try:
				if re.match(r'^[A-Za-z_]+[A-Za-z0-9]*$', k):
					setattr(self, k, v[0])
				elif re.match(r'^[A-Za-z_]+[A-Za-z0-9]*\[\]$', k):
					setattr(self, k, v)
				else:
					#prefix k with underscore
					setattr(self, '_%s'%k, v)
			except:
				pass
		try:
			import Image
			self.imglib = True
		except ImportError:
			self.imglib = False
		self.config()
	def config(self):
		''' Extend __init__ '''
		pass
	def get_result(self):
		return self.result
	def get_headers(self):
		return self.headers
	def get_result_type(self):
		return self.result_type
	def get_errors(self):
		return self.errors
	def execute(self):
		raise NotImplementedError
	def validate_params(self):
		for param in self.required:
			if hasattr(self, param):
				if getattr(self, para):
					self.can_execute = True
				else:
					self.can_execute = False
					break
			else:
				self.can_execute = False
				break
		if not self.required:
			self.can_execute = True
		#check also for self.optional
	def get_url(self, path):
		elfinder_root = ELFINDER_ROOT
		elfinder_abspath = elfinder_root
		rel_path = os.path.relpath(path, elfinder_abspath).replace('\\','/')
		abs_url = ELFINDER_URL
		return u'%s%s'%(abs_url, rel_path)
	def get_mime(self, path):
		mime = mimes.guess_type(path)[0] or 'Unknown'
		if mime.startswith('image/'):
			return mime, True
		return mime, False
	def find_path(self, fhash, mr=None, resolution=False):
		if not mr:
			mr = u'%s'%ELFINDER_ROOT
		fp = None
		for dirpath, dirnames, filenames in os.walk(mr):
			for f in filenames:
				f = os.path.abspath(os.path.join(dirpath, f))
				rf = f
				#f = f.encode('utf8')
				if fhash == self.hash(f):
					fp = f
					if resolution:
						try:
							fp = unicode(fp, 'utf8')
						except:
							pass
					return fp
			for d in dirnames:
				d = os.path.abspath(os.path.join(dirpath, d))
				rd = d
				if fhash == self.hash(d):
					fp = d
					if resolution:
						try:
							fp = unicode(fp, 'utf8')
						except:
							pass
					return fp
			d = os.path.abspath(dirpath)
			print '' # u'````````PATH NOW ++++ %s'%d
			print '' # u'````````ELFINDER PATH NOW ++++ %s'%os.path.abspath(ELFINDER_ROOT)
			rd = d
			#d = d.encode('utf8')
			if fhash == self.hash(d):
				fp = d
				if resolution:
					try:
						fp = unicode(fp, 'utf8')
					except:
						pass
				return fp
			
		return fp
	def cwd(self, path, volume=False):
		print '' # u'PATHYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYXXXXXXXXX ' +path
		d = {}
		time = 'Today'
		ts = 0
		try:
			ts = os.stat(path).st_mtime
			time = datetime.fromtimestamp(ts).strftime("%d %b %Y %H:%M")
		except:
			pass
		d['name'] = os.path.basename(path)
		d['hash'] = self.hash(path)
		d['date'] = time
		d['ts'] = ts
		d['locked'] = 0
		d['dirs'] = self.has_dirs(path)
		d['mime'] = 'directory'
		d['size'] = self.get_size(path)
		d['read'] = True
		d['write'] = True
		d['rm'] = False
		if not volume:
			d['phash'] = self.get_parent_hash(path)
		if volume:
			d['volumeid'] = u'%s_' % d['hash'][0:2]
		if 'ONN' in path:
			d['volumeid'] = u'%s_' % d['hash'][0:2]
		return d
	def cdc(self, path):
		self.imglib
		u = []
		dirs = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
		files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]
		parent_hash = None
		for d in dirs:
			l = self.get_dir_info(d)
			u.append(l)
		#for files in cwd
		parent_hash = None
		for f in files:
			l = self.get_file_info(f)
			u.append(l)
		return u
	def filtering(self, cwd):
		dirs = [os.path.join(cwd,d) for d in os.listdir(cwd) if os.path.isdir(os.path.join(cwd, d))]
		u = []
		for d in dirs:
			l = []
			l.append(('name', os.path.basename(d)))
			l.append(('hash', self.hash(d)))
			l.append(('phash', self.get_parent_hash(d)))
			l.append(('date', datetime.fromtimestamp(os.stat(d).st_mtime).strftime("%d %b %Y %H:%M")))
			l.append(('mime', 'directory'))
			l.append(('read', True))
			l.append(('write', True))
			l.append(('rm', True))
			hdirs = self.has_dirs(d)
			l.append(('dirs', hdirs))
			if hdirs:
				u.extend(self.filtering(d))
			u.append(dict(l))
		return u
	def has_dirs(self, cwd):
		dirs = [os.path.join(cwd,td) for td in os.listdir(cwd) if os.path.isdir(os.path.join(cwd, td))]
		return bool(dirs)
	def get_size(self, path):
		total_size = 0
		if os.path.isdir(path):
			for dirpath, dirnames, filenames in os.walk(path):
				for f in filenames:
					fp = os.path.join(dirpath, f)
					if os.path.exists(fp):
						total_size += os.stat(fp).st_size
		else:
			total_size = os.lstat(path).st_size
		return total_size
	def hash(self, path):
		return u'%s_%s' % (self.real_hash(ELFINDER_ROOT)[0:2], self.real_hash(os.path.abspath(path)))
	def real_hash(self, path):
		path = u'%s'%path
		enc_path = path.encode('utf8')
		m = hashlib.md5()
		m.update(enc_path)
		return u'%s'%str(m.hexdigest())
	def get_parent_hash(self, path):
		if os.path.abspath(path) == os.path.abspath(ELFINDER_ROOT):
			return None
		ppath = os.path.dirname(path)
		return self.hash(ppath)
	def get_volume_id(self, path):
		return self.hash(ELFINDER_ROOT)[0:2]
	def get_thumb_url(self, path):
		print '\n'*10
		print 'INSIDE GET THUMB URL'
		hash = self.hash(path)
		ext = path.rsplit('.', 1)[1]
		full_path = os.path.join(ELFINDER_THUMB, u'%s.%s'%(hash, ext))
		print 'FULL PATH IS %s '%full_path
		if os.path.exists(full_path):
			return u'%s.%s'%(hash, ext)
		else:
			import Image
			image = Image.open(path)
			thumb = image.resize((50, 50), 1)
			thumb.save(full_path)
			return u's.%s'%(hash, ext)
		return u''
	def get_file_info(self, f):
		l = {}
		l['name'] = os.path.basename(f)
		l['hash'] = self.hash(f)
		parent_hash = self.get_parent_hash(f)
		if parent_hash:
			l['phash'] = parent_hash
			#print '' # 'getFILE INFOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO:::::: AFTER PARENR HASHHHHHHH .....'
		l['date'] = datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%d %b %Y %H:%M")
		mime, is_image = self.get_mime(f)
		if is_image and self.imglib:
			try:
				import Image
				l['tmb'] = self.get_thumb_url(f)
			except:
				pass
		#print '' # u'getFILE INFOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO:::::: AFTER IS IMAGE.....'
		l['mime'] = mime
		l['size'] = self.get_size(f)
		l['read'] = True
		l['write'] = True
		#print '' # u'getFILE INFOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO:::::: SOME HOW.....'
		l['rm'] = True
		l['url'] = self.get_url(f)
		#print '' # u'getFILE INFOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO:::::: AFTER GET URL.....'
		return l
	def get_dir_info(self, d):
		l = {}
		l['name'] = os.path.basename(d)
		l['hash'] = self.hash(d)
		parent_hash = self.get_parent_hash(d)
		if parent_hash:
			l['phash'] = parent_hash
		l['date'] = datetime.fromtimestamp(os.stat(d).st_mtime).strftime("%d %b %Y %H:%M")
		l['mime'] = 'directory'
		l['size'] = self.get_size(d)
		l['read'] = True
		l['write'] = True
		l['rm'] = True
		l['dirs'] = self.has_dirs(d)
		return l
	def check_name(self, name):
		print '' # '\n'*10
		print '' # 'INSIDE CHECK NAME     '
		pattren = ur'[\/\\\:\<\>]'
		if re.search(pattren, name, re.UNICODE):
			print '' # 'OUTSIDE CHECK NAME KKKKKKKK'
			return False
		print '' # 'OUTSIDE CHECK NAME KKKKKKKK TRUE'
		return True
	def file_exists(self, path, new_name):
		print '' # '\n'*9
		print '' # u'CALLING FUNCTIONFDSSJHGBHG >>>>>>>>>>>>>>>>>>>'
		print '' # 'CALLING BEFORE INCODING >>>>>>>>>>>>>>>>>>> %s'%path
		print '' # 'OS.PTH.DIRNAME IS %s'%os.path.dirname(path)
		try:
			path = u'%s'%unicode(path, 'utf8')
		except:
			print '' # 'This is an Error for English file names ---- F'
		new_name = u'%s'%new_name
		print '' # 'FILE EXISTS TURNED TO UNICODE SUCESSSSS '
		abspath = os.path.join(path, new_name)
		print '' # u'CALLING FUNCTIONFDSSJHGBHG PHASE 2 %s'%os.path.dirname(abspath)
		print '' # '\n'*6
		#print '' # u'NOE KLJJKJKJ PATH BBNNNMK<KOKOKO ::: %s '%abspath
		return os.path.exists(abspath)
	def get_info(self, path):
		if os.path.isdir(path):
			return self.get_dir_info(path)
		return self.get_file_info(path)
		
	def safe_copy(self, src, dst):
		import shutil
		if os.path.isfile(src):
			try:
				shutil.copyfile(src, dst)
				shutil.copymode(src, dst)
				return True
			except:
				return False
		elif os.path.isdir(src):
			try:
				os.mkdir(dst)
			except:
				return False
			for f in os.listdir(src):
				new_src = os.path.join(src, f)
				new_dist = os.path.join(dst, f)
				if not self.safe_copy(new_src, new_dist):
					return False
		return True
	def run(self):
		self.validate_params()
		if self.can_execute:
			self.execute()
