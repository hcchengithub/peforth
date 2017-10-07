# peforth

### A programmable python debugger. Set one breakpoint to x-ray everything.

There are many ways to run peforth:

1. In the project folder 
   run ```python __main__.py``` or ```python __init__.py``` or double click them.
   
2. From above the project folder run ```python peforth```

3. If the peforth package is installed. At any folder, run ```python -m peforth```

4. If the peforth package is installed. At any folder, run ```python``` 
   then ```import peforth``` then type ```peforth.ok()``` to run it, type ```exit``` 
   to come back to python interpreter, and do it again and again. peforth context 
   will be all of the same session for all runs.

# Install peforth as a package:

Use the pip install:

    pip install peforth 

If you were participating the development of peforth project or if you were playing 
with it with 
your experiments, after once installed, you can run setup.bat at the project root 
directory to update your new code into the peforth module so ```import peforth```
will get your latest code. 

# Hello World! 

All peforth words have their help messages.

    : hi  ( -- ) // The hello world! command
        ." Hello World!!" cr ;
        /// if help message is not enough then use /// leading lines to add comments.
        /// Both // and /// leading messages go to the last word.

The first stack diagram and the // leading comment line become help messages.

    OK hi
    Hello World!!
    OK help hi
    ( -- ) The hello world! command
        if help message is not enough then use /// leading lines to add comments.
        Both // and /// leading messages go to the last word.

'see' command to see a word's source code and attributes.

    OK see hi
    {
        "__class__": "Word",
        "__module__": "peforth.projectk",
        "name": "hi",
        "xt": {
            "__class__": "function",
            "__module__": "peforth.projectk"
        },
        "immediate": false,
        "help": "( -- ) The hello world! command",
        "comment": "\tif help message is not enough then use /// leading lines to add comments.\n\tBoth // and /// leading messages goes to the last word.\n",
        "vid": "forth",
        "wid": 242,
        "type": "colon",
        "private": false,
        "cfa": 717
    }
    ------------ Definition in dictionary ------------
    00717: Literal: Hello World!! <class 'str'>
    00718: . ( x -- ) Print the TOS __str__  (<class 'peforth.projectk.Word'>)
    00719: cr ( -- ) print a carriage return __str__  (<class 'peforth.projectk.Word'>)
    00720: RET  (<class 'NoneType'>)
    ------------ End of the difinition ---------------
    OK

# code ... end-code 

peforth like eforth attempts to use very basic words to build the entire forth system. Actually, peforth is started with only two words 'code' and 'end-code'. 

To define a code word, we press Ctrl-D to make the Windows DOS-Box CLI to accept multiple lines at once then type in the example and at the end drop another Ctrl-D to terminate the multiple-line input.

    OK ^D
    code hello
        print('hello world!\n')
    end-code
    ^D
    OK hello
    hello world!

    OK see hello
    {
        "__class__": "Word",
        "__module__": "peforth.projectk",
        "name": "hello",
        "xt": {
            "__class__": "function",
            "__module__": "peforth.projectk",
            "name": "hello"
        },
        "immediate": false,
        "help": "",
        "comment": "",
        "vid": "forth",
        "wid": 243,
        "type": "code"
    }
    ------------ Source code ------------
    def xt(_me=None): ### hello ###
        print('hello world!\n')

    -------------------------------------
    OK

Where _me refers to the forth word object itself if you need to access its own attributes.

# inline python code \<py> \</py> \</pyV> py: py>  

python code can be put inline mixed with forth code. This example brings you the 
python ```help()``` utility:

    OK py: help()

    Welcome to Python 3.6's help utility!

    If this is your first time using Python, you should definitely check out
    the tutorial on the Internet at http://docs.python.org/3.6/tutorial/.

    Enter the name of any module, keyword, or topic to get help on writing
    Python programs and using Python modules.  To quit this help utility and
    return to the interpreter, just type "quit".

    To get a list of available modules, keywords, symbols, or topics, type
    "modules", "keywords", "symbols", or "topics".  Each module also comes
    with a one-line summary of what it does; to list the modules whose name
    or summary contain a given string such as "spam", type "modules spam".

    help> quit

    You are now leaving help and returning to the Python interpreter.
    If you want to ask for help on a particular object directly from the
    interpreter, you can type "help(object)".  Executing "help('string')"
    has the same effect as typing a particular string at the help> prompt.
    OK

This example defines a 'dos-dir' command to go out to DOS box, run the 'dir' DOS command, and come back.

    OK : dos-dir <py> import os; os.system('dir') </py> ;
    OK dos-dir
     Volume in drive C is Windows
     Volume Serial Number is 2EA4-3202

     Directory of c:\Users\hcche\Documents\GitHub\ML\machine-learning-recipes\src\part_5

    2017-09-03  16:09    <DIR>          .
    2017-09-03  16:09    <DIR>          ..
    2017-06-11  08:53               240 check.py
    2017-06-23  17:00    <DIR>          Datasets
    2017-06-11  08:53             2,218 Fisher.csv
    2017-09-03  17:41             6,912 kNNClassifier.f
    2017-09-01  19:45             2,256 kNNClassifier.py
    2017-06-11  08:53             2,079 Part5.py
    2017-09-03  16:09    <DIR>          __pycache__
                   5 File(s)         13,705 bytes
                   4 Dir(s)  262,004,789,248 bytes free
    OK

Again, use 'see' to view its source code:

    OK see dos-dir
    {
        "__class__": "Word",
        "__module__": "peforth.projectk",
        "name": "dos-dir",
        "xt": {
            "__class__": "function",
            "__module__": "peforth.projectk"
        },
        "immediate": false,
        "help": "",
        "comment": "",
        "vid": "forth",
        "wid": 242,
        "type": "colon",
        "private": false,
        "cfa": 717
    }
    ------------ Definition in dictionary ------------
    00717: def compyle_anonymous():
        import os; os.system('dir') (<class 'function'>)
      2           0 LOAD_CONST               1 (0)
                  2 LOAD_CONST               0 (None)
                  4 IMPORT_NAME              0 (os)
                  6 STORE_FAST               0 (os)
                  8 LOAD_FAST                0 (os)
                 10 LOAD_ATTR                1 (system)
                 12 LOAD_CONST               2 ('dir')
                 14 CALL_FUNCTION            1
                 16 POP_TOP
                 18 LOAD_CONST               0 (None)
                 20 RETURN_VALUE
    00718: RET  (<class 'NoneType'>)
    ------------ End of the difinition ---------------
    OK

Now we have seen ```<py> ... </py>``` brings in a block of python code that does 
not return value. While ```<py> ... </pyV>``` is to envelope a python statement 
that returns a value back to forth's top of the data stack. We'll use it's short 
form ```py>``` that followed with a statement without space to get CPU information 
from DOS environment variable PROCESSOR_IDENTIFIER:

    OK : CPU ( -- string ) // View CPU info
    OK   py> os.getenv('PROCESSOR_IDENTIFIER') . cr ;
    OK CPU
    Intel64 Family 6 Model 142 Stepping 9, GenuineIntel  
    OK

So ```py>``` and ```py:``` are short form of ```<py>...</pyV>``` and ```<py>...</py>``` respectively.
    

Visit this project's [Wiki](https://github.com/hcchengithub/peforth/wiki) for more examples.

FigTaiwan H.C. Chen<br>
hcchen_1471@hotmail.com<br>
Just undo it!</br>


