# Python prototype source for demo.html
page = {
  breadcrumbs: [["Home", "/index.html"], ["Test", "/Test/index.html"]],
  title: "Current",
  fname: "/Test/demo.html"
  written: "09/02/2016",
  content: [
    "This is a test article... No real purpose, just trying to get some formatting working properly. Still though, it's pretty awesome I guess.",
    "The spacing is also pretty good between paragraphs.",
    "Blah blah blah. Now onto some content.",
    {
      type: "code",
      lang: "python",
      content: """# Python
# filename: foo.py
def foo():
    print "Hello, World!"

foo()"""
    },
    "And now there's syntax highlighting!",
    {
      type: "code",
      lang: "ada",
      content: """-- Ada
-- filename: foo.adb
with Ada.Text_IO;
use Ada.Text_IO;
procedure foo is
begin
    Put_Line("Hello, World!");
end;"""
    },
    "Including other languages.",
    "Not sure what else needs to work... How about some latex math?",
    "Does \( x^2 \) work? Cool. Now does display mode work?", # Inline math can just be written in
    {
      type: "math",
      content: "x = \frac{-b \pm \sqrt{b^2 - 4 a c}}{2 a}"
    },
    "Neat. The spacing is a little off from what I'd like but it certainly works. Woo.",
    "Oh yeah, still need a footer.",
    "Almost forgot... Lipsum incoming",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum ac leo molestie, accumsan massa ac, consequat nibh. Vivamus tristique feugiat tellus, ut vehicula lacus blandit sed. Integer convallis sit amet orci id elementum. Vestibulum eu libero sit amet nunc posuere aliquam. Fusce sit amet ultrices enim. Ut ut viverra nisi. Morbi dignissim nunc non fringilla condimentum. Mauris maximus molestie fermentum. In quis facilisis massa. Aliquam vitae est vel massa porta egestas nec nec quam.",
    [
      "And of course we need some pics here and there.",
      {
        type: "link",
        target: "_blank",
        href: "http://lorempixel.com",
        text: "Lorempixel"
      },
      "to the rescue."
    ],
    {
      type: "img",
      src: "http://lorempixel.com/640/480/abstract/1/",
      alt: "Some Cool Picture"
    },
    {
      type: "chunk",
      content: "Not sure what to have here, just a placeholder really."
    }
  ]
}