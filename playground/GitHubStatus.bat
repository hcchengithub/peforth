: @rem ; ' \ dup alias echo dup alias @echo dup alias @echo. dup alias @goto dup alias :end dup alias @cd dup alias @call dup alias @if dup alias :ERR dup alias @pause dup alias :END dup alias @rem drop
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

    \ Check modified projects
        import os constant os
        os :> getenv('USERPROFILE')+'\\Documents\\GitHub' os :: chdir(pop())
        os :> listdir() ( [dirlist,...] ) cr cr cr
        [begin]
            py> tos().pop() ( [dirlist,...] projectName ) 
            os :: chdir(pop())
            cd
            dos git status
            drop cd ..
            cr cr
        py> len(tos()) not [until] drop
		os :> getenv('USERPROFILE')+'\\Documents\\GitHub\\jeforth\\jeforth.3we'
		os :: chdir(pop())
		cd
		dos git status
		drop 
        os :> getenv('USERPROFILE')+'\\Documents\\GitHub' os :: chdir(pop())
		cr cr

    \ The end

        cr ." ----------- All Done --------------" cr 
        \ bye <-- don't we might need to see the error messages
        stop
        
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



