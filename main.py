import requests
import json
import codecs
import time
import sys, os
from googletrans import Translator
from bs4 import BeautifulSoup

with open('config.json', encoding="utf8") as file:
    setup_file = json.load(file)
	
class Ripper:

	def __init__(self):
		self.dump_data("nothing")
		self.toc = []
		self.seriesraw = setup_file["seriesData"]["seriesraw"]
		self.populate_toc()
		self.translator = GTranslator()
		print("\nRipper Class Running\n------------\nRaw Source: {}\nChapter Count: {}".format(self.seriesraw, len(self.toc)))
		
	def populate_toc(self):
		print("Populating Table of Contents [RAW]...")
		soup = self.download_ncode_page(self.seriesraw)
		tocLoc = soup.find('div', {"class": "index_box"})
		for chapterlink in tocLoc.find_all('a', href=True):
			self.toc.append(self.seriesraw + chapterlink['href'].split("/")[2])
			
	def download_ncode_page(self, url):
		headers = { "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36" }
		r = requests.get(url, headers=headers)
		soup = BeautifulSoup(r.text, 'lxml')
		return soup
		
	def rip_chapter(self,number):
		print("Ripping Chapter {}...".format(number))
		print(self.toc[number-1])
		soup = self.download_ncode_page(self.toc[number-1])
		print("RAW: " + self.toc[number-1])
		novelBody = soup.find('div', {"class":"novel_view"})
		novelLines = []
		chapterTitle = soup.find('p', {'class': 'novel_subtitle'}).get_text()
		for line in novelBody.find_all('p'):
			novelLines.append(line.get_text())
		count = 1
		try:
			translatedBody = self.bulk_translate(novelLines)
			#translatedBody = self.linebyline_translate(novelLines)
			chtitle = self.translator.translate_text(chapterTitle).text
		except:
			print("Failed. Terminating.")
			sys.exit()
			#chtitle = self.linebyline_dtranslate([chapterTitle])[0]
			#translatedBody = self.linebyline_dtranslate(novelLines)
		novelStr = "\n".join(translatedBody)
		return chtitle, novelStr
		
	def parse_existing_file(self, seriesslug, number):
		#check if slug folder exists
		if os.path.exists(seriesslug):
			if os.path.exists("{}/{}.txt".format(seriesslug, number)):
				body = []
				f = codecs.open("{}/{}.txt".format(seriesslug, number), encoding='utf-8')
				for line in f:
					body.append(line)
				chtitle = body[0]
				body.pop(0)
				return chtitle, "\n".join(body)
		return False, False
		#first line is title, the rest is body
		
	def bulk_translate(self, textarray):
		print("Bulk Translating...")
		translatedBody = self.translator.translate_text(textarray)
		print('Complete')
		outStrArray = []
		for item in translatedBody:
			outStrArray.append(item.text)
		return outStrArray
		
	def linebyline_translate(self, textarray):
		#self.dump_data(textarray)
		count = 1
		translatedBody = []
		for line in textarray:
			nLine = self.translator.translate_text(line).text
			translatedBody.append(nLine)
			print("Line {} of {} translated".format(count, len(textarray)))
			time.sleep(2)
			count+=1
		return translatedBody
		
	def dump_data(self,text):
		#f = codecs.open('dump.txt', mode="w", encoding="utf-8")
		with codecs.open('dump.txt', mode="w", encoding="utf-8") as f:
			if isinstance(text, (list, tuple)):
				f.write("\n".join(text))
			else:
				f.write(text)
		#f.close()
		print('dumped')
		input()
		
class GTranslator:

	def __init__(self):
		self.gtranslator = Translator()
		self.srclang = setup_file["seriesData"]["srclang"]
		self.outlang = "en"
		print("\nGTranslator Class Running\n------------\nSRCLANG: {}\nDESTLANG: {}".format(self.srclang, self.outlang))
		
	def translate_text(self, text):
		return self.gtranslator.translate(text, dest=self.outlang, src=self.srclang)
		
class Authenticator:
	
	def __init__(self):
		self.usernameStr = setup_file["wordpressAPI"]["username"]
		self.passwordStr = setup_file["wordpressAPI"]["password"]
		self.clientId = setup_file["wordpressAPI"]["clientId"]
		self.clientSecret = setup_file["wordpressAPI"]["clientSecret"]
		#self.redirectUri = setup_file["wordpressAPI"]["redirectUri"]
		self.AuthInUrl = "https://public-api.wordpress.com/oauth2/authorize"
		self.AuthTokenUrl = "https://public-api.wordpress.com/oauth2/token"
		#self.authorizeUrl = "{}?client_id={}&redirect_uri={}&response_type={}".format(self.AuthInUrl, self.clientId, self.redirectUri, "token")
		self.response = {}
		print("\nAuthenticator Class Running\n------------\nUser: {}\nPassword: {}\nClient ID: {}\nClient Secret: {}\n".format(self.usernameStr, self.passwordStr, self.clientId, self.clientSecret))
		
	def authorized(self):
		if self.check_if_auth():
			return True
		else:
			try:
				self.send_auth_request()
				return True
			except:
				return False
				
	def check_if_auth(self):
		if self.response == {}:
			return False
		r = requests.get("https://public-api.wordpress.com/rest/v1.1/me", headers=self.make_auth_header())
		if r.status_code == 200:
			return True
		return False
		
	def send_auth_request(self):
		clientData = {
			'client_id':str(self.clientId),
			'client_secret':self.clientSecret,
			'grant_type': 'password',
			'username':self.usernameStr,
			'password':self.passwordStr
		}
		r = requests.post(self.AuthTokenUrl, data=clientData)
		self.response = json.loads(r.content.decode("utf-8"))
		#print(self.response)
		
	def make_auth_header(self):
		return { 'Authorization': 'BEARER ' + self.response['access_token'] }
		
class WordPressAPI:

	def __init__(self):
		self.MyAuth = Authenticator()
		self.ripper = Ripper()
		self.apiUrl = "https://public-api.wordpress.com/rest/v1.1/sites/"
		self.homeUrl = setup_file["wordpressConfig"]["bloghome"]
		self.targetBlog = self.homeUrl[self.homeUrl.index("//")+2:]
		self.postsApiSlug = "/posts/new"
		self.parentApiSlug = '/posts/slug:'
		self.newpostApiSlug = '/posts/'
		self.seriesname = setup_file["seriesData"]["seriesname"].lower()
		self.serieshomeslug = setup_file["seriesData"]["seriesslug"]#self.seriesname.replace(" ", "-")
		self.parentPageID = None
		self.mostRecentChapter = None
		self.postUrl = '{}{}{}'.format(self.apiUrl, self.targetBlog, self.postsApiSlug)
		self.parentUrl = '{}{}{}{}'.format(self.apiUrl, self.targetBlog, self.parentApiSlug, self.serieshomeslug)
		self.editUrl = '{}{}{}'.format(self.apiUrl, self.targetBlog, self.newpostApiSlug)
		self.parse_series_page()
		print("\nWordpress Class Running\n------------\nBlog Base URL: {}\nBlog API Target: {}\nSeries Name: {}\nSeries Slug: {}\nBegin Parsing after Chapter {}".format(self.homeUrl, self.targetBlog, self.seriesname, self.serieshomeslug, self.mostRecentChapter))
		
	def create_a_page(self):
		print("Creating a page...")
		self.mostRecentChapter = self.mostRecentChapter + 1
		#rip chapter
		title, novelbody = self.ripper.parse_existing_file(self.serieshomeslug, self.mostRecentChapter)
		if not title:
			title, novelbody = self.ripper.rip_chapter(self.mostRecentChapter)
		templateNavigation = self.generate_navigation_wrapper()
		postTemplate = "{}\n{}\n{}\n{}".format(templateNavigation, self.generate_title_wrapper(title), novelbody, templateNavigation)
		postData = {
			'title': '{} Chapter {}'.format(self.seriesname.title(), self.mostRecentChapter),
			'content': postTemplate,
			'slug': '{}-{}'.format(self.serieshomeslug, self.mostRecentChapter),
			'parent': self.parentPageID,
			'type': 'page',
			'comment_status': 'open'
		}
		if self.MyAuth.authorized():
			r = requests.post(self.postUrl, headers=self.MyAuth.make_auth_header(), data=postData)
			self.create_a_post()
			self.update_series_page(title)
			print("Chapter {} added".format(self.mostRecentChapter))
			return True
		else:
			print("Failure to authenticate.")
			return False
		
	def create_a_post(self):
		print("Creating a post...")
		postData = {
			'title': '{} Chapter {}'.format(self.seriesname.title(), self.mostRecentChapter),
			'content': '<p><a href="{}/series/{}/{}">Link to chapter</a></p><p>Enjoy.</p>'.format(self.homeUrl,self.serieshomeslug, '{}-{}'.format(self.serieshomeslug, self.mostRecentChapter)),
			'slug': '{}-{}'.format(self.serieshomeslug,self.mostRecentChapter),
			'parent': self.parentPageID,
			'type': 'post'
		}
		if self.MyAuth.authorized():
			r = requests.post(self.postUrl, headers=self.MyAuth.make_auth_header(), data=postData)
			return True
		else:
			print("Failure to authenticate.")
			return False
			
	def parse_series_page(self):
		print("Parsing series page...")
		r = requests.get(self.parentUrl)
		vals = json.loads(r.content.decode("utf-8"))
		#print(vals['content'])
		soup = BeautifulSoup(vals['content'], "lxml")
		chapters = []
		for chapter in soup.find_all('a', href=True):
			chapters.append(chapter.get_text())
		if len(chapters)!=0:
			lastchapter = chapters[-1].split(" ")[1].strip()
		else:
			lastchapter = setup_file["seriesData"]["chapterstart"]-1
		self.mostRecentChapter = int(lastchapter)
		self.parentPageID = int(vals['ID'])
			
	def update_series_page(self, chaptertitle):
		print("Updating series page...")
		r = requests.get(self.parentUrl)
		vals = json.loads(r.content.decode("utf-8"))
		#print(vals['content'])
		newContent = vals['content']
		newContent+=('<p><a href="{}/{}/{}">Chapter {} - {}</a></p>'.format(self.homeUrl,self.serieshomeslug, '{}-{}'.format(self.serieshomeslug, self.mostRecentChapter), self.mostRecentChapter, chaptertitle))
		editData = {
			'content': newContent
		}
		r = requests.post(self.editUrl + str(vals['ID']), headers=self.MyAuth.make_auth_header(), data=editData)
		
	def generate_title_wrapper(self, text):
		return '<h2 style="text-align: center;">{}</h2>'.format(text.title())
		
	def generate_navigation_wrapper(self):
		seriesSlug = self.serieshomeslug
		indexSlug = self.homeUrl + "/series/" + self.serieshomeslug
		if self.mostRecentChapter > 1:
			templateStr = '<p style="text-align: center;"><a href="{}">Prev</a> - <a href="{}">Index</a> - <a href="{}">Next</a></p>'.format(indexSlug + "/" + seriesSlug + "-" + str(self.mostRecentChapter-1), indexSlug, indexSlug + "/" + seriesSlug + "-" + str(self.mostRecentChapter+1))
		else:
			templateStr = '<p style="text-align: center;">Prev - <a href="{}">Index</a> - <a href="{}">Next</a></p>'.format(self.homeUrl + "/" + self.serieshomeslug, seriesSlug + str(self.mostRecentChapter+1))
		return templateStr
		
def main():
	looper = True
	myBlog = WordPressAPI()
	while looper:
		if myBlog.create_a_page():
			print("Post created successfully.")
		else:
			print("Post failed.")
			sys.exit()
		print("Waiting half a day before executing again...")
		time.sleep(43200)
	
if __name__=="__main__":
	main()