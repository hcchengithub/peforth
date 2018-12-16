__author__ = 'hcchen'

import peforth
from ipykernel.kernelbase import Kernel

class peforthKernel(Kernel):
    implementation = 'peforth'
    implementation_version = '1.0'
    language = 'peforth'
    language_version = '0.1'
    language_info = {'mimetype': 'text/plain', 'name': 'peforth'}
    banner = "Ipeforth Kernel - one breakpoint to x-ray everything"

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        if not silent:
            peforth.vm.dictate("display-off")  
            peforth.vm.dictate(code)
            peforth.vm.dictate("display-on screen-buffer")
            code_result = peforth.vm.pop()[0]
            stream_content = {'name': 'stdout', 'text': code_result}
            self.send_response(self.iopub_socket, 'stream', stream_content)
        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=peforthKernel)
else:
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=peforthKernel)