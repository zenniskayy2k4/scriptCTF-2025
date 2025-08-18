#!/usr/bin/env python3
from pwn import *

# =========================================================
#                  SETUP
# =========================================================
HOST = "play.scriptsorcerers.xyz" 
PORT = 10009 

# pwnlib context setting để nhất quán
context.arch = 'amd64'
context.endian = 'little'

# Payload xây dựng bằng pwnlib functions cho an toàn
payload = b""
payload += b"\x10\x01" + p32(0)      # mov r1, 0           (offset 0x00, len 6)
payload += b"\xa0\x00\x01"             # cmp r0, r1          (offset 0x06, len 3)
payload += b"\xe0" + p32(0x15)         # jz IS_ZERO(0x15)    (offset 0x09, len 5)
                                        # Next instruction at 0x0e
# --- NOT_ZERO path ---
payload += b"\x10\x00" + p32(0)      # mov r0, 0           (offset 0x0e, len 6)
payload += b"\xf0"                     # halt                (offset 0x14, len 1)
# --- IS_ZERO path --- (starts at 0x15)
payload += b"\x10\x00" + p32(1)      # mov r0, 1           (offset 0x15, len 6)
payload += b"\xf0"                     # halt                (offset 0x1b, len 1)


def solve():
    io = remote(HOST, PORT)
    
    log.info(f"Payload length: {len(payload)} bytes")
    log.info(f"Payload (hex): {payload.hex()}")
    
    # Quan trọng: Thử dùng send() thay vì sendline()
    log.info("Sending payload...")
    io.send(payload)
    
    log.info("Waiting for flag...")
    
    try:
        response = io.recvall(timeout=5)
        if response:
            print("Response from server:")
            print(response.decode(errors='ignore'))
        else:
            print("Server closed connection with no response. Payload likely failed.")
    except Exception as e:
        log.warning(f"An error occurred: {e}")

if __name__ == "__main__":
    solve()