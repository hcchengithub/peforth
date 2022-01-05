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
    r'''
	\ paste command ---------------------------------------------------------------------------------------------
		' paste [if] 
			.( 煩不煩？已經執行過了！ ) cr stop 
		[else]
			import IPython
				: paste py> IPython.lib.clipboard.win32_clipboard_get() tib.insert ;
					// ( ... -- ... ) 執行 clipboard 裡的內容，jupyternotebook 進了 peforth prompt 特別需要此功能。
				
	\ Timer -- the "with Timer():" block ------------------------------------------------------------------------
		<py>
			from time import time

			class Timer():
				"""
				%%time equivalent Context manager -- the "with Timer():" block
				Learned from https://www.codingame.com/playgrounds/500/advanced-python-features
				Usage : with Timer('This job costs {} ms'): ... 
				Where the argument of description can be omitted and use default 'Wall time: ... ms'.
				"""
				def __init__(self, message=None):
					self.message = message

				def __enter__(self):
					self.start = time()
					return None  # could return anything, to be used like this: with Timer("Message") as value:

				def __exit__(self, type, value, traceback):
					elapsed_time = (time() - self.start) * 1000
					if self.message:
						print(self.message.format(elapsed_time))
					else:
						print("Wall time: {} ms".format(elapsed_time))
			push(Timer)
		</py> constant Timer // ( -- class ) %%time magic equivalent "with" block. Usage: with Timer('This job costs {} ms'): ... 
							 /// Learned from https://www.codingame.com/playgrounds/500/advanced-python-features
							 /// Usage : 
							 /// 	Timer = peforth.dictate('Timer').pop()
							 /// 	with Timer('This job costs {} ms'): ... 
							 /// Arg omitted use default 'Wall time: ... ms'.

	\ Converter .py to .ipynb --------------------------------------------------------------------------------------------

		: py2ipynb ( pathname -- ) // Create converted foo.py.ipynb from given foo.py
			dup readTextFile ( pathname file.py )
			py> json.encoder.JSONEncoder().encode(pop()) ( pathname file.py.json )
			( before ) <text> {"cells":[{"cell_type":"code","execution_count":null,"metadata":{"collapsed":false},"outputs":[],"source":[</text> 
			swap + 
			( after ) <text> ]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.4.2"}},"nbformat":4,"nbformat_minor":0}</text> 
			+ ( pathname packed )
			swap char .ipynb + writeTextFile ;
			/// Usage:
			///   char c:\Users\username\1.py py2ipynb
			/// Result:
			///   Created new file c:\Users\username\1.py.ipynb
			/// 16:10 2018-01-12 https://www.webucator.com/blog/2015/07/bulk-convert-python-files-to-ipython-notebook-files-py-to-ipynb-conversion/

	\ ----------------------------------------------------------------------------------------------------------------------
	\ ----------------------------------------------------------------------------------------------------------------------
	\ ----------------------------------------------------------------------------------------------------------------------
	\ ----------------------------------------------------------------------------------------------------------------------
	\ ----------------------------------------------------------------------------------------------------------------------
	
    [then] 
	
	''')


