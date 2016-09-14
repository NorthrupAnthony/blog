import sys
from parse import *
from render import *

if __name__ == "__main__":
	clearDist = False
	forceRender = False
	if "--clean" in sys.argv:
		clearDist = True
		forceRender = True
	elif "--force" in sys.argv:
		forceRender = True
	parse_main(clearDist, clearDist)
	render_main(clearDist, forceRender)