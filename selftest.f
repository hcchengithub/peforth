\ selftest.f - peforth comprehensive self-test suite
\ Verifies Forth vocabulary, control structures, stack operations, and Python interop.

: ?assert ( flag msg -- )
    swap if
        drop
    else
        cr ." [FAIL] Assertion failed: " . cr
        abort
    then ;
    last :: safe=True

\ =====================================================================
\ 1. Top-Level Tests (Defining Words & Interpreted Words)
\ =====================================================================

123 constant _TEST_CONST
_TEST_CONST 123 = s" constant" ?assert

variable _TEST_VAR
456 _TEST_VAR !
_TEST_VAR @ 456 = s" variable @" ?assert
789 _TEST_VAR !  _TEST_VAR @ 789 = s" variable !" ?assert

50 value _TEST_VAL
_TEST_VAL 50 = s" value initial" ?assert
100 to _TEST_VAL  _TEST_VAL 100 = s" value to" ?assert

\ =====================================================================
\ 2. Main Self-Test Definition
\ =====================================================================

: selftest ( -- )
    cr ." === Running peforth Forth Self-Test ===" cr

    \ --- Stack Manipulation ---
    1 2 swap 1 = s" swap top" ?assert 2 = s" swap second" ?assert
    5 dup + 10 = s" dup" ?assert
    1 2 over 1 = s" over" ?assert drop drop
    1 2 3 rot 1 = s" rot top" ?assert 3 = s" rot second" ?assert 2 = s" rot third" ?assert
    1 2 3 -rot 2 = s" -rot top" ?assert 1 = s" -rot second" ?assert 3 = s" -rot third" ?assert
    1 2 nip 2 = s" nip" ?assert
    1 2 2dup 2 = s" 2dup top" ?assert 1 = s" 2dup 2nd" ?assert 2 = s" 2dup 3rd" ?assert 1 = s" 2dup 4th" ?assert
    1 2 3 4 2drop 2 = s" 2drop top" ?assert 1 = s" 2drop 2nd" ?assert
    10 20 30 depth 3 = s" depth" ?assert dropall depth 0 = s" dropall" ?assert
    10 20 30 0 pick 30 = s" 0 pick" ?assert drop drop drop
    10 20 30 2 pick 10 = s" 2 pick" ?assert drop drop drop
    10 20 30 2 roll 10 = s" 2 roll" ?assert drop drop
    1 2 3 4 5 -3 slice count 3 = s" slice count" ?assert drop drop drop

    \ --- Return Stack and Temporary Stack ---
    42 >r r@ 42 = s" r@" ?assert r> 42 = s" r>" ?assert
    99 >r rdrop depth 0 = s" rdrop" ?assert
    77 >t t@ 77 = s" t@" ?assert t> 77 = s" t>" ?assert

    \ --- Arithmetic and Logic ---
    10 20 + 30 = s" +" ?assert
    50 20 - 30 = s" -" ?assert
    6 7 * 42 = s" *" ?assert
    84 2 / 42 = s" /" ?assert
    17 5 mod 2 = s" mod" ?assert
    9 1+ 10 = s" 1+" ?assert
    10 1- 9 = s" 1-" ?assert
    10 2+ 12 = s" 2+" ?assert
    12 2- 10 = s" 2-" ?assert
    -42 abs 42 = s" abs neg" ?assert 42 abs 42 = s" abs pos" ?assert
    42 negate -42 = s" negate" ?assert
    15 25 max 25 = s" max" ?assert
    15 25 min 15 = s" min" ?assert
    10 10 = s" = true" ?assert 10 20 = not s" = false" ?assert
    10 20 <> s" <> true" ?assert 10 10 <> not s" <> false" ?assert
    10 20 != s" != true" ?assert 10 10 != not s" != false" ?assert
    1 1 == s" == true" ?assert 1 0 == not s" == false" ?assert
    5 10 < s" < true" ?assert 10 5 < not s" < false" ?assert
    10 5 > s" > true" ?assert 5 10 > not s" > false" ?assert
    5 5 <= s" <= true" ?assert 6 5 <= not s" <= false" ?assert
    5 5 >= s" >= true" ?assert 4 5 >= not s" >= false" ?assert
    0 0= s" 0= true" ?assert 5 0= not s" 0= false" ?assert
    -5 0< s" 0< true" ?assert 5 0< not s" 0< false" ?assert
    5 1 10 within s" within true" ?assert 15 1 10 within not s" within false" ?assert

    \ --- Bitwise and Boolean Logic ---
    true not false = s" not" ?assert
    true true and s" and true" ?assert true false and not s" and false" ?assert
    true false or s" or true" ?assert false false or not s" or false" ?assert
    12 10 AND 8 = s" AND" ?assert
    12 10 OR 14 = s" OR" ?assert
    12 10 XOR 6 = s" XOR" ?assert
    1 4 << 16 = s" <<" ?assert
    16 4 >> 1 = s" >>" ?assert

    \ --- Strings and Data Types ---
    s" hello" count 5 = s" string count" ?assert drop
    s"   spaced   " trim s" spaced" = s" trim" ?assert
    char X s" X" = s" char" ?assert
    BL s"  " = s" BL" ?assert
    CR py> chr(10) = s" CR" ?assert
    s" 42" int 42 = s" int" ?assert
    s" 3.14" float 3.14 = s" float" ?assert
    1 bool true = s" bool" ?assert
    42 str s" 42" = s" str" ?assert

    \ --- Control Flow Structures ---
    5 0 > if 100 else 200 then 100 = s" if-else true branch" ?assert
    -5 0 > if 100 else 200 then 200 = s" if-else false branch" ?assert

    \ for ... next loop sum
    0 5 for r@ + next 15 = s" for ... next loop sum" ?assert

    \ begin ... while ... repeat
    0 5 begin ?dup while dup rot + swap 1- repeat 15 = s" begin-while-repeat sum" ?assert

    \ case structure
    1 case 1 of 111 endof 2 of 222 endof 999 swap endcase 111 = s" case branch 1" ?assert
    2 case 1 of 111 endof 2 of 222 endof 999 swap endcase 222 = s" case branch 2" ?assert
    3 case 1 of 111 endof 2 of 222 endof 999 swap endcase 999 = s" case default" ?assert

    \ --- Python Interoperability ---
    py> 6*7 42 = s" py> expr" ?assert
    s" HELLO" :> lower() s" hello" = s" :> method call" ?assert

    cr ." [PASS] All Forth assertions completed successfully." cr
    ;
    last :: safe=True

\ Run self-test immediately on include
selftest
