set pythonlib=C:\Users\hcche\AppData\Local\Programs\Python\Python36\lib
copy /Y __main__.py __init__.py 
copy /y version.txt %pythonlib%\site-packages\peforth\
copy /y projectk.py %pythonlib%\site-packages\peforth\
copy /y __main__.py %pythonlib%\site-packages\peforth\
copy /y __init__.py %pythonlib%\site-packages\peforth\
copy /y quit.f      %pythonlib%\site-packages\peforth\
copy /y peforth.f   %pythonlib%\site-packages\peforth\
copy /y peforth.selftest %pythonlib%\site-packages\peforth\
pause 