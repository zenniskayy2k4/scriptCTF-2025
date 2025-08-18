from pwn import *
import math

# --- Cấu hình ---
# Dán giá trị bạn nhận được từ lần chạy đầu tiên vào đây.
# Ban đầu, để giá trị này là None.
val1 = None 

# --- Kết nối ---
# Thay đổi host và port nếu cần
r = remote('play.scriptsorcerers.xyz', 10153)
# r = process(['python3', 'chall.py'])

# --- Logic ---
if val1 is None:
    # Lần chạy đầu tiên
    log.info("Lần chạy 1: Lấy giá trị đầu tiên.")
    num1 = 2**1024
    
    # Chờ prompt "Provide a number: " và gửi số
    r.sendlineafter(b'Provide a number: ', str(num1).encode())
    
    # --- SỬA ĐỔI Ở ĐÂY ---
    # Đọc một dòng duy nhất chứa kết quả modulo
    rem1_line = r.recvline()
    rem1 = int(rem1_line.strip())
    # --- KẾT THÚC SỬA ĐỔI ---
    
    result = num1 - rem1
    log.success(f"Giá trị 1 (num1 - rem1): {result}")
    log.info("Chạy lại script và dán giá trị trên vào biến 'val1'.")
    
    # Gửi một đoán sai để kết thúc chương trình
    r.sendlineafter(b'Guess: ', b'1')

else:
    # Lần chạy thứ hai
    log.info("Lần chạy 2: Lấy giá trị thứ hai và tính GCD.")
    num2 = 2**1024 + 1
    r.sendlineafter(b'Provide a number: ', str(num2).encode())

    # --- SỬA ĐỔI Ở ĐÂY ---
    rem2_line = r.recvline()
    rem2 = int(rem2_line.strip())
    # --- KẾT THÚC SỬA ĐỔI ---
    
    val2 = num2 - rem2
    log.info(f"Giá trị 2 (num2 - rem2): {val2}")

    # Tính GCD để tìm secret
    secret_guess = math.gcd(val1, val2)
    log.success(f"Đoán secret là: {secret_guess}")

    # Gửi secret đã tìm được
    r.sendlineafter(b'Guess: ', str(secret_guess).encode())

    # Nhận flag
    flag = r.recvuntil(b'}').strip().decode()
    log.success(f"Flag: {flag}")

r.close()