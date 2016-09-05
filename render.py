import os, ast, sys, json, hashlib, shutil
from codesnippets import *
from collections import deque

nav_links = [["/index", "Home"], ["/about", "About"], ["/contact", "Contact"]]
def file_name(folder, pname, ext):
	fname = pname
	if "." not in fname:
		fname = fname + "." + ext
	if "/" not in fname:
		fname = "/" + fname
	return folder + fname
def dist_page_name(pname):
	return file_name("docs", pname, "html")
def source_page_name(pname):
	return file_name("src", pname, "page")

def get(fname):
	res = ""
	with open(fname, 'r') as f:
		res = f.read()
	return res
def load_contents(contents):
	return ast.literal_eval(contents)
def load(fname):
	return load_contents(get(fname))

def hashed(msg):
	msg = str(msg)
	m = hashlib.md5()
	m.update(msg)
	return m.hexdigest()

class Logic:
	def __init__(self, mname, arr):
		self.memory_file = mname
		self.memory = dict()
		with open(mname, "r") as f:
			self.memory = json.load(f)
		self.file_name = ""
		self.lookup = deque()
		self.lookat = set()
		for item in arr:
			self.require(item)
	
	def require(self, page_name):
		if self.file_name != "":
			if page_name not in self.memory[self.file_name]["links"]:
				self.memory[self.file_name]["links"].append(page_name)
		if page_name not in self.lookat:
			self.lookup.append(page_name)
			self.lookat.add(page_name)
			return True
		return False
	
	def hasNext(self):
		return len(self.lookup) > 0
	
	def next(self):
		res = self.lookup.popleft()
		return res
	
	def stop(self):
		with open(self.memory_file, "w+") as f:
			json.dump(self.memory, f, indent=4)
	
	def checkRendered(self, page_name, pcontents):
		res = False
		phash = hashed(pcontents)
		if page_name in self.memory:
			if "hash" in self.memory[page_name]:
				if self.memory[page_name]["hash"] == phash:
					for link in self.memory[page_name]["links"]:
						self.require(link)
					res = True
		return res
	
	def rendering(self, page_name):
		self.file_name = page_name
		if page_name not in self.memory:
			self.memory[page_name] = {
				"hash": "",
				"links": []
			}
		else:
			self.memory[page_name]["links"] = []
	
	def doneRendering(self, page_name, pcontents):
		phash = hashed(pcontents)
		self.memory[page_name]["hash"] = hashed(pcontents)
		self.file_name = ""

def path_parse(fname):
	res = []
	l = len(fname)
	c = "root"
	for i in range(0, l):
		if fname[i] == "/":
			res.append(c)
			c = ""
		else:
			c += fname[i]
	res.append(c)
	return res
def path_route(logic, fname, tname):
	if "//" in tname:
		return tname
	logic.require(tname)
	if "." not in tname:
		tname = tname + ".html"
	fdir = path_parse(fname)[:-1]
	flen = len(fdir)
	tdir = path_parse(tname)
	tfile = tdir[-1]
	tdir = tdir[:-1]
	tlen = len(tdir)
	res = ""
	level = 0
	while level < flen and level < tlen and fdir[level] == tdir[level]:
		level = level + 1
	if level == flen:
		res = "./"
	else:
		res = "../" * (flen - level)
	while level < tlen:
		res += tdir[level] + "/"
		level = level + 1
	res += tfile
	return res

def parse(logic, fname, body):
	res = ""
	for item in body:
		if type(item) is str:
			# Basic <p> tag
			res = res + snippet_tags["text"][0]
			res = res + item
			res = res + snippet_tags["text"][1]
		elif type(item) is list:
			# Complex <p> tag
			res = res + snippet_tags["text"][0]
			for subitem in item:
				if type(subitem) is str:
					res = res + subitem
				elif type(subitem) is dict:
					if "type" not in subitem:
						continue
					if subitem["type"] == "link":
						res = res + snippet_tags["link"][0]
						if "target" in subitem:
							res = res + subitem["target"]
						res = res + snippet_tags["link"][1]
						if "href" in subitem:
							res = res + path_route(logic, fname, subitem["href"])
						res = res + snippet_tags["link"][2]
						if "text" in subitem:
							res = res + subitem["text"]
						res = res + snippet_tags["link"][3]
					elif subitem["type"] == "text":
						if "text" in subitem:
							res = res + subitem["text"]
			res = res + snippet_tags["text"][1]
		elif type(item) is dict:
			# Custom tag
			if "type" not in item:
				continue
			if item["type"] == "text":
				res = res + snippet_tags["text"][0]
				if "text" in item:
					res = res + item["text"]
				res = res + snippet_tags["text"][1]
			elif item["type"] == "chunk":
				res = res + snippet_tags["chunk"][0]
				if "content" in item:
					res = res + snippet_tags["chunk"][1]
					res = res + item["content"].replace("\n", snippet_tags["chunk"][1])
				res = res + snippet_tags["chunk"][2]
			elif item["type"] == "math":
				res = res + snippet_tags["math"][0]
				if "content" in item:
					res = res + item["content"]
				res = res + snippet_tags["math"][1]
			elif item["type"] == "img":
				res = res + snippet_tags["img"][0]
				if "src" in item:
					res = res + item["src"]
				res = res + snippet_tags["img"][1]
				if "alt" in item:
					res = res + item["alt"]
				res = res + snippet_tags["img"][2]
			elif item["type"] == "code":
				res = res + snippet_tags["code"][0]
				if "lang" in item:
					res = res + item["lang"]
				res = res + snippet_tags["code"][1]
				if "content" in item:
					res = res + item["content"]
				res = res + snippet_tags["code"][2]
	return res

def parse_file(logic, file_name, file_contents):
	data = load_contents(file_contents)
	fname = "/index"
	if "fname" in data:
		fname = data["fname"]
	res = "<!-- Parsed from " + file_name + " -->\n"
	res = res + snippet_head
	if "title" in data:
		res = res + data["title"]
	res = res + snippet_title
	res = res + snippet_style_head
	res = res + path_route(logic, fname, "/css/styles.css")
	res = res + snippet_style_tail
	if "styles" in data:
		for sname in data["styles"]:
			res = res + snippet_style_head
			res = res + path_route(logic, fname, sname)
			res = res + snippet_style_tail
	res = res + snippet_script
	if "langs" in data:
		for lang in data["langs"]:
			res = res + snippet_lang_head
			res = res + lang
			res = res + snippet_lang_tail
	res = res + snippet_middle
	res = res + path_route(logic, fname, "/index")
	res = res + snippet_middle_title
	for nav_link in nav_links:
		res = res + snippet_middle_nav_link_head
		res = res + path_route(logic, fname, nav_link[0])
		res = res + snippet_middle_nav_link_middle
		res = res + nav_link[1]
		res = res + snippet_middle_nav_link_tail
	res = res + snippet_middle_nav_tail
	if "breadcrumbs" in data:
		for breadcrumb in data["breadcrumbs"]:
			res = res + snippet_breadcrumb_link_head
			res = res + path_route(logic, fname, breadcrumb[0])
			res = res + snippet_breadcrumb_link_middle
			res = res + breadcrumb[1]
			res = res + snippet_breadcrumb_link_tail
	res = res + snippet_breadcrumb_active_head
	if "title" in data:
		res = res + data["title"]
	res = res + snippet_breadcrumb_active_tail
	res = res + snippet_article_head
	if "title" in data:
		res = res + data["title"]
	res = res + snippet_article_middle
	if "written" in data:
		res = res + data["written"]
	res = res + snippet_article_body_head
	if "content" in data:
		res = res + parse(logic, fname, data["content"])
	res = res + snippet_tail
	return res

def main():
	clearDist = False
	forceRender = False
	if "--clean" in sys.argv:
		clearDist = True
		forceRender = True
		print "[!] Clearing dist folder"
		print "[!] Rendering all documents"
	elif "--force" in sys.argv:
		forceRender = True
		print "[!] Rendering all documents"
	
	if clearDist == True:
		shutil.rmtree("docs")
		print "[!] Dist folder cleared"
	
	logic = Logic("memory.json", ["/index"])
	found = False
	while logic.hasNext():
		page_name = logic.next()
		pname = source_page_name(page_name)
		fname = dist_page_name(page_name)
		if not os.path.isfile(pname):
			print "[!] Does Not Exist: " + pname
			continue
		pcontents = get(pname)
		render = True
		if logic.checkRendered(page_name, pcontents):
			render = False
		fdir = os.path.dirname(fname)
		if not os.path.exists(fdir):
			render = True
			os.makedirs(fdir)
			open(fname, 'a').close()
		if forceRender == True or render == True:
			found = True
			print "[-] Rendering: " + page_name
			logic.rendering(page_name)
			with open(fname, "w+") as f:
				if ".page" in pname:
					f.writelines(parse_file(logic, pname, pcontents))
				else:
					f.writelines(pcontents)
			logic.doneRendering(page_name, pcontents)
	logic.stop()
	if found == False:
		print "[-] Nothing to render, all up to date"

if __name__ == "__main__":
	main()