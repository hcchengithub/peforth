#
# Python debugger in FORTH language for jupyternotebook 
#
# Usage: %run <this file>.py 
#
# In a jupyternotebook cell to initialize peforth environment. So we have, 
# bp    - breakpoints
# paste - run anything in clipboard at a breakpoint
# display-on display-off - turn on/off peforth STDOUT
# magic %f and %%f for peforth
# magic %%skip True / False / $python_variable to skip the cell 
#
# H.C. Chen 18:10 12/4/2021
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

        \ ------ %%skip magic ------------------------------------------------------------

            \
            \ Conditional skip jupyternotebook cells 
            \ https://stackoverflow.com/questions/26494747/simple-way-to-choose-which-cells-to-run-in-ipython-notebook-during-run-all
            \ 
            \ # Load the extension in your notebook:
            \ #   %load_ext <file name w/o .py> 以下咱直接執行 load_ipython_extension(get_ipython())
            \ 
            \ 
            \ Run the skip magic command in the cells you want to skip:               
            \                                                                         
            \   %%skip True  # skips cell                                              
            \   %%skip False # won't skip                                              
            \                                                                         
            \ You can use a variable to decide if a cell should be skipped by using $:
            \                                                                         
            \   should_skip = True                                                    
            \   %%skip $should_skip                                                   

            <py>
            def init_skip_magic(get_ipython):
                def skip(line, cell):
                    # Skips execution of the current line/cell if line evaluates to True.
                    if eval(line):
                        return
                    get_ipython().run_cell(cell)  # instead of get_ipython().ex(cell)

                def load_ipython_extension(shell):
                    # Registers the skip magic when the extension loads.
                    shell.register_magic_function(skip, 'line_cell')

                def unload_ipython_extension(shell):
                    # Unregisters the skip magic when the extension unloads.
                    del shell.magics_manager.magics['cell']['skip']

                load_ipython_extension(get_ipython()) # make the magic to start working 
            push(init_skip_magic)
            </py> constant init_skip_magic // Init %%skip magic. Usage: %f get_ipython init_skip_magic :: (pop())  

        \ ------ Redirect STDOUT to screen-buffer ------------------------------------------------------------
            py> float(vm.version)<=1.28 [if]

            \
            \ Redirect print() to screen-buffer 
            \ 	v1.28 版 built-in, v1.27 之前用 forth.py 加上。

            py: vm.forth['screen-buffer']=[""]
            code screen-buffer # ( -- ['string'] ) Screen buffer for STDOUT 
                push(vm.forth['screen-buffer']) end-code
                /// Enveloped in array for "access by reference"
            
            \   Defining a home made STDOUT substitution
            \   Usage guide 
            \     # Start redirection
            \     sys.stdout=Screenbuffer(vm.forth['screen-buffer'])
            \     
            \     # Print to screen when redirected
            \     sys.stdout.stdoutwas.write("-------1111-----")
            \     sys.stdout.stdoutwas.write("-------2222-----")
            \     
            \     # view screen buffer
            \     sys.stdout.view()
            \     
            \     # reset
            \     sys.stdout.reset()

            <py>
                class Screenbuffer:
                    def __init__(self,buf):
                        self.stdoutwas=sys.stdout
                        self.buffer=buf
                    def write(self, output_stream):
                        self.buffer[0] += output_stream
                    def view(self):
                        self.stdoutwas.write(self.buffer[0])
                    def reset(self):
                        sys.stdout=self.stdoutwas
                    def flush(self):
                        # self.buffer[0]=''
                        pass
                vm.Screenbuffer=Screenbuffer
            </py>

            : display-off // ( -- ) Redirect stdout to an empty screen-buffer
                py: sys.stdout=Screenbuffer(vm.forth['screen-buffer'])
                screen-buffer :: [0]="" ;

            : display-on // ( -- ) Redirect stdout back to what it was. screen-buffer has data during it was off.
                py: sys.stdout.reset() ;

            [then]
        \ ------ end of STDOUT redirection ------------------------------------------------------------
    [then] 
    '''
)

