# Walkthrough Giải Bài CTF Crypto: EaaS (Email as a Service)

Dưới đây là walkthrough chi tiết về cách tôi tư duy và giải bài CTF này. Tôi sẽ trình bày từng bước một, từ phân tích code đến xây dựng exploit, dựa trên lỗ hổng của AES-CBC malleability. Tôi sử dụng ngôn ngữ đơn giản, logic rõ ràng để bạn dễ theo dõi. Vì bạn yêu cầu dạng markdown để lưu, tôi cấu trúc với heading, bullet points và code blocks cho dễ đọc.

## Bước 1: Phân Tích Code Và Hiểu Vấn Đề
- **Đọc code server.py**: Code là một dịch vụ email đơn giản sử dụng AES-CBC để mã hóa/mã giải mã. Người dùng có email ngẫu nhiên dạng `random@notscript.sorcerer` (gọi là `E`, dài 29 bytes). Mục tiêu là lấy flag từ "email" gửi đến chính mình.
- **Các điểm chính**:
  - Password (plaintext `P`) phải là hex, độ dài bội 16, không chứa `@script.sorcerer` (gọi là `S`, 16 bytes) hoặc `E` làm substring.
  - Server mã hóa `P` thành ciphertext `C` (AES-CBC với key/IV random, nhưng dùng chung cho decrypt sau).
  - Để lấy flag: Chọn option 2, gửi ciphertext `C'` (encrypted email), decrypt thành `T`.
  - `T` phải kết thúc bằng `S` (kiểm tra `user_email[-16:] == S`).
  - `send_email(T)`: Split `T` bằng `,` thành recipients, nếu có recipient == `E`, set `has_flag=True`.
  - Sau đó chọn option 1 để đọc flag.
- **Tư duy ban đầu**: Không thể trực tiếp gửi `E + S` vì `P` không được chứa `E` hoặc `S`. Cần exploit malleability của CBC: Thay đổi ciphertext để thay đổi plaintext mà không biết key, nhưng sẽ garble (làm hỏng) block trước đó.
- **Mục tiêu**: Xây dựng `T` chứa `E` như một recipient (ví dụ: `dummy, E, dummy + S`), nhưng `P` phải là phiên bản "flipped" (thay đổi vài byte) để tránh cấm, rồi dùng malleability để "sửa" lại khi decrypt.

## Bước 2: Hiểu Về AES-CBC Malleability
- **CBC decryption**: Plaintext block `T_i = decrypt(C_i) XOR C_{i-1}` (với C_0 = IV, nhưng ở đây IV chung).
- **Malleability**: Để thay đổi `T_i` bằng delta `D`, XOR `D` vào `C_{i-1}`. Kết quả: `T_i` thay đổi đúng `D`, nhưng `T_{i-1}` bị garble (trở thành random).
- **Tư duy áp dụng**: Tôi cần `T` có cấu trúc split đúng (chứa `E` nguyên vẹn), kết thúc `S`. Nhưng `P` không chứa `E`/`S`, nên flip vài byte ở `P`, rồi dùng malleability để flip lại ở decryption (garble các block dummy không quan trọng).
- **Rủi ro**: Garble có thể chứa `,`, làm split thêm recipients, nhưng miễn không match `E` là ok. Chọn flip ở vị trí an toàn.

## Bước 3: Xây Dựng Cấu Trúc Mong Muốn Cho `T`
- **Yêu cầu**: `T` dài bội 16 (ví dụ 80 bytes = 5 blocks). Phải split bằng `,` thành recipients, trong đó có đúng `E`.
- **Cấu trúc tôi chọn** (80 bytes):
  - Block 1 (0-15): Dummy1 (garble sau, ví dụ `\x00*16`).
  - Block 2 (16-31): `,` + E[0:15] (15 bytes đầu của `E`).
  - Block 3 (32-47): E[15:29] (14 bytes sau) + `,` + `a` (1 byte dummy để align).
  - Block 4 (48-63): Dummy2 (garble sau).
  - Block 5 (64-79): `S` (`@script.sorcerer`).
- **Lý do**:
  - `,` trước/sau `E` để isolate `E` khi split.
  - Dummy blocks để garble không ảnh hưởng (garble thành random recipients, nhưng không match `E` vì `E` dài 29 bytes, random ít trùng).
  - Tổng: 16 (dummy1) + 1(,) + 29(E) + 1(,) + 1(a) + 16(dummy2) + 16(S) = 80 bytes.
- **Split kết quả**: Recipients như [garble, E, a + garble + S (nhưng S ở cuối, không ảnh hưởng vì check recipients riêng)] – quan trọng là có `E`.

## Bước 4: Xây Dựng Plaintext `P` (Password) Để Tránh Cấm
- **Vấn đề**: `P` không được chứa `E` hoặc `S` làm substring.
- **Giải pháp**: Flip 1 byte ở phần `E` và `S` trong `P` (XOR với 1 để thay đổi).
  - Flip ở block 2: Vị trí cuối của E[0:15] (byte thứ 15 trong block 2, tức E[14]).
  - Flip ở block 5: Byte đầu của `S` (`@` thành `#` hoặc tương tự).
- **Lý do flip ít**: Chỉ cần thay đổi substring để không match, flip 1 byte đủ. Vị trí cuối để tránh overlap substring.
- **Xác nhận**: `P` giờ không chứa `E` (vì phần đầu E bị flip) hoặc `S` (bị flip). Gửi `P.hex()` làm password, nhận `C`.

## Bước 5: Tính Delta Và Modify `C` Thành `C'`
- **Delta cho E**: `delta_E = P_block2 XOR T_block2` (chỉ khác 1 byte).
- **Delta cho S**: `delta_S = P_block5 XOR T_block5` (chỉ khác 1 byte).
- **Áp dụng malleability**:
  - Để sửa block 2: XOR `delta_E` vào block 1 của `C` (garble block 1).
  - Để sửa block 5: XOR `delta_S` vào block 4 của `C` (garble block 4).
- **Kết quả `C'`**: Decrypt thành `T` mong muốn (với block 1 và 4 garble, nhưng ok vì dummy).
- **Tư duy toán**: XOR là phép toán reversible. Vì delta chỉ 1 byte, phần còn lại delta=0 (không thay đổi).

## Bước 6: Interact Với Server Và Lấy Flag
- Connect server (dùng pwntools cho remote/process).
- Đọc `E` từ welcome.
- Build `P` như trên, gửi hex.
- Nhận `C` hex, parse thành bytes.
- Tính deltas, build `C'`.
- Chọn 2, gửi `C'.hex()`.
- Server decrypt `C'` thành `T`, check cuối `S`, split và gửi đến `E` (set has_flag).
- Chọn 1, đọc flag từ "Body: {flag}".

## Bước 7: Edge Cases Và Debug Tư Duy
- **Nếu garble chứa `,`**: Split thêm, nhưng recipients ngắn (16 bytes) không match `E` (29 bytes), và `E` vẫn intact nhờ `,` bao quanh.
- **Align lengths**: Luôn multiple of 16, dùng dummy để pad.
- **Flip position**: Chọn không phải `@` hoặc phần đặc biệt để tránh substring vẫn match (test local nếu cần).
- **Script tự động**: Dùng pwntools để handle I/O, tránh lỗi manual.

## Script Python Để Giải (Dựa Trên Tư Duy Trên)
Dưới đây là script đầy đủ, bạn có thể copy và run với `pip install pwntools`.

```python
from pwn import *

# Thay bằng remote('host', port) khi connect thực
# r = remote('example.com', 12345)
r = process('./server.py')  # Test local

# Đọc email
r.recvuntil(b'Your Email is: ')
email = r.recvline().decode().strip()
E = email.encode()
print(f'Email: {email}')
assert len(E) == 29

S = b'@script.sorcerer'
assert len(S) == 16

# Build T parts (mong muốn)
dummy1 = b'\x00' * 16
part1 = b',' + E[:15]
part2 = E[15:] + b',' + b'a'
dummy2 = b'\x00' * 16
part3 = S

# Flip positions
flip_E_pos = 15  # Trong part1 (byte cuối, E[14])
flip_S_pos = 0   # Trong part3 (byte đầu '@')

# Build P với flips
P_part1 = part1[:flip_E_pos] + bytes([part1[flip_E_pos] ^ 1]) + part1[flip_E_pos + 1:]
P_part3 = part3[:flip_S_pos] + bytes([part3[flip_S_pos] ^ 1]) + part3[flip_S_pos + 1:]
P = dummy1 + P_part1 + part2 + dummy2 + P_part3

# Gửi password
r.recvuntil(b'Enter secure password (in hex): ')
r.sendline(P.hex().encode())

# Nhận C
r.recvuntil(b'Please use this key for future login: ')
enc_hex = r.recvline().decode().strip()
C = bytes.fromhex(enc_hex)
assert len(C) == 80

# Tính deltas
delta_E = bytes([a ^ b for a, b in zip(P_part1, part1)])
delta_S = bytes([a ^ b for a, b in zip(P_part3, part3)])

# Build C blocks
C_blocks = [C[i*16:(i+1)*16] for i in range(5)]

# Modify thành C'
C_prime_blocks = C_blocks[:]
C_prime_blocks[0] = bytes([a ^ b for a, b in zip(C_blocks[0], delta_E)])
C_prime_blocks[3] = bytes([a ^ b for a, b in zip(C_blocks[3], delta_S)])
C_prime = b''.join(C_prime_blocks)

# Interact
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
```

## Kết Luận Tư Duy
- **Tại sao thành công**: Khai thác malleability để "cheat" asserts ở plaintext, nhưng decrypt ra đúng mong muốn.
- **Bài học**: CBC dễ bị tamper nếu attacker control ciphertext. Luôn verify integrity (như HMAC).
- Nếu bạn run script và gặp lỗi, check lengths hoặc flip positions (thử flip byte khác nếu substring vẫn match).

Hy vọng walkthrough này chi tiết và hữu ích! Nếu cần chỉnh sửa, cứ hỏi nhé. 😊