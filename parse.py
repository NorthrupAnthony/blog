import sys, os, shutil

def die(msg):
	raise SystemExit(str(msg))

def process(contents):
	lines = contents.split("\n")
	linenum = [-1]
	def next():
		if linenum[0] + 1 >= len(lines):
			return ""
		linenum[0] += 1
		return lines[linenum[0]]
	def hasnext():
		return linenum[0] + 1 < len(lines)
	
	res = "{\n"
	headers = True
	while hasnext():
		line = next()
		if line == "":
			continue
		if headers:
			# Figure out the header stuffs
			if line == "### content":
				headers = False
				res += "\t\"content\": [\n"
				continue
			header = line[2:]
			if header == "breadcrumbs":
				breadcrumbs = list()
				while hasnext():
					breadcrumb = next()
					if breadcrumb == "":
						break
					breadcrumb = breadcrumb.split("|")
					breadcrumbs.append("[\"" + breadcrumb[1] + "\", \"" + breadcrumb[0] + "\"]")
				res += "\t\"breadcrumbs\": ["
				res += ", ".join(breadcrumbs)
				res += "],\n"
			elif header in ["breadcrumb", "title", "fname", "written"]:
				res += "\t\"" + header + "\": \""
				if hasnext():
					res += next()
				res += "\",\n"
			elif header in ["langs", "styles"]:
				parts = list()
				while hasnext():
					part = next()
					if part == "":
						break
					parts.append("\"" + part + "\"")
				res += "\t\""
				res += header
				res += "\": ["
				res += ", ".join(parts)
				res += "],\n"
		else:
			if line.startswith("```"):
				codes = list()
				while hasnext():
					code = next()
					if code == "```":
						break
					codes.append(code)
				res += "\t\t{\n\t\t\t\"type\": \"code\",\n\t\t\t\"lang\": \""
				res += line[4:]
				res += "\",\n\t\t\t\"content\": \"\"\""
				res += "\n".join(codes)
				res += "\"\"\"\n\t\t},\n"
			elif line == "$$": # TODO: Support for multiline
				maths = ""
				while hasnext():
					math = next()
					if math == "$$":
						break
					maths = math
				res += "\t\t{\n\t\t\t\"type\": \"math\",\n\t\t\t\"content\": \""
				res += maths
				res += "\"\n\t\t},\n"
			elif line == "***":
				chunks = list()
				while hasnext():
					chunk = next()
					if chunk == "***":
						break
					chunks.append(chunk)
				res += "\t\t{\n\t\t\t\"type\": \"chunk\",\n\t\t\t\"content\": \"\"\""
				res += "\n".join(chunks)
				res += "\"\"\"\n\t\t},\n"
			elif line.startswith(">>>"):
				alts = None
				while hasnext():
					alt = next()
					if alt == "<<<":
						break
					alts = alt
				res += "\t\t{\n\t\t\t\"type\": \"img\",\n\t\t\t\"src\": \""
				res += line[4:]
				res += "\",\n"
				res += "\t\t\t\"alt\": \""
				if alts:
					res += alts
				res += "\"\n"
				res += "\t\t},\n"
			else:
				# Inline stuffs
				nline = ""
				if hasnext():
					nline = next()
				if nline == "":
					res += "\t\t\"" + line + "\",\n"
				else:
					res += "\t\t[\n"
					parts = list()
					parts.append(line)
					parts.append(nline)
					while hasnext():
						part = next()
						if part == "":
							break
						parts.append(part)
					partnum = [-1]
					def inext():
						if partnum[0] + 1 >= len(parts):
							return ""
						partnum[0] += 1
						return parts[partnum[0]]
					def ihasnext():
						return partnum[0] + 1 < len(parts)
					while ihasnext():
						part = inext()
						if part.startswith("!") or part.startswith("?"):
							mode = "!" if part.startswith("!") else "?"
							texts = None
							while ihasnext():
								text = inext()
								if text == mode:
									break
								texts = text
							res += "\t\t\t{\n\t\t\t\t\"type\": \"link\",\n"
							if mode == "!":
								res += "\t\t\t\t\"target\": \"_blank\",\n"
							res += "\t\t\t\t\"href\": \""
							res += part[2:]
							res += "\",\n"
							res += "\t\t\t\t\"text\": \""
							if texts:
								res += texts
							res += "\"\n"
							res += "\t\t\t},\n"
						elif part.startswith("`"):
							codes = None
							while ihasnext():
								code = inext()
								if code == "`":
									break
								codes = code
							res += "\t\t\t{\n\t\t\t\t\"type\": \"code\",\n\t\t\t\t\"lang\": \""
							res += part[2:]
							res += "\",\n\t\t\t\t\"content\": \"\"\""
							if codes:
								res += codes
							res += "\"\"\"\n\t\t\t},\n"
						else:
							res += "\t\t\t\""
							res += part
							res += "\",\n"
					res += "\t\t],\n"
	if headers == False:
		res += "\t]\n"
	res += "}"
	return res

def parsefile(fname):
	contents = ""
	with open(fname, "r") as f:
		contents = f.read()
		f.close()
	result = process(contents)
	return result
def parsedir(fdir, tdir, clean=False, debug=False):
	if clean == True:
		print "[!] Cleared " + tdir
		shutil.rmtree(tdir)
	for (dirpath, dirnames, filenames) in os.walk(fdir):
		tdirpath = dirpath.replace(fdir, tdir)
		if not os.path.exists(tdirpath):
			os.makedirs(tdirpath)
		for filename in filenames:
			fname = dirpath + "\\" + filename
			tname = tdirpath + "\\" + filename
			if filename.endswith(".snippet"):
				tname = tname[:-8] + ".page"
				if debug == True:
					print "[-] Parsed: " + fname + " to " + tname
				parsed = parsefile(fname)
				with open(tname, "w+") as f:
					f.write(parsed)
					f.close()
			else:
				if debug == True:
					print "[-] Copied binary: " + fname + " to " + tname
				contents = b""
				with open(fname, "rb") as f:
					contents = f.read()
					f.close()
				with open(tname, "wb+") as f:
					f.write(contents)
					f.close()

def parse_main(cleanDir=False, debug=False):
	parsedir(".\\snippets", ".\\pages", clean=cleanDir, debug=debug)

if __name__ == "__main__":
	clean = False
	if "--clean" in sys.argv:
		clean = True
	parse_main(clean, True)