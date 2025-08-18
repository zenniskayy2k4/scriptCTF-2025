from pwn import *

# --- Kết nối ---
# Cập nhật lại port đúng của challenge
r = remote('play.scriptsorcerers.xyz', 10103) 
# r = process(['python3', 'chall.py'])

# 1. Chọn một số num lớn hơn một chút so với giới hạn trên của secret
# secret < 2^256, vậy chúng ta chọn num = 2^256.
num = 2**256
log.info(f"Gửi số num = 2^256")
r.sendlineafter(b'Provide a number: ', str(num).encode())

# 2. Nhận kết quả modulo
rem_line = r.recvline()
rem = int(rem_line.strip())
log.info(f"Nhận được remainder: {rem}")

# 3. Suy ra secret
# Vì 2^255 <= secret < 2^256, khi ta thực hiện phép chia:
# num = q * secret + rem
# 2^256 = q * secret + rem
# Thương số q phải bằng 1.
# Do đó, secret = 2^256 - rem.
secret_guess = num - rem
log.success(f"Tìm thấy secret: {secret_guess}")
log.info(f"Độ dài bit của secret: {secret_guess.bit_length()}")

# 4. Gửi secret và nhận flag
r.sendlineafter(b'Guess: ', str(secret_guess).encode())

# Đọc đến khi nhận được '}' để đảm bảo lấy hết flag
try:
    flag = r.recvuntil(b'}').strip().decode()
    log.success(f"Flag: {flag}")
except EOFError:
    log.error("Đoán sai, server đã đóng kết nối.")
    log.info("Output từ server: " + r.recvall().decode())

r.close()