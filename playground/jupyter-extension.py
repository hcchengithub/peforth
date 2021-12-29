#
# Python debugger in FORTH language for jupyternotebook 
#
# Usage: 
#   %run "drive:\path\this file.py" 
#        ^^^^^^^^^ backslash is ok magic does not need to use r" which is of python not magic  
#
#   In a jupyternotebook cell to initialize peforth environment. So we have, 
#   bp    - breakpoints
#   paste - run anything in clipboard at a breakpoint
#   display-on display-off - turn on/off peforth STDOUT
#
# Conditional invoke:
#   if not PROD:
#       get_ipython().run_line_magic('run', r"drive:\path\this file.py") 
#
#
# H.C. Chen 16:01 12/15/2021
# http://github.com/hcchengithub/peforth
#

import peforth
peforth.dictate(
    '''
    ' paste [if] 
        .( 煩不煩？已經執行過了！ ) cr stop 
    [else]
        import IPython
        \ ------ paste ------------------------------------------------------------

            : paste py> IPython.lib.clipboard.win32_clipboard_get() tib.insert ;
                // ( ... -- ... ) 執行 clipboard 裡的內容，jupyternotebook 進了 peforth prompt 特別需要此功能。

    [then] 
    '''
)

