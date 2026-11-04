\ peforth.f - peforth system default extensions and modules.
\ peforth 2.1.0

include base.f
include auxiliary.f
include herdr.f
include ai.f
include repl.f

\ --- Launch CLI or REPL if not headless ---
code ?repl
    yield from vm.call(vm.tick("?cli"))
    end-code
    // ( -- ) Launch CLI dispatcher or interactive REPL if not headless.
    /// Delegates to ?cli.
?repl

