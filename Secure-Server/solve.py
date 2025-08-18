from pwn import xor

enc_hex  = "151e71ce4addf692d5bac83bb87911a20c39b71da3fa5e7ff05a2b2b0a83ba03" # Dữ liệu đầu tiên client gửi (màu đỏ)
enc2_hex = "e1930164280e44386b389f7e3bc02b707188ea70d9617e3ced989f15d8a10d70" # Dữ liệu server gửi (màu xanh)
dec_hex  = "87ee02c312a7f1fef8f92f75f1e60ba122df321925e8132068b0871ff303960e" # Dữ liệu thứ hai client gửi (màu đỏ)

# Chuyển đổi từ hex string sang bytes
enc = bytes.fromhex(enc_hex)
enc2 = bytes.fromhex(enc2_hex)
dec = bytes.fromhex(dec_hex)

# Áp dụng công thức S = enc ⊕ enc2 ⊕ dec
# pwn.xor có thể nhận nhiều tham số
secret = xor(enc, enc2, dec)

# In ra secret, có thể nó là flag
try:
    print("Secret (flag):", secret.decode())
except UnicodeDecodeError:
    print("Secret (hex):", secret.hex())