import os, ast, sys, json, hashlib, shutil
from codesnippets import *
from collections import deque

def die(msg):
	raise SystemExit(str(msg))

# Main state of the program
class App:
	# Initialize state
	def __init__(self):
		# Header links
		self.nav_links = [["/index", "Home"], ["/about", "About"], ["/contact", "Contact"]]
		
		# Folder locations
		self.dist_path = "./docs"
		self.src_path = "./src"
		
		# Faster compiling
		self.memory = dict()
		
		# Rendering
		self.active_file = None
		self.lookup = deque()
		self.lookat = set()
		self.require("/index")
		
		# Content processing
		self.lines = list()
		self.linenum = 0
	
	# Get resource path relative to app
	def file_name(self, folder, pname, ext):
		fname = pname
		# Only give extension to un-typed files
		if "." not in fname:
			fname = fname + "." + ext
		if "/" not in fname:
			fname = "/" + fname
		return folder + fname
	def dist_page_name(self, pname):
		# Default output file type: html
		return self.file_name(self.dist_path, pname, "html")
	def src_page_name(self, pname):
		# Default input file type: snippet
		return self.file_name(self.src_path, pname, "snippet")
	
	# File IO
	def get(self, fname, binary=False):
		mode = "r"
		if binary == True:
			mode = "rb"
		res = ""
		if os.path.isfile(fname):
			with open(fname, mode) as f:
				res = f.read()
				f.close()
		return res
	def put(self, fname, content, binary=False):
		mode = "w+"
		if binary == True:
			mode = "wb+"
		with open(fname, mode) as f:
			f.write(content)
			f.close()
	
	# Hashing
	def hashed(self, payload):
		m = hashlib.md5()
		m.update(str(payload))
		return m.hexdigest()
	
	# Public memory control
	def memory_load(self, fname):
		self.memory_clear()
		if os.path.isfile(fname):
			with open(fname, "r") as f:
				self.memory = json.load(f)
			return True
		return False
	def memory_save(self, fname):
		with open(fname, "w+") as f:
			json.dump(self.memory, f, indent=4)
	def memory_clear(self):
		self.memory = dict()
	
	# Add resource to app
	def require(self, fname):
		# Attach to active file as link
		if self.active_file:
			links = self.memory[self.active_file]["links"]
			if fname not in links:
				links.append(fname)
		if fname not in self.lookat:
			self.lookup.append(fname)
			self.lookat.add(fname)
			return True
		return False
	
	# Polling
	def hasnext(self):
		return len(self.lookup) > 0
	def next(self):
		res = self.lookup.popleft()
		return res
	
	# Check if up-to-date
	def check_rendered(self, fname, contents):
		hash = self.hashed(contents)
		if fname in self.memory:
			if hash == self.memory[fname]["hash"]:
				for link in self.memory[fname]["links"]:
					self.require(link)
				return True
		return False
	
	# Attaching active file
	def start_rendering(self, fname, contents):
		self.active_file = fname
		self.memory[fname] = {
			"hash": self.hashed(contents),
			"links": []
		}
	def stop_rendering(self, fname):
		self.active_file = None
	
	# Path processing
	def path_route(self, fname, tname):
		# Don't handle external resource
		if "//" in tname:
			return tname
		# Require any local links
		self.require(tname)
		# Used in live page, append default file-type
		if "." not in tname:
			tname = tname + ".html"
		res = os.path.relpath(os.path.dirname(tname), os.path.dirname(fname)) + "/" + os.path.basename(tname)
		return res
		
	
	# Content processing
	def set_content(self, content):
		self.lines = content.split("\n")
		self.linenum = 0
	def line_hasnext(self):
		return self.linenum < len(self.lines)
	def line_next(self):
		res = self.lines[self.linenum]
		self.linenum = self.linenum + 1
		return res
	
	# Render the file
	def render_headers(self, fname, header):
		# Head
		res = "" + snippet_head
		
		# Title
		if "title" in header:
			res = res + header["title"]
		res = res + snippet_title
		
		# Default style
		res = res + snippet_style_head
		res = res + self.path_route(fname, "/css/styles.css")
		res = res + snippet_style_tail
		
		# Dynamic styles
		if "styles" in header:
			for sname in header["styles"]:
				res = res + snippet_style_head
				res = res + self.path_route(fname, sname)
				res = res + snippet_style_tail
		
		# Languages
		res = res + snippet_script
		if "langs" in header:
			for lang in header["langs"]:
				res = res + snippet_lang_head
				res = res + lang
				res = res + snippet_lang_tail
		
		# Nav bar
		res = res + snippet_middle
		res = res + self.path_route(fname, "/index")
		res = res + snippet_middle_title
		
		# Nav links
		for nav_link in self.nav_links:
			res = res + snippet_middle_nav_link_head
			res = res + self.path_route(fname, nav_link[0])
			res = res + snippet_middle_nav_link_middle
			res = res + nav_link[1]
			res = res + snippet_middle_nav_link_tail
		res = res + snippet_middle_nav_tail
		
		# Breadcrumbs
		if "breadcrumbs" in header:
			for breadcrumb in header["breadcrumbs"]:
				res = res + snippet_breadcrumb_link_head
				res = res + self.path_route(fname, breadcrumb[0])
				res = res + snippet_breadcrumb_link_middle
				res = res + breadcrumb[1]
				res = res + snippet_breadcrumb_link_tail
		
		# Current page breadcrumb
		res = res + snippet_breadcrumb_active_head
		if "breadcrumb" in header:
			res = res + header["breadcrumb"]
		elif "title" in header:
			res = res + header["title"]
		res = res + snippet_breadcrumb_active_tail
		
		# Page title
		res = res + snippet_article_head
		if "title" in header:
			res = res + header["title"]
		
		# Date written
		res = res + snippet_article_middle
		if "written" in header:
			res = res + header["written"]
		
		# End
		res = res + snippet_article_body_head
		
		# Return
		return res
	def render_body(self, fname):
		# Result
		res = ""
		
		# Process
		while self.line_hasnext():
			line = self.line_next()
			if line == "":
				continue
			
			# Handle various block elements
			if line.startswith("```"): # Code
				codes = list()
				while self.line_hasnext():
					code = self.line_next()
					if code == "```": # Code terminator
						break
					codes.append(code)
				res = res + snippet_tags["code"][0]
				res = res + line[4:] # lang
				res = res + snippet_tags["code"][1]
				res = res + "\n".join(codes) # content
				res = res + snippet_tags["code"][2]
			elif line == "$$": # Math
				maths = list()
				while self.line_hasnext():
					math = self.line_next()
					if math == "$$": # Math terminator
						break
					maths.append(math)
				if len(maths) <= 1: # Single line
					res = res + snippet_tags["math"][0]
					if len(maths) > 0:
						res = res + maths[0] # content
					res = res + snippet_tags["math"][1]
				else: # Multiline
					res = res + snippet_tags["math"][2]
					res = res + snippet_tags["math"][3].join(maths) # content
					res = res + snippet_tags["math"][4]
			elif line == "***": # Chunk
				chunks = list()
				while self.line_hasnext():
					chunk = self.line_next()
					if chunk == "***": # Chunk terminator
						break
					chunks.append(chunk)
				res = res + snippet_tags["chunk"][0]
				if len(chunks) > 0:
					res = res + snippet_tags["chunk"][1]
					res = res + snippet_tags["chunk"][1].join(chunks) # content
				res = res + snippet_tags["chunk"][2]
			elif line.startswith(">>>"): # Image
				alts = None
				while self.line_hasnext():
					alt = self.line_next()
					if alt == "<<<": # Image terminator
						break
					alts = alt
				res = res + snippet_tags["img"][0]
				res = res + self.path_route(fname, line[4:]) # src
				res = res + snippet_tags["img"][1]
				if alt:
					res = res + alts # alt
				res = res + snippet_tags["img"][2]
			else: # P tag
				nline = ""
				if self.line_hasnext():
					nline = self.line_next()
				if nline == "": # Simple p tag
					res = res + snippet_tags["text"][0]
					res = res + line
					res = res + snippet_tags["text"][1]
					continue
					
				# Cache lines
				lines = deque()
				lines.append(line)
				lines.append(nline)
				while self.line_hasnext():
					line = self.line_next()
					if line == "":
						break
					lines.append(line)
				def ihasnext():
					return len(lines) > 0
				def inext():
					return lines.popleft()
				
				# Process lines
				res = res + snippet_tags["text"][0]
				while ihasnext():
					part = inext()
					if part.startswith("!") or part.startswith("?"): # Link
						mode = "!" if part.startswith("!") else "?"
						texts = None
						while ihasnext():
							text = inext()
							if text == mode: # Link termination
								break
							texts = text
						res = res + snippet_elements["link"][0]
						if mode == "!":
							res = res + "_blank" # target
						else:
							res = res + "_self" # target
						res = res + snippet_elements["link"][1]
						res = res + self.path_route(fname, part[2:]) # href
						res = res + snippet_elements["link"][2]
						if texts:
							res = res + texts # text
						res = res + snippet_elements["link"][3]
					elif part.startswith("`"): # Inline Code
						codes = None
						while ihasnext():
							code = inext()
							if code == "`": # Inline Code termination
								break
							codes = code
						res = res + snippet_elements["code"][0]
						res = res + part[2:] # lang
						res = res + snippet_elements["code"][1]
						if codes:
							res = res + codes # content
						res = res + snippet_elements["code"][2]
					else: # Normal text
						res = res + part
				res = res + snippet_tags["text"][1]
		
		# Return
		return res
	def render_snippet(self, fname, content):
		# Put content in memory
		self.set_content(content)
		
		# Result
		res = ""
		
		# Parse headers
		isheader = True
		headers = dict()
		while isheader == True and self.line_hasnext():
			# Get next line
			line = self.line_next()
			
			# Ignore blank lines
			if line == "":
				continue
			
			# Headers terminator string
			if line == "### content":
				isheader = False
				break
			
			# Process current header
			header = None
			data = None
			
			# Is valid header name
			if line.startswith("# "):
				header = line[2:]
			else:
				continue
			
			# Handle valid header types
			if header == "breadcrumbs":
				data = list()
				while self.line_hasnext():
					part = self.line_next()
					if part == "":
						break
					part = part.split("|")
					if len(part) == 2:
						data.append([part[1], part[0]])
			elif header in ["breadcrumb", "title", "fname", "written"]:
				while self.line_hasnext():
					line = self.line_next()
					if line == "":
						break
					data = line
			elif header in ["langs", "styles"]:
				data = list()
				while self.line_hasnext():
					part = self.line_next()
					if part == "":
						break
					data.append(part)
			
			# Store current header, if valid
			if data:
				headers[header] = data
		
		# Process headers
		res = res + self.render_headers(fname, headers)
		
		# Body
		if isheader == False and self.line_hasnext():
			res = res + self.render_body(fname)
		
		# Footer
		res = res + snippet_tail
		
		# Return
		return res

# Running the program
def make_main(clearDist=False, forceRender=False):
	# Load state
	app = App()
	app.memory_load("memory.json")
	
	# Handle running options
	if clearDist == True:
		print "[!] Clearing dist folder"
		if os.path.exists(app.dist_path):
			shutil.rmtree(app.dist_path)
		print "[!] Dist folder cleared"
		app.memory_clear()
		print "[!] Cleared render cache"
	if forceRender == True:
		print "[!] Rendering all documents"
	
	# Process
	render_count = 0
	while app.hasnext():
		# Get next page name
		pname = app.next()
		
		# Get from/to actual file names
		fname = app.src_page_name(pname)
		tname = app.dist_page_name(pname)
		
		# Verify file exists
		if not os.path.isfile(fname):
			print "[!] Does not exist: " + fname
			continue
		
		# Load contents
		issnippet = fname.endswith(".snippet")
		contents = app.get(fname, (not issnippet))
		
		# Render
		render = True
		if app.check_rendered(pname, contents):
			render = False
		
		# Ensure dirs
		tdir = os.path.dirname(tname)
		if not os.path.exists(tdir):
			os.makedirs(tdir)
		
		# Render
		if forceRender == True or render == True:
			render_count = render_count + 1
			
			# Active file
			app.start_rendering(pname, contents)
			
			# Log
			print "[-] Rendering " + pname
			
			# Process if snippet
			res = contents
			if issnippet:
				res = "<!-- Rendered from " + fname + " -->\n" + app.render_snippet(pname, contents)
			
			# Write to output file
			app.put(tname, res, (not issnippet))
			
			# No longer active
			app.stop_rendering(pname)
	
	# Done
	if render_count == 0:
		print "[-] No files rendered"
	elif render_count == 1:
		print "[-] Successfully rendered 1 file"
	else:
		print "[-] Successfully rendered " + str(render_count) + " files"
	
	# Save state
	app.memory_save("memory.json")

if __name__ == "__main__":
	clearDist = False
	forceRender = False
	if "--clean" in sys.argv:
		clearDist = True
		forceRender = True
	elif "--force" in sys.argv:
		forceRender = True
	make_main(clearDist, forceRender)