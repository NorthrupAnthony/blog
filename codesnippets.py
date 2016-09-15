snippet_head = """<!DOCTYPE html>
<head>
	<title>"""
snippet_title = """</title>"""
snippet_style_head = """
	<link rel="stylesheet" type="text/css" href=\""""
snippet_style_tail = """\" />"""
snippet_script = """
	
	<!-- Highlight.js -->
	<!-- Download more languages: https://cdnjs.com/libraries/highlight.js/9.6.0 -->
	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.6.0/styles/default.min.css" />
	<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.6.0/highlight.min.js"></script>"""

snippet_lang_head = """
	<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.6.0/languages/"""
snippet_lang_tail = """.min.js"></script>"""

snippet_middle = """
	<script>
		hljs.configure({ tabReplace: "    " })
		hljs.initHighlightingOnLoad();
		window.addEventListener("load", function() {
			var els = document.getElementsByClassName("hljs-inline");
			for(var i in els) {
				hljs.highlightBlock(els[i]);
			}
		});
	</script>
	
	<!-- MathJax -->
	<script type="text/javascript" src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-MML-AM_CHTML"></script>
	<script type="text/x-mathjax-config">
		MathJax.Hub.Config({
			tex2jax: {inlineMath: [ ['$','$'], ['\\\\(','\\\\)'] ]},
			showMathMenu: false,
			showMathMenuMSIE: false,
			menuSettings: {zoom: "Click"},
			MathZoom: {styles: {"#MathJax_Zoom": {"color": "black !important", "border-radius": "20px"}}},
			errorSettings: {message: ["span", {"class": "MathJax--error"}, "Could not parse equation"]}
		});
	</script>
</head>
<body>
	<div class="header">
		<div class="nav">
			<div class="title"><a href=\""""
snippet_middle_title = """\">Anthony Northrup's Blog</a></div>
			<ul class="links">
				<li class="highlight">Pages:</li>"""
snippet_middle_nav_link_head = """
				<li><a class="nav--link" href=\""""
snippet_middle_nav_link_middle = """\">"""
snippet_middle_nav_link_tail = """</a></li>"""
snippet_middle_nav_tail = """
				<li class="clearfix"></li>
			</ul>
			<div class="clearfix"></div>
		</div>
	</div>
	<div class="content">
		<div class="breadcrumbs">
			<span class="highlight">Navigation:</span>"""

snippet_breadcrumb_link_head = """
			<a class="breadcrumb--link" href=\""""
snippet_breadcrumb_link_middle = """\">"""
snippet_breadcrumb_link_tail = """</a>
			/"""
snippet_breadcrumb_active_head = """
			<span class="breadcrumb--current">"""
snippet_breadcrumb_active_tail = """</span>"""

snippet_article_head = """
		</div>
		<div class="article">
			<div class="heading">
				<div class="title">"""
snippet_article_middle = """</div>
				<div class="info">
					<span class="highlight">Written:</span>
					<span class="date">"""
snippet_article_body_head = """</span>
				</div>
				<div class="clearfix"></div>
			</div>
			<div class="body">"""
snippet_tail = """
			</div>
		</div>
	</div>
	<div class="footer">
		Made by Anthony Northrup &copy; 2016
	</div>
</body>"""

snippet_tags = {
	"text": [
		"""
				<p>""",
		"""</p>"""
	],
	"code": [
		"""
				<pre><code class="lang-""",
		"""\">""",
		"""</code></pre>"""
	],
	"math": [
		"""
				$$ """,
		""" $$""",
		"""
				$$
					""",
		"""
					""",
		"""
				$$"""
	],
	"img": [
		"""
				<img src=\"""",
		"""\" alt=\"""",
		"""\" />"""
	],
	"chunk": [
		"""
				<div class="chunk">""",
		"""
					""",
		"""
				</div>"""
	]
}

snippet_elements = {
	"link": [
		"""<a target=\"""",
		"""\" href=\"""",
		"""\">""",
		"""</a>"""
	],
	"code": [
		"""<code class="lang-""",
		""" hljs-inline">""",
		"""</code>"""
	]
}