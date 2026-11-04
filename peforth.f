\ peforth.f - peforth system default extensions and modules.
\ peforth 2.1.0

include base.f
include auxiliary.f
include herdr.f
include ai.f
include repl.f

\ --- Launch REPL if not headless ---
code ?repl
    if not vm.host.get("headless", False):
        yield from vm.call(vm.tick("repl"))
    end-code
    // ( -- ) Launch interactive REPL if not running in headless mode.
    /// Checks vm.host['headless']; if false, transfers execution to repl loop.
?repl
