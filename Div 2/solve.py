from pwn import *

# --- Cấu hình kết nối ---
# Thay đổi host và port nếu cần
r = remote('play.scriptsorcerers.xyz', 10097)
# r = process(['python3', 'chall.py'])

# --- Khởi tạo khoảng tìm kiếm ---
lower_bound = 1 << 127
upper_bound = (1 << 128) - 1

log.info(f"Initial range: [{lower_bound}, {upper_bound}]")

# --- Vòng lặp tìm kiếm nhị phân ---
while lower_bound < upper_bound:
    # 1. Chọn lựa chọn 1 để cung cấp số
    r.sendlineafter(b'Choice: ', b'1')

    # 2. Chọn một số N để truy vấn.
    # Chúng ta có thể chọn một số cố định 128-bit như 2**127
    # hoặc điểm giữa của khoảng hiện tại.
    # Chọn điểm giữa sẽ hội tụ nhanh hơn.
    n_to_send = (lower_bound + upper_bound) // 2
    
    # Đảm bảo n_to_send là số 128-bit
    if n_to_send.bit_length() != 128:
        n_to_send = lower_bound # Nếu điểm giữa không phải 128-bit, dùng cận dưới

    log.info(f"Sending number: {n_to_send}")
    r.sendlineafter(b'Enter a number: ', str(n_to_send).encode())

    # 3. Nhận kết quả k = floor(secret / N)
    k = int(r.recvline().strip())
    log.info(f"Received k = {k}")

    # 4. Cập nhật khoảng tìm kiếm dựa trên bất đẳng thức
    # k * N <= secret < (k + 1) * N
    new_lower = k * n_to_send
    new_upper = (k + 1) * n_to_send - 1

    lower_bound = max(lower_bound, new_lower)
    upper_bound = min(upper_bound, new_upper)

    log.info(f"New range: [{lower_bound}, {upper_bound}]")
    log.info(f"Range size: {upper_bound - lower_bound}")

# --- Giai đoạn cuối: Đoán số bí mật ---
# Khi vòng lặp kết thúc, lower_bound == upper_bound == secret
secret_guess = lower_bound
log.success(f"Secret found: {secret_guess}")

# Chọn lựa chọn 2
r.sendlineafter(b'Choice: ', b'2')

# Gửi số bí mật đã tìm được
r.sendlineafter(b'Enter secret number: ', str(secret_guess).encode())

# Nhận và in flag
flag = r.recvline().strip().decode()
log.success(f"Flag: {flag}")

r.close()