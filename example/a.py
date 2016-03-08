def foo():
    return "bar"

## comment
# print(foo())
# print("#")



ml = """line 1
# line 2
line 3
"""

def strip_block(ml):
    return "<" + ml + ">"


print(strip_block(ml)) # representation = insprect


import re

# re.sub(pattern, repl, string, count=0, flags=0)
#
print(re.sub(r'^# ', r'', """line1
# comment1
## double comment
# comment2
line2
""",0,re.MULTILINE))
# line1
 # comment1
# ## double comment
# comment2
# line2


re.sub(r'^# ', r'', s,0,re.MULTILINE)

b = ("wahr" if 1 == 1
           else "falsch"
)
