
    \ Specify directory paths and target file names

        "" value project-directory // ( -- 'path' ) local GitHub project source code working directory
        "" value package-directory // ( -- 'path' ) a temp folder to build the whl 
        [] value source-files      // ( -- iterable ) source code file names  
        
        char c:\Users\hcche\Documents\GitHub\peforth\ to project-directory 
        char c:\Users\hcche\Desktop\peforth-master\   to package-directory
        py> ['projectk.py','__main__.py','__init__.py','peforth.f','quit.f','README.md','version.txt'] 
                                                  to source-files
    \ Please confirm the directory paths and source files
    
        project-directory tib.
        package-directory tib.
        source-files tib.
        ." Check above directory paths and source files, ok? [Enter] to continue or 'abort' " 
        py> input() cr char abort = [if] bye [then]
                                                  
    \ Creating symbolic links from project folder to working folder to make whl
    \ Example : os.symlink(src, dst)
    
        <py>
            os.symlink(v('project-directory')+'setup.py', v('package-directory')+"setup.py")
            for fname in v('source-files'):
                ok('11> ',fname)
                os.symlink(v('project-directory')+fname, v('package-directory')+"peforth\\"+fname)
        </py>
stop    
        <comment>
            
            檢查 creating symbolic links 有沒有成功，可能用上的方法。

            1. 土土地看檔案在不在

                py> os.path.isfile(r'c:\Users\hcche\Desktop\peforth-master\peforth\quit.f') tib. \ ==> True (<class 'bool'>)
                py> os.path.isfile(r'c:\Users\hcche\Desktop\peforth-master\peforth\quit.fff') tib. \ ==> False (<class 'bool'>)

            2. 跟目標比較看是否完全一樣，這個好！

                查看咱 target directory 裡有哪些檔案
                py> os.listdir('peforth') tib. \ ==> ['peforth.f', 'projectk.py', 'quit.f', '__init__.py', '__main__.py'] (<class 'list'>)
                
                把咱 target directory 檔案 list 改成 set 以便比較
                py> os.listdir('peforth') py> set(pop())
                
                應該要有這些檔案
                source-files tib. \ ==> ['projectk.py', '__main__.py', '__init__.py', 'peforth.f', 'quit.f']
                
                該有的檔案 list 改成 set 以便比較
                source-files py> set(pop())

            最終，一行搞定，得 creating symbolic links 有沒有成功的一個 boolean 

                py> os.listdir('peforth') py> set(pop()) source-files py> set(pop()) =
            
        </comment>
    
    \ 檢查 creating symbolic links 有沒有成功 
    
        py> os.listdir('peforth') py> set(pop()) source-files py> set(pop()) =
        [if] [else] 
            ." Error! sth wrong in creating symbolic links of source code files to working directory." cr 
            *debug* update.f_1122>>>
        [then]
    
    \ 開始打包 whl 結果出現在 package-directory 之下的 dist directory 裡面：
    
        <py> 
            os.system("pip wheel --wheel-dir=dist " + v('package-directory'))
        </py>

        <comment>
        
            peforth/version.txt 只有一行 python statement 讓相關的單位都來參考它。
            see peforth/log.txt for more details

                __version__ = "1.02"
            
        </comment>
    
    \ 好了，告知 user whl 在哪裡
    
        ." whl package has been successfully created at " cr
        py> v('package-directory')+"dist" . cr cr
    
        ." ---- Done ---- " cr
        