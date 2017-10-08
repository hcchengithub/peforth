# peforth

### A programmable python debugger. Set one breakpoint to x-ray everything.

You guys know how to bebug already. We all do.
But when it comes to Machine Learning and Tensorflow or the likes, 
things are getting annoying if we were still using traditional debuggers.
A programmable debugger is what in my mind and probably in yours too. 
One breakpoint to investigate about everything with procedures that we
come out at the point depend on variant needs of emerged ideas good or bad.

### Debug commands in FORTH syntax

So now we need to choose an interactive UI and its syntax that 
is light weight, reliable and flexible so we won't regret of choosing it 
someday, has been there for decades so many people don't need to learn about 
another new language although we are only to use some debug commands, yet easy 
enough for new users, that's FORTH. 

### Install peforth:

    pip install peforth 

### Run peforth:

Print "Hello World!"

    Microsoft Windows [Version 10.0.15063]
    (c) 2017 Microsoft Corporation. All rights reserved.

    c:\Users\your-working-folder>python -m peforth .' Hello World!!' cr bye
    Hello World!!

    c:\Users\your-working-folder>

so your peforth has been working fine. 
To your application, ``` import peforth ``` as usual to bring in the debugger:

    c:\Users\your-working-folder>python
    Python 3.6.0 (v3.6.0:41df79263a11, Dec 23 2016, 08:06:12) [MSC v.1900 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import peforth
    p e f o r t h    v1.07
    source code http://github.com/hcchengithub/peforth
    Type 'peforth.ok()' to enter forth interpreter, 'exit' to come back.

    >>>

The greeing message tells us how to enter the FORTH interpreter for your 
debugging or investigating and how to come back to continue running your 
code.     
    
### Let's try to debug a program
    
    # 100.py
    
    sum = 0
    for i in range(100):
        sum += i
    print("The sum of 1..100 is ", sum)
    
Run it:

    c:\Users\your-working-folder>python 100.py
    The sum of 1..100 is 4950

    c:\Users\your-working-folder>

The result should be 5050 but it's not! Let's drop a breakpoint 
to see what's wrong:

    # 100.py with breakpoing   .----- Specify an unique command prompt to indicate where 
                               |      the breakpoint is from if there are many of them
    import peforth             |            .----- pass locals() at the breakpoint
    sum = 0                    |            |      to our debugger
    for i in range(100):       |            |               .------- use a FORTH constant   
        sum += i               |            |               |        to represent the locals()
    peforth.ok('my first breakpoint> ',loc=locals(),cmd="constant locals-after-the-for-loop")
    print("The sum of 1..100 is ", sum)

Run again:
    
    c:\Users\your-working-folder>python 100.py
    p e f o r t h    v1.07
    source code http://github.com/hcchengithub/peforth
    Type 'peforth.ok()' to enter forth interpreter, 'exit' to come back.

                         .--------------- at the breakpoint, type in 'words' 
                         |                command to see what have we got   
    my first breakpoint> words        .-------- It's a long list of 'words'
    ... snip .......                  |         or available commands. Don't worry, we'll use only some of them.
    expected_rstack expected_stack test-result [all-pass] *** all-pass [r r] [d d] [p 
    p] WshShell inport OK dir keys --- locals-after-the-for-loop
                                           |
                The last one is what ------' 
                we have just created throuth the breakpoint statement    
                , named "locals-after-the-for-loop"

Let's see it:

           print a carriage return at the end -------.
                              print the thing -----. | 
                                                   | |
    my first breakpoint> locals-after-the-for-loop . cr
    ({'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': 
    <_frozen_importlib_external.SourceFileLoader object at 0x000001DD2D737710>, 
    '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' 
    (built-in)>, '__file__': '100.py', '__cached__': None, 'peforth': <module 'peforth' 
    from 'C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\site-packages\\pe
    forth\\__init__.py'>, 'sum': 4950, 'i': 99}, {}, 'my first breakpoint> ')
    my first breakpoint>    |           |                   |
                            |           |                   '--- our command
               our sum -----'           |                        prompt
                                        |                  indicates where the 
            99 instead of 100 ----------'                  breakpoint is from
            this is the problem !!            

Now leave the breakpoint and let the program continue:

    my first breakpoint> exit
    my first breakpoint> The sum of 1..100 is  4950

    c:\Users\your-working-folder>

Visit this project's 
[Wiki](https://github.com/hcchengithub/peforth/wiki) pages
for more examples about how to view MNIST handwritten digit images
at the half way of your investigating in a Tensorflow tutorial, for
example, and the usages of this programmable debugger.

#### Have fun!

H.C. Chen, FigTaiwan <br>
hcchen_1471@hotmail.com<br>
Just undo it!</br>
