
# Run peforth from the source directory without pip install in prior
# for debugging or developping.
#
# Example command line:
#   c:\Users\hcche\Documents\GitHub\peforth\peforth>python test.py    
#
# Although You can run:
#   c:\Users\hcche\Documents\GitHub\peforth\peforth>python __main__.py    
# But it 'import peforth' so you are still running the pip'ed package not 
# the source. 

if __name__ == '__main__':
    exec(open("__init__.py", encoding="utf-8").read())  # this is like: include __init__.py 
    ok(cmd ="\n")
