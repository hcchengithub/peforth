"""
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
            # "Llama3-8b-instruct"
            # "RootCauseAssistant"
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

    %ai introduce yourself please
    %ai where from ?
    %f "" to chat_history


"""

import os, peforth
from IPython.display import display, Markdown
# from IPython import get_ipython 這樣不行，用 %run -i %pathname 即可。
from columbus_api import Columbus
columbus = Columbus()

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
        modelname=aiModel,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    peforth.dictate("""
        peforth_llm constant peforth_llm // 把 OpenAI 某 llm 介紹給 peforth
        : llm_wrapper trim peforth_llm :> invoke(pop()).content ;  // llm_wrapper for OpenAI models
        ' llm_wrapper to @llm // 把 llm_wrapper 介紹給 peforth
        """);

if aiModel in ["Columbus4o","Columbus4o-mini"]:
    peforth_llm = columbus.get_llm_for_LangChain(
        modelname=({
            "Columbus35" : "gpt-35-turbo",
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
