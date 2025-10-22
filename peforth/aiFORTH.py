r"""
    Install peforth
    ==========================================

    pip install --force-reinstall "c:\Users\...\GitHub\peforth"


    aiFORTH - Add %ai to your jupyter notebook
    ==========================================

    From your .py or .ipynb run:

        import os
        import peforth  # Import your module
        module_directory = os.path.dirname(peforth.__file__)
        aiforth = os.path.join(module_directory, "aiFORTH.py")
        aiModel = "gpt-4o-mini" # "gpt-4o", "gpt-4o-mini"
        %run -i $aiforth

    and then you can start talking to AI.

        %ai hi! tell me a joke.
        %chat why it is funny ?

    注意: 行尾緊貼著 ? 在 JupyterlAB 是取得 help 的 magic 所以或前
    或後要多個空格以免打架。


    Usage
    ===========================================
    
    %f columbus :> config :> ['openai_api_type'] -->
    %f columbus :> access_token -->
    %ai tell me a joke
    %%ai 
       tell me a joke
    %f ai: tell me a joke
    %f chat: why is it funny? 
    %chat why is it not funny? 
    %f "" to chat_history \ clean chat history
    %f columbus :> __version__ --> # Columbus imported
    %f -1 .chat \ Pretty print the last chat turn

        
    How to debug %ai %chat commands 
    ==============================================
    
    %f @get_ipython --> # 先查這個，應該都有。
    %f @llm --> # 再查這個，可能就是 None 了 <--- Problem!
    %f see @llm # 有東西就沒問題了。
    %f help llm_wrapper \ @llm 的前一級有嗎？ 否則要進去查 peforth_llm。
    %f peforth_llm --> # 這就是 call client 的 llm() function 了。
    %f peforth_llm :> ("hi!") --> # llm() 可以這麼執行。

"""

import os
import peforth  # peforth.__version__ v1.33
from IPython.display import display, Markdown
# from IPython import get_ipython 這樣不行，用 %run -i %pathname 即可。
from columbus_api import Columbus, Config # Config().config
columbus = Columbus()  # columbus.__version__ v1.22
client, extra_headers = columbus.get_client()

# 從外面定義好 aiModel 才 %run 進來，否則用這裡的 default 值。
if 'aiModel' not in locals():
    aiModel = "gpt-4o-mini"

def llm(prompt):
    response = client.chat.completions.create(
        model=aiModel,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

peforth.dictate(r"""
    display constant display // ( -- obj ) Jupyternotebook display function
    Markdown constant Markdown // ( -- obj ) Jupyternotebook Markdown class
    columbus constant columbus // ( -- obj ) Columbus API
    get_ipython to @get_ipython // 把 get_ipython 介紹給 peforth
    llm constant peforth_llm // 把 python function llm() 介紹給 peforth
    : llm_wrapper trim peforth_llm :> (pop()) ;  // ( prompt -- complete ) 執行 llm()
    ' llm_wrapper to @llm \ 把 llm_wrapper 介紹給 peforth
    : .chat // ( chat_turn# -- ) Print a chat turn with Markdown rendering.
        1- display Markdown
        <py>
        display, Markdown = pop(1), pop()
        import re
        sections = re.split("---===---", dictate('chat_history').pop())
        display(Markdown(sections[pop()]))
        </py> ;
        ///  1 第一個 chat turn。
        /// -1 最後一個 chat turn。
    """);
# %ai You are aiFORTH, say Hi to the world.
