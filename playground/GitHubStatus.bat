: @rem ; ' \ dup alias echo dup alias @echo dup alias @echo. dup alias @goto dup alias :end dup alias @cd dup alias cd dup alias call dup alias @if dup alias :ERR dup alias pause dup alias :END dup alias @rem drop
@cd %~dp0
@rem
@rem
@rem   Check my GitHub status
@rem   Find anything modified that might need a commit
@rem

@echo.
@echo Executing %~nx0 . . .
@goto batch

\ --------------- start peforth code ----------------------

    \ Greetings
    
        cr cr
        ." What I am going to do are:" cr
        ." 1. Copy peforth package files to site-packages\peforth." cr
        ." 2. Packup peforth into a wheel package." cr
        ." 3. Upload peforth package to pypi.python.org" cr
        ." Press Enter to continue or 'abort' to stop it. "
        py> input()=="abort" [if] ." Action aborted by user." cr abort [then] 

    \ 從 project directory copy updated files to site-packages\peforth

        \ 說明接下來要幹什麼
        
            cr 
            ." Copy peforth package files to site-packages\peforth." cr
            ." Press Enter to continue or 'abort' to stop it. "
            py> input()=="abort" [if] ." Action aborted by user." cr abort [then] 
    
        \ 取得 peforth package 在本電腦 site-packages\peforth 的完整 path.
        \ 因為執行方法是 -m peforth 所以 py> path 正是它。
        \ py> path tib. \ ==> C:\Users\hcche\AppData\Local\Programs\Python\Python36\lib\site-packages\peforth\ (<class 'str'>)

            py> path value dest // ( -- "path" ) ~\site-packages\peforth\
            
            \ 檢查 dest 以免亂寫到別地方去
            dest :> find('peforth')!=-1 dest :> find('site-packages')!=-1
            and [if] [else] cr ." Error! unexpected destination." cr abort [then]

        \ 當前 working directory 一定就是 peforth project directory 因為
        \ 這是 setup.bat 唯一所在，而 @cd %~dp0 就是到這裡來。
        \ py> os.getcwd() tib. \ ==> c:\Users\hcche\Documents\GitHub\peforth (<class 'str'>)

            py> os.getcwd() char \ + value source // ( -- "path" ) ~\GitHub\peforth\
            
            \ 檢查 source 雖然應該不會錯
            source :> find('peforth')!=-1 source :> lower().find('GitHub'.lower())!=-1
            and [if] [else] cr ." Error! unexpected source." cr abort [then]

        \ 直接用 DOS 的 copy /y from to 就可以了

            \ List peforth package files 
            <py> 
            [
            "version.txt", 
            "projectk.py", 
            "__main__.py", 
            "__init__.py", 
            "quit.f", 
            "peforth.f", 
            "peforth.selftest",
            "kernel.json",
            "peforthkernel.py",
            ]
            </pyV>
            constant files // ( -- [filenames] ) peforth package files in site-packages/

            \ ---- 作廢老 code -----------
            \ 這個 file 從 __main__.py copy 出來，單獨 copy。
            \ s" copy /y {}__main__.py {}__init__.py" :> format(v('source'),v('dest'))
            \ py: os.system(pop())

            \ ---- 本想改用 --upgrade --force-reinstall peforth 但不成功
            \ peforth package files 都 copy 過去
            <py>
            for i in v('files'):
                cmd = "copy /y {} {}".format(i,v('dest'))
                os.system(cmd)
            </py>

            \ 此法失敗
            \ os.getcwd() --> GitHub/peforth
            \ cd ..
            \ dos pip install --upgrade --force-reinstall peforth
            \ cd peforth
            \ 此法失敗 症狀如下
            \ c:\Users\hcche\Documents\GitHub>pip install --upgrade --force-reinstall peforth
            \ Collecting peforth
            \   Using cached peforth-1.11-py3-none-any.whl
            \ Installing collected packages: peforth
            \   Found existing installation: peforth 1.11
            \     Uninstalling peforth-1.11:
            \       Successfully uninstalled peforth-1.11
            \ Successfully installed peforth-1.11
            \ 
            \ c:\Users\hcche\Documents\GitHub>
            
            
    \ 問要不要打包 whl?

        cr 
        ." Packup peforth into a wheel package" cr
        ." Press Enter to stop it or 'continue' to proceed. "
        py> input()=="continue" [if] [else] ." Action aborted by user." cr bye [then] 
            
        cr 
        ." o  Check ~\GitHub\peforth\setup.py and ~\GitHub\peforth\setup.bat" cr
        ."    files to make sure no new files are missing." cr cr
        ." o  Check the package quit.f to make sure selftest is Disabled before a release." cr cr
        ." Press Enter to stop it or 'continue' to proceed. "
        py> input()=="continue" [if] [else] ." Action aborted by user." cr abort [then] 

        \ 準備 target directory 
        \ ~\Desktop\peforth-master 裡面清空，只留空的 peforth folder 在裡面。

            \ 取得 desktop 的 path , USERPROFILE=C:\Users\hcche
            py> os.getenv('USERPROFILE') char \desktop\ + constant desktop // ( -- "path" )
            
            \ 刪除本來的 peforth-master directory
            s" rmdir /s /q {}peforth-master" :> format(v('desktop'))
            py> os.system(pop()) \ 0:OK, 2:directory not found
            [if] 
                ." Can't rmdir desktop\peforth-master. Enter to go on or 'abort' "
                py> input()=="abort" [if] ." Action aborted by user." cr abort [then] 
            [then]
            
            \ Create the desktop\peforth-master tree
            s" mkdir {}peforth-master\peforth" :> format(v('desktop'))
            py> os.system(pop()) \ 一下完成，這是用 dos command 的好處. 0:OK 
            [if] ." Error! Failed to mkdir desktop\peforth-master\peforth" cr abort [then]
            
            \ path of the wheel working directory
            desktop char peforth-master\ + constant peforth-master // ( -- "path" ) working directory to build wheel
            peforth-master char peforth\ + constant peforth-master\peforth // ( -- "path" ) working directory to build wheel
            
        \ 把所需的 files 都從 site-packages\peforth copy 過去
        
            \ Copy peforth package files to peforth-master

                \ peforth package files 都從 site-packages\peforth copy 過去
                <py>
                for i in v('files'):
                    cmd = "copy /y {} {}".format(v('dest')+i,v('peforth-master\peforth'))
                    os.system(cmd)
                </py>
                
                \ 還有 building wheel 特別要用的檔案
                s" copy /y setup.py {}" :> format(v('peforth-master'))
                py: os.system(pop())
                s" copy /y README.rst {}" :> format(v('peforth-master'))
                py: os.system(pop())
            
        \ 檢查 files copy 有沒有成功 
        
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

                最終，一行搞定，得 copy files 有沒有成功的一個 boolean 

                    py> os.listdir('peforth') py> set(pop()) source-files py> set(pop()) =
            
            </comment>

            \ 檢查 peforth-master\peforth 裡面
            py> os.listdir(v('peforth-master\peforth')) py> set(pop()) 
            files py> set(pop()) =
            [if] [else] 
                ." Error! files not correct in desktop\peforth-master\peforth " cr 
                abort
            [then]
            
            \ 檢查 peforth-master 本身
            py> os.listdir(v('peforth-master')) py> set(pop()) 
            py> ['peforth','setup.py','README.rst'] py> set(pop()) =
            [if] [else] 
                ." Error! files not correct in desktop\peforth-master " cr 
                abort
            [then]
            
        
        \ 開始打包 whl 結果出現在 peforth-master 之下的 dist directory 裡面：
        
            py> os.getcwd() ( cwd ) \ Save cwd
            py: os.chdir(v('peforth-master'))
            <py> 
                os.system("pip wheel --wheel-dir=dist " + v('peforth-master'))
            </py>
            py: os.chdir(pop()) \ restore cwd 
        
        \ 好了，告知 user whl 在哪裡
        
            cr ." ---- wheel has been created ---- " cr
            ." whl package is supposed to have been created at " cr
            py> v('peforth-master')+"dist" . cr cr
        
        \ 打包步驟
        \ 1. 檢查 ~\GitHub\peforth\setup.py ＆ ～\GitHub\peforth\pack.f 看有沒有漏掉新檔案，有沒有要去掉的檔案。
        \ 2. ～\Desktop\peforth-master 裡面清空，只留空的 peforth folder 在裡面。
        \ 3. 跑 ~\GitHub\peforth\update.bat , 試驗 python -m peforth 以及 ～\GitHub\peforth\__main__.py 都能跑。
        \ 4. 用 administrator mode 跑 pack.bat 得到 peforth.whl in ~\Desktop\peforth-master\dist 
        \ 5. 從 ～\Desktop\peforth-master> 執行 twine upload dist/* 需要帳號密碼，看這裡 python pypi 研究 -- upload to PyPI ok now.note
        \ 6. pip uninstall peforth 然後再 pip install peforth 試驗看看。
        \ 7. 完成！
            
    \ 問要不要 upload 上 pypi?

        cr 
        ." Upload peforth package to pypi.python.org" cr
        ." You'll be asked to input pypi ID and password." cr
        ." Press Enter to stop it or 'continue' to proceed. "
        py> input()=="continue" [if] [else] ." Action aborted by user." cr abort [then] 

        \ Do the upload

        py> os.getcwd() ( cwd ) \ Save cwd
        py: os.chdir(v('peforth-master'))
        <py> 
            os.system("twine upload dist/*")
        </py>
        py: os.chdir(pop()) \ restore cwd 

    \ The end

        cr ." ----------- All Done --------------" cr 
        \ bye <-- don't we may need to see the error messages
        
\ ---------------- end peforth code -----------------------

:batch
@rem @call admin.bat
@rem ---------- start batch code ---------------------------
@python -m peforth include %~nx0 \ include the batch program itself
@if %errorlevel% GEQ 1 goto ERR
@rem ------------ end batch code ---------------------------

@goto END
:ERR
@echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@echo   errorlevel : %errorlevel%
@echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@pause
:END



