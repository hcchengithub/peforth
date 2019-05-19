# peforth

### A programmable python debugger. Set one breakpoint to x-ray everything.

You guys know how to bebug already. We all do.
But when it comes to Machine Learning and Tensorflow or the likes, 
things are getting annoying if we were still using traditional debuggers.
A programmable debugger is what in my mind and probably in yours too. 
One breakpoint to investigate about everything! At this point, you can  
then test whatever you want, supported by all the power of FORTH.


### Debug commands in FORTH syntax

So now we need to choose an interactive UI and its syntax that 
is light weight, reliable and flexible so we won't regret of choosing it 
someday, has been there for decades so many people don't need to learn about 
another new language although we are only to use some debug commands, yet easy 
enough for new users, that's FORTH. 

### The quickest way to try peforth

An easy way to try peforth is through the [Microsoft Azure Notebooks](https://notebooks.azure.com/). Create a [Jupyter notebook page](https://notebooks.azure.com/hcchen1471/projects/peforthplayground) and install peforth on that page with this line:
    
    !pip install peforth
    
and then you can import peforth like this:

    iport peforth
    
and then start using peforth through magics `%f` and `%%f` as shown below: 

![Run peforth on Azure notebooks](http://imgsrc.baidu.com/forum/pic/item/dea32e738bd4b31ca20ded1a89d6277f9e2ff828.jpg)

### Install peforth:

    pip install peforth 

### Magics for Jupyter Notebook

`import peforth` on Jupyter Notebook is the only thing you need to do to use peforth 
`%f` and `%%f` magics.  For tutorials, please find and read jupyter notebooks in the 'notebook' directory of this project.

Optionally if you want ipython and jupyter notebook to load peforth magics automatically at startup, so you don't need to `import peforth` explicitly everytime, what you need to do is to find this config file:

    C:\Users\<your user name>\.ipython\profile_default\ipython_config.py (for Windows)
    or
    ~/.ipython/profile_default/ipython_config.py (for Linux, WSL Ubuntu in my case) 

this line:

    ... snip...
    # A list of dotted module names of IPython extensions to load.
    c.InteractiveShellApp.extensions = ['peforth']
    ... snip...
    
to have 'peforth' in the list as shown above.

### Add peforth as a native language kernel to Jupyter Notebook

This is to make a notebook to run FORTH instead of python. 
That means when you 'New' a notebook, "peforth" appears in the list among "Python 2" and "Python 3".
Do these steps to make this happen:

1. `pip install peforth` so you have peforth in your computer
2. copy the file `kernel.json` from here<br>
   `c:\Users\<your name>\AppData\Local\Programs\Python\Python36\Lib\site-packages\peforth\kernel.json` <br>
   to here <br>
   `c:\Users\<your name>\AppData\Roaming\jupyter\kernels\peforth`<br>
   if the above directory is not exist then you create it.
3. Edit `c:\Users\<your name>\AppData\Roaming\jupyter\kernels\peforth\kernel.json` to correct the path of _peforthkernel.py_ which is supposed to be 
`c:\Users\<your name>\AppData\Local\Programs\Python\Python36\Lib\site-packages\peforth\peforthkernel.py` for example on my Windows 10 computer. Your `<user name>` must be different from mine so you need to correct it.

### Run peforth:

Print "Hello World!"

    Microsoft Windows [Version 10.0.15063]
    (c) 2017 Microsoft Corporation. All rights reserved.

    c:\Users\your-working-folder>python -m peforth .' Hello World!!' cr bye
    Hello World!!

    c:\Users\your-working-folder>

so your peforth is working fine. 
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


### Investigate by running experiments right at a breakpoint
    
When at a breakpoint in Tensorfow tutorials, I always want to
make some experiments on those frustrating *tf.something(tf.something(...),...)*
things to have a clearer understanding of them 
without leaving the underlying tutorial. Let's use the above example
again in another way to demonstrate how to do that with peforth:  

Run peforth:

    Microsoft Windows [Version 10.0.15063]
    (c) 2017 Microsoft Corporation. All rights reserved.

    c:\Users\hcche\Downloads>python
    Python 3.6.0 (v3.6.0:41df79263a11, Dec 23 2016, 08:06:12) [MSC v.1900 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import peforth
    p e f o r t h    v1.07
    source code http://github.com/hcchengithub/peforth
    Type 'peforth.ok()' to enter forth interpreter, 'exit' to come back.

    >>> peforth.ok()

    OK   <-------- Default FORTH command prompt
    OK    

Assume we are at a breakpoint and we need a procedure to
add 1..100 to get the sum of them. We are not sure if the procedure
is correct so we need to try. Now copy the procedure from 
your text editor. The ``` <py>...</py> ``` tells the debugger that 
the code within is a block of in-line python. 
The ```outport()``` function outports the given ```locals()``` to the
FORTH environment outside the in-line python block.

    <py>
    sum = 0
    for i in range(100):
        sum += i
    print("The sum of 1..100 is ", sum)
    outport(locals())
    </py>
    
It's a block of multiple-line text strings so we press Ctrl-D
to start a multiple-line input, copy-paste, and press another Ctrl-D
to end the multiple-line block. Like this:

    OK
    OK ^D
        <py>
        sum = 0
        for i in range(100):
            sum += i
        print("The sum of 1..100 is ", sum)
        outport(locals())
        </py>
    ^D
    The sum of 1..100 is  4950
    OK

Now use the 'words' command to see what have we got:

    OK words
    code end-code \ // <selftest> </selftest> bye /// immediate stop compyle 
    trim indent -indent <py> </py> </pyV> words . cr help interpret-only 
    compile-only literal reveal privacy (create) : ; ( BL CR word ' , 
    [compile] py: py> py:~ py>~ 0branch here! here swap ! @ ? >r r> r@ drop 
    dup over 0< + * - / 1+ 2+ 1- 2- compile if then compiling char last 
    version execute cls private nonprivate (space) exit ret rescan-word-hash 
    (') branch bool and or not (forget) AND OR NOT XOR true false "" [] {} 
    none >> << 0= 0> 0<> 0<= 0>= = == > < != >= <= abs max min doVar doNext 
    depth pick roll space [ ] colon-word create (marker) marker next abort 
    alias <> public nip rot -rot 2drop 2dup invert negate within ['] allot 
    for begin until again ahead never repeat aft else while ?stop ?dup 
    variable +! chars spaces .( ." .' s" s' s` does> count accept accept2 
    <accept> nop </accept> refill [else] [if] [then] (::) (:>) :: :> ::~ 
    :>~ "msg"abort abort" "msg"?abort ?abort" '<text> (<text>) <text> </text> 
    <comment> </comment> (constant) constant value to tib. >t t@ t> [begin] 
    [again] [until] [for] [next] modules int float drops dropall char>ASCII 
    ASCII>char ASCII .s (*debug*) *debug* readTextFile writeTextFile 
    tib.insert sinclude include type obj>keys obj2dict stringify toString 
    .literal .function (dump) dump dump2ret d (see) .members .source see dos 
    cd slice description expected_rstack expected_stack test-result 
    [all-pass] *** all-pass [r r] [d d] [p p] WshShell inport OK dir keys 
    --- i sum
    OK

At the end of the long list after the ``` --- ``` marker we found ``` i ``` and 
``` sum ```. They are all locals() at the point in the in-line python block.
Let's see them:

    OK i . cr
    99
    OK sum . cr
    4950
    OK
    
Again, we found the root cause of why the sum is not 5050 because
``` i ``` didn't reach to 100 as anticipated. That's exactly how the 
python ```range()``` works and that has actually confused me many times.


Visit this project's 
[Wiki](https://github.com/hcchengithub/peforth/wiki) pages
for more examples about how to view MNIST handwritten digit images
at the half way of your investigating in a Tensorflow tutorial, for
example, and the usages of this programmable debugger.

#### Have fun!

H.C. Chen, FigTaiwan <br>
hcchen_1471@hotmail.com<br>
Just undo it!</br>
