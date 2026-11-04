\ peforth.f - peforth system default extensions and modules.

include ai.f
include base.f
include repl.f

\ --- Launch REPL if not headless ---
code ?repl
    if not vm.host.get("headless", False):
        yield from vm.call(vm.tick("repl"))
    end-code
?repl
