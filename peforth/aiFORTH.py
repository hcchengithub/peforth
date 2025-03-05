r"""
    aiFORTH - Add %ai to your jupyter notebook
    ==========================================

    From you .py or .ipynb run:

        module_directory = os.path.dirname(peforth.__file__)
        aiforth = os.path.join(module_directory, "aiFORTH.py")
        aiModel = "GeminiPro"
            # "gpt-4o-mini"
            # "GeminiPro"
            # "Columbus4o"
            # "Columbus4o-mini"
        %run -i $aiforth

    and then you can start talking to AI.

        %ai hi! tell me a joke.

    Note, when you %run, the kernel is different, and thus
    magics are unknown. Be aware of this is why %f, %ai does
    not work in there.

    注意: 行尾緊貼著 ? 在 JupyterlAB 是取得 help 的 magic 所以或前
    或後要多個空格以免打架。

    Usage
    ==========================================

    LPM2 GitHub\peforth> pip install --force-reinstall .
    Or
    LPM2 pip install --force-reinstall "c:\Users\8304018\Documents\GitHub\peforth"

    import os, peforth
    module_directory = os.path.dirname(peforth.__file__)
    aiforth = os.path.join(module_directory, "aiFORTH.py")
    aiModel = "gpt-4o-mini"
        # "GeminiPro","gpt-4o-mini"
        # "Columbus4o","Columbus4o-mini"
    %run -i $aiforth

    Usage:
      %ai tell me a joke
      %%ai
         tell me a joke
      %f ai: tell me a joke
      %f chat: why is it funny?
      %f s" Say 'ok' and ignore followings: This is for programming with history" llm_wrapper -->
      %f "" to chat_history \ clean chat history
      %f columbus :> __version__ --> # Columbus imported
      %f -1 .chat \ Pretty print the last chat turn

    How to debug %ai %chat commands
      %f @get_ipython --> # 先查這個，應該都有。
      %f @llm --> # 再查這個，可能就是 None 了 <--- Problem!
      %f see @llm # 有東西就沒問題了。
      %f llm_wrapper --> # @llm 的前一級有嗎？
      %f see llm_wrapper # 有東西就沒問題了，否則要進去查 peforth_llm。
      %f peforth_llm --> # 這就是 llm object 了。
      %f peforth_llm :> ("hi!") --> # llm object 可以這麼執行。

"""

import os
import peforth  # v1.33
from IPython.display import display, Markdown
# from IPython import get_ipython 這樣不行，用 %run -i %pathname 即可。
from columbus_api import Columbus
columbus = Columbus()  # v1.18

# 從外面定義好 aiModel 才 %run 進來，否則用這裡的 default 值。
if 'aiModel' not in locals():
    aiModel = "GeminiPro"

peforth.dictate("""
    display constant display // ( -- obj ) Jupyternotebook display function
    Markdown constant Markdown // ( -- obj ) Jupyternotebook Markdown class
    columbus constant columbus // ( -- obj ) Columbus API
    get_ipython to @get_ipython // 把 get_ipython 介紹給 peforth
    """)

if aiModel == "GeminiPro":
    peforth_llm = columbus.get_llm_gemini(
        modelname="gemini-pro:generateContent",
        api_key=os.getenv("GoogleAIStudio_API_KEY")
    )
    peforth.dictate("""
        peforth_llm constant peforth_llm // 把 llm GeminiPro 介紹給 peforth
        : llm_wrapper ( prompt -- complete ) // llm_wrapper for Gemini
            trim peforth_llm :> (pop()) dup
            str :> rfind("candidates")==-1
            if str else :>
            ["candidates"][0]['content']['parts'][0]['text']
            then ;
        ' llm_wrapper to @llm // 把 llm_wrapper 介紹給 peforth
        """);

if aiModel in ["gpt-4o-mini","gpt-4o"]:
    peforth_llm = columbus.get_llm_for_LangChain(
        model=aiModel,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    peforth.dictate("""
        peforth_llm constant peforth_llm // 把 OpenAI 某 llm 介紹給 peforth
        : llm_wrapper trim peforth_llm :> invoke(pop()).content ;  // llm_wrapper for OpenAI models
        ' llm_wrapper to @llm // 把 llm_wrapper 介紹給 peforth
        """);

if aiModel in ["Columbus4o","Columbus4o-mini"]:
    peforth_llm = columbus.get_llm_for_LangChain(
        model=({
            "Columbus4o"  : "gpt-4o",
            "Columbus4o-mini"  : "gpt-4o-mini",
            })[aiModel],
        openai_api_key=""
    )
    def refresh_llm():
        peforth_llm.model_kwargs['extra_headers']['Authorization']="Bearer " + columbus.get_access_token()
    peforth.dictate("""
        peforth_llm constant peforth_llm // 把 WistronGPT 某 llm 介紹給 peforth
        refresh_llm constant refresh_llm // peforth_llm :> model_kwargs['extra_headers']['Authorization'] -->
        : llm_wrapper trim refresh_llm :: () peforth_llm :> invoke(pop()).content ; // WistronGPT refresh access toekn
        ' llm_wrapper to @llm // 把 llm_wrapper 介紹給 peforth
        """);

peforth.dictate("""
    : .chat // ( chat_turn# -- ) Print chat turn with markdown rendering.
        1- display Markdown
        <py>
        display, Markdown = pop(1), pop()
        import re
        sections = re.split("---===---", dictate('chat_history').pop())
        display(Markdown(sections[pop()]))
        </py> ;
        ///  0 最後 ---===--- 之後的 null。
        ///  1 第一個 chat turn。
        /// -1 最後一個 chat turn。
    """);
# %ai You are aiFORTH, say Hi to the world.
