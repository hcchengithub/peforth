
# 02:33 2021/11/22 was 'forth.py' 
# Usage: %run ../../../jupyter-extension.py 
#        In a jupyternotebook cell to init peforth

import IPython
import peforth
peforth.dictate('''
    ' paste [if] .( 執行過了 ) cr stop [else] 
    import IPython
    : paste py> IPython.lib.clipboard.win32_clipboard_get() tib.insert ;
        // ( ... -- ... ) 執行 clipboard 裡的內容，jupyternotebook 進了 peforth prompt 特別需要此功能。
    ''')
