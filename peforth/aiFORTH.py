"""
    aiFORTH - Add %ai to your jupyter notebook
    ==========================================

    From you .py or .ipynb run:

        %run -i "C:\\...\\peforth\\notebook\\aiFORTH.py"

    and then you can start talking to AI.

        %ai hi! tell me a joke.

    Note, when you %run, the kernel is different, and thus
    magics are unknown. Be aware of this is why %f, %ai does
    not work in there.
"""

import os, peforth
from IPython.display import display, Markdown
# from IPython import get_ipython 這樣不行，用 %run -i %pathname 即可。
from columbus_api import Columbus
columbus = Columbus()

peforth.dictate("""
    display constant display // ( -- obj ) Jupyternotebook display function
    Markdown constant Markdown // ( -- obj ) Jupyternotebook Markdown class
    get_ipython to @get_ipython \ 把 get_ipython 介紹給 peforth
    """)

# Gemini Pro ------
peforth_llm = columbus.get_llm_gemini(
    modelname="gemini-pro:generateContent",
    api_key=os.getenv("GoogleAIStudio_API_KEY")
)
peforth.dictate("""
    peforth_llm constant llm_function \ 把 llm 介紹給 peforth
    : llm_wrapper ( prompt -- complete ) // llm_wrapper for Gemini
        trim llm_function :> (pop()) dup
        str :> rfind("candidates")==-1
        if str else :>
        ["candidates"][0]['content']['parts'][0]['text']
        then ;
    ' llm_wrapper to @llm \ 把 llm_wrapper 介紹給 peforth
    """);
# Gemini Pro ------

peforth.dictate("""
    : .chat // ( chat turn# -- ) Print chat turn with markdown rendering.
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
# %ai: You are aiFORTH, say Hi to the world.
