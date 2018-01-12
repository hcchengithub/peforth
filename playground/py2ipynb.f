
\ 16:10 2018-01-12
\ I found this solution from 
\ https://www.webucator.com/blog/2015/07/bulk-convert-python-files-to-ipython-notebook-files-py-to-ipynb-conversion/

import json constant json // ( -- module )
<text> {"cells":[{"cell_type":"code","execution_count":null,"metadata":{"collapsed":false},"outputs":[],"source":[</text> 
constant nb_start // ( -- "text" ) 
<text> ]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"codemirror_mode":{"name":"ipython","version":3},"file_extension":".py","mimetype":"text/x-python","name":"python","nbconvert_exporter":"python","pygments_lexer":"ipython3","version":"3.4.2"}},"nbformat":4,"nbformat_minor":0}</text> 
constant nb_end // ( -- "text" ) 

: py2ipynb ( pathname -- ) // Convert the given .py to .ipynb 
    dup readTextFile ( pathname file.py )
    json :> encoder.JSONEncoder().encode(pop()) ( pathname file.py.json )
    nb_start swap + nb_end + ( pathname packed )
    swap char .ipynb + writeTextFile ;
    /// Usage:
    ///   char c:\Users\username\1.py py2ipynb
    /// Result:
    ///   c:\Users\username\1.py.ipynb created
    
