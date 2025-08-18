from pwn import *

r = remote('play.scriptsorcerers.xyz', 10108)

# Read welcome and email
r.recvuntil(b'Your Email is: ')
email = r.recvline().decode().strip()
E = email.encode()
print(f'Email: {email}')
assert len(E) == 29

S = b'@script.sorcerer'
assert len(S) == 16

# Define blocks for desired T
dummy1 = b'\x00' * 16
part1 = b',' + E[:15]
part2 = E[15:] + b',' + b'a'
dummy2 = b'\x00' * 16
part3 = S

# Flip positions and values (XOR 1 to flip)
flip_E_pos = 15  # Position in part1 (last byte, E[14])
flip_S_pos = 0   # Position in part3 (first byte '@')

# Build P blocks with flips
P_part1 = part1[:flip_E_pos] + bytes([part1[flip_E_pos] ^ 1]) + part1[flip_E_pos + 1:]
P_part3 = part3[:flip_S_pos] + bytes([part3[flip_S_pos] ^ 1]) + part3[flip_S_pos + 1:]
P = dummy1 + P_part1 + part2 + dummy2 + P_part3

# Send password hex
r.recvuntil(b'Enter secure password (in hex): ')
r.sendline(P.hex().encode())

# Read encrypted_pass
r.recvuntil(b'Please use this key for future login: ')
enc_hex = r.recvline().decode().strip()
C = bytes.fromhex(enc_hex)
assert len(C) == 80

# Compute deltas
delta_E = bytes([a ^ b for a, b in zip(P_part1, part1)])
delta_S = bytes([a ^ b for a, b in zip(P_part3, part3)])

# Build C blocks
C_blocks = [C[i*16:(i+1)*16] for i in range(5)]

# Modify C to C'
C_prime_blocks = C_blocks[:]
C_prime_blocks[0] = bytes([a ^ b for a, b in zip(C_blocks[0], delta_E)])
C_prime_blocks[3] = bytes([a ^ b for a, b in zip(C_blocks[3], delta_S)])
C_prime = b''.join(C_prime_blocks)

r.recvuntil(b'Enter your choice: ')
r.sendline(b'2')

r.recvuntil(b'Enter encrypted email (in hex): ')
r.sendline(C_prime.hex().encode())

r.recvuntil(b'Email sent!')

r.recvuntil(b'Enter your choice: ')
r.sendline(b'1')

r.recvuntil(b'Body: ')
flag = r.recvline().decode().strip()
print(f'Flag: {flag}')

r.close()