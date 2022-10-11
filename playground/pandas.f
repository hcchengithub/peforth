<comment>
    https://levelup.gitconnected.com/top-20-pandas-functions-which-you-arent-using-which-you-should-be-using-a408a330daac

    要想在 jupyternotebook 中玩 peforth 開發 pandas.f 要先查清楚 working directory 之所在 through %f cd --> D:\hcchen\OneDrive\Documents\Jupyter Notebooks
    然後把 pandas.f (如上) hard link 放進該 directory. 回到 jypyternotebook cell 就可以 include 它了。或者用 %f cd D:\hcchen\OneDrive\Documents\Jupyter Notebooks
    把 working directory 切換 pandas.f 所在之處亦可，也許更好。    
</comment>

import pandas  \ 注意！可以直接抓 pandas 喔！咱好厲害。
import io
code dummy-df # ( -- DataFrame ) A dummy DataFrame
    csv_in_memory = """
            index  ;  col 1  ;    col 2
            9; 4.4 ;99
          2; 4.4 ; 200
           7;; 65
              2 ;3.2 ;
        """
    csv_in_memory = '\n'.join([s.strip() for s in csv_in_memory.split('\n') if s.strip()])  # 去蕪存菁
    df = pandas.read_csv(io.StringIO(csv_in_memory)  , sep=";")
    df.columns = [str(c).strip() for c in df.columns]  # (來自 D-tale) update columns to strings in case they are numbers also trim leading and tailing white spaces.
    push(df)
    end-code

    <selftest>
    *** dummy_df
        dummy_df ( df )
        :> shape type py> pop()==tuple
        [d True d]
        [p 'dummy_df' p]
    </selftest>

code see-dummy-df # ( -- ) Use variant pandas ways to see the DataFrame
    execute("dummy-df");
    print("tos().info()"); tos().info(); 
    print(); print("tos().describe()"); print(tos().describe());
    print(); print("tos().head()"); print(tos().head(2));
    print(); print("tos().tail()"); print(tos().tail(2));
    print(); print("tos().sample()"); print(tos().sample(2));
    print(); print("tos().shape"); print(tos().shape);
    print(); print("tos().isnull().any()"); print(tos().isnull().any());
    print(); print("tos().isnull().sum()"); print(tos().isnull().sum());
    print(); print("tos().isna().any()"); print(tos().isna().any());
    print(); print("tos().isna().sum()"); print(tos().isna().sum());
    print(); print("tos().nunique()"); print(tos().nunique());
    print(); print("tos().index"); print(tos().index);
    print(); print("tos().columns"); print(tos().columns);
    print(); print("tos().memory_usage()"); print(tos().memory_usage());
    col_first = tos().columns[0] # dummy example
    print(); print("tos().nsmallest(2,col_first)"); print(tos().nsmallest(2,col_first));
    print(); print("tos().nlargest(2,col_first)"); print(tos().nlargest(2,col_first));
    print(); print("df[...].groupby()"); print("tos()[['index','col 1','col 2']].groupby[['index','col 1']].mean()"); print(tos()[['index','col 1','col 2']].groupby(['index','col 1']).mean());
    print(); print("Sort"); print("tos().sort_index(axis=1,ascending=True)"); print(tos().sort_index(axis=1,ascending=True)); print(); print("tos().sort_values(by='col 2')"); print(tos().sort_values(by='col 2')); execute("dropall")
    end-code
    /// tos().shape
    /// tos().info()
    /// tos().describe()
    /// tos().nunique()
    /// tos().nsmallest(2,col_first)
    /// tos().nlargest(2,col_first)
    /// tos().head(2)
    /// tos().tail(2)
    /// tos().sample(2)
    /// tos().isnull().any()
    /// tos().isnull().sum()
    /// tos().isna().sum()
    /// tos().isna().any()
    /// tos().index
    /// tos().columns
    /// tos().memory_usage()
    /// tos()[['index','col 1','col 2']].groupby(['index','col 1']).mean()
    /// tos().sort_index(axis=1,ascending=True)
    /// tos().sort_values(by='col 2')
