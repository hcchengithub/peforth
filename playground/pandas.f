<comment>
    天哪，都忘了怎麼用 peforth 了。首先要想在 jupyternotebook 中玩 peforth 開發 pandas.f 要先查清
    楚 working directory 之所在 through %f cd --> D:\hcchen\OneDrive\Documents\Jupyter Notebooks 
    然後把 pandas.f (如上) 放進該 directory. 回到 jypyternotebook cell 就可以 include 它了。
</comment>

import pandas  \ 注意！可以直接抓 pandas 喔！咱好厲害。
import io
code dummy_df # ( -- DataFrame ) A dummy DataFrame
    csv_in_memory = """
             index  ;  col 1  ;    col 2       
        9; 4.4 ;99
        2; 4.5 ; 200
        7;   4.7 ; 65    
          2 ;3.2 ; 140
        """
    csv_in_memory = '\n'.join([s.strip() for s in csv_in_memory.split('\n') if s.strip()])  # 去蕪存菁
    df = pandas.read_csv(io.StringIO(csv_in_memory)  , sep=";")
    # (來自 D-tale) update columns to strings in case they are numbers also trim leading and tailing white spaces.
    df.columns = [str(c).strip() for c in df.columns]  
    push(df)
    end-code
    
    <selftest>
    *** dummy_df
        dummy_df ( df ) 
        :> shape type py> pop()==tuple
        [d True d]
        [p 'dummy_df' p]
    </selftest>
                