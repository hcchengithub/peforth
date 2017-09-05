# peforth
A Forth programming language in python

Click above [Wiki] to read usage examples.

There are many ways to run peforth:

1. In the project folder run ```python __main__.py``` or ```python __init__.py``` or double click them.
2. From above the project folder run ```python peforth```
3. If the peforth package is installed. At any folder, run ```python -m peforth```
4. If the peforth package is installed. At any folder, run ```python``` then ```import peforth``` then type ```peforth.ok()``` to run it.

Install peforth as a package:

Copy all five files (```projectk.py quit.f peforth.f __main__.py __init__.py```) from the peforth project folder to the new created folder: ```c:\Users\...\Python36\Lib\site-packages\peforth``` , that's all.
The sample path is for this computer on my desk. For your computer, do these steps to get the corresponding path:

    >>> import re
    >>> re
    <module 're' from '*C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\*re.py'>
    >>>

----
這是個用 python 實現的 forth 語言 interpreter。

執行 peforth 有多種方式
1. 從 project folder 下執行 ```python __main__.py``` 或 double click ```__main__.py or __init__.py```
   OK 後打 ```: test .’ hello world!’ cr ; test``` 印出 hello world! 打 ```bye``` 離開。
2. 從 project folder 外面執行 ```python peforth``` 
   OK 後打 ```: test .’ hello world!’ cr ; test``` 印出 hello world! 打 ```bye``` 離開。
3. 安裝好 peforth package 之後,任意 folder 下執行 ```python -m peforth``` 後同上。   
4. 安裝好 peforth package 之後,任意 folder 下執行 ```python```
   然後 ```import peforth``` 然後按照指示打 ```peforth.main()``` 進入 peforth 後同上。

手動安裝成 package：

把本 project 的五個檔案 ```projectk.py quit.f peforth.f __main__.py __init__.py``` 全部 copy 到如下新創建的 folder: ```c:\Users\yourname\...\Python36\Lib\site-packages\peforth```
一步完成！用下例方法確定該新 folder 的相對位置：

    >>> import re
    >>> re
    <module 're' from '*C:\\Users\\hcche\\AppData\\Local\\Programs\\Python\\Python36\\lib\\*re.py'>
    >>>


我初學 python 就只會以上的手動安裝。很希望能打包成 peforth.whl 似乎很方便讓使用者經由 ```pip install peforth.whl``` 來安裝以供 import peforth 引用。或者其他傳播、安裝的方法也都歡迎高手指導看怎麼好做。

FigTaiwan H.C. Chen<br>
hcchen_1471@hotmail.com<br>
Just undo it!</br>


