# peforth
A Forth programming language in python

----
這是個用 python 實現的 forth 語言 interpreter。
我初學 python 想要把這個 project 打包成 peforth.whl 讓使用者經由 ```pip install peforth.whl``` 來安裝以供 import peforth 引用。
打包成 .whl 或者其他方法也都歡迎指導。

我已經實驗好手動安裝可以成功。
1. 把本 project 的四個檔案 ```projectk.py quit.f peforth.f __main__.py``` 全部 copy 到如下新創建的 folder: c:\Users\yourname\AppData\Local\Programs\Python\Python36\Lib\site-packages\peforth
2. 把其中 ```__main__.py``` 多 copy 一份成 ```__init__.py``` 即可。

執行 peforth 有四個方式
1. 從 project folder 下執行 ```python __main__.py```
   OK 後打 ```: test .’ hello world!’ cr ; test``` 印出 hello world! 打 ```bye``` 離開。
2. 從 project folder 外面執行 ```python peforth``` 
   OK 後打 ```: test .’ hello world!’ cr ; test``` 印出 hello world! 打 ```bye``` 離開。
3. 安裝好 peforth package 之後,任意 folder 下執行 ```python -m peforth``` 後同上。   
4. 安裝好 peforth package 之後,任意 folder 下執行 ```python```
   然後 import peforth 然後按照指示打 ```peforth.main()``` 進入 peforth 後同上。

我就是只會手動安裝 peforth，不知如何讓使用者用方便點的方式安裝。請惠予指點。

H.C. Chen
Just undo it!
hcchen_1471@hotmail.com


