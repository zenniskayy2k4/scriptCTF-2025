from Crypto.Cipher import AES
from tqdm import tqdm

def generate_aes_key(key_bytes):
    assert len(key_bytes) == 2
    binary_string = bin(key_bytes[0])[2:].zfill(8) + bin(key_bytes[1])[2:].zfill(8)
    return binary_string.encode()

# --- Dữ liệu từ pcap ---
enc_hex = "19574ac010cc9866e733adc616065e6c019d85dd0b46e5c2190c31209fc57727"
enc2_hex = "0239bcea627d0ff4285a9e114b660ec0e97f65042a8ad209c35a091319541837"
dec_hex = "4b3d1613610143db984be05ef6f37b31790ad420d28e562ad105c7992882ff34"

enc = bytes.fromhex(enc_hex)
enc2 = bytes.fromhex(enc2_hex)
dec = bytes.fromhex(dec_hex)

# --- CHIA DỮ LIỆU THÀNH CÁC KHỐI 16-BYTE ---
enc_block1, enc_block2 = enc[:16], enc[16:]
enc2_block1, enc2_block2 = enc2[:16], enc2[16:]
dec_block1, dec_block2 = dec[:16], dec[16:]

# --- PHẦN 1: Tìm k1 và k2 với xác thực ---
print("[*] Performing VERIFIED MitM attack for k1 and k2 using dec and enc2...")
lookup_k1 = {}
print("[+] Building lookup table for E_k1(dec_block1)...")
for i in tqdm(range(256 * 256)):
    k1_bytes = i.to_bytes(2, 'big')
    cipher = AES.new(generate_aes_key(k1_bytes), AES.MODE_ECB)
    lookup_k1[cipher.encrypt(dec_block1)] = k1_bytes

print("[+] Searching for a match and verifying on block 2...")
found_k1, found_k2 = None, None
for i in tqdm(range(256 * 256)):
    k2_bytes = i.to_bytes(2, 'big')
    cipher2 = AES.new(generate_aes_key(k2_bytes), AES.MODE_ECB)
    decrypted_with_k2_block1 = cipher2.decrypt(enc2_block1)
    
    if decrypted_with_k2_block1 in lookup_k1:
        candidate_k1 = lookup_k1[decrypted_with_k2_block1]
        candidate_k2 = k2_bytes
        
        # --- BƯỚC XÁC THỰC ---
        cipher1_verify = AES.new(generate_aes_key(candidate_k1), AES.MODE_ECB)
        if cipher1_verify.encrypt(dec_block2) == cipher2.decrypt(enc2_block2):
            found_k1 = candidate_k1
            found_k2 = candidate_k2
            print(f"\n[+] VERIFIED k1: {found_k1.hex()}")
            print(f"[+] VERIFIED k2: {found_k2.hex()}")
            break

if not found_k1: exit("[-] Could not find k1 and k2.")

# --- PHẦN 2: Tìm k3 và k4 với xác thực ---
print("\n[*] Performing VERIFIED MitM attack for k3 and k4...")
lookup_k4 = {}
print("[+] Building lookup table for D_k4(enc2_block1)...")
for i in tqdm(range(256 * 256)):
    k4_bytes = i.to_bytes(2, 'big')
    cipher = AES.new(generate_aes_key(k4_bytes), AES.MODE_ECB)
    lookup_k4[cipher.decrypt(enc2_block1)] = k4_bytes

print("[+] Searching for a match and verifying on block 2...")
found_k3, found_k4 = None, None
for i in tqdm(range(256 * 256)):
    k3_bytes = i.to_bytes(2, 'big')
    cipher3 = AES.new(generate_aes_key(k3_bytes), AES.MODE_ECB)
    encrypted_with_k3_block1 = cipher3.encrypt(enc_block1)
    if encrypted_with_k3_block1 in lookup_k4:
        candidate_k3 = k3_bytes
        candidate_k4 = lookup_k4[encrypted_with_k3_block1]
        cipher4_verify = AES.new(generate_aes_key(candidate_k4), AES.MODE_ECB)
        if cipher4_verify.decrypt(enc2_block2) == cipher3.encrypt(enc_block2):
            found_k3 = candidate_k3
            found_k4 = candidate_k4
            print(f"\n[+] VERIFIED k3: {found_k3.hex()}")
            print(f"[+] VERIFIED k4: {found_k4.hex()}")
            break

if not found_k3: exit("[-] Could not find k3 and k4.")

# --- PHẦN 3: Khôi phục message và tạo flag ---
cipher1 = AES.new(generate_aes_key(found_k1), AES.MODE_ECB)
cipher2 = AES.new(generate_aes_key(found_k2), AES.MODE_ECB)
cipher3 = AES.new(generate_aes_key(found_k3), AES.MODE_ECB)
cipher4 = AES.new(generate_aes_key(found_k4), AES.MODE_ECB)

# Giải mã enc
message = cipher1.decrypt(cipher2.decrypt(enc))
print("\n[*] Decrypted message from enc:")
print(f"[+] Hex: {message.hex()}")
print(f"[+] ASCII: {message.decode('ascii', errors='replace')}")

# Lấy các bytes của các khóa
k1_bytes = found_k1
k2_bytes = found_k2
k3_bytes = found_k3
k4_bytes = found_k4

# Tạo flag hoàn chỉnh theo đúng format
# Dựa trên gợi ý: flag = secret_message + k1 + k2 + k3 + k4
# Kiểm tra xem message đã chứa dấu ngoặc nhọn } chưa
partial_flag = message.decode('ascii', errors='replace')
if partial_flag.endswith('7'):
    # Nếu message kết thúc bằng số 7, ta thêm các khóa vào
    # Chuyển các khóa sang ASCII
    k1_ascii = ''.join(chr(c) for c in k1_bytes)
    k2_ascii = ''.join(chr(c) for c in k2_bytes)
    k3_ascii = ''.join(chr(c) for c in k3_bytes)
    k4_ascii = ''.join(chr(c) for c in k4_bytes)
    
    complete_flag = f"{partial_flag}{k1_ascii}{k2_ascii}{k3_ascii}{k4_ascii}"
    print(f"\n[+] Flag (Option 1): {complete_flag}")
    
    # Thêm dấu } nếu chưa có
    if not complete_flag.endswith('}'):
        complete_flag += '}'
        print(f"[+] Flag (Option 2): {complete_flag}")
    
    # Nếu các khóa không phải là các ký tự có thể in được, thử dùng giá trị hex
    complete_flag_hex = f"{partial_flag}{found_k1.hex()}{found_k2.hex()}{found_k3.hex()}{found_k4.hex()}"
    print(f"[+] Flag (Option 3): {complete_flag_hex}")
    if not complete_flag_hex.endswith('}'):
        complete_flag_hex += '}'
        print(f"[+] Flag (Option 4): {complete_flag_hex}")
else:
    # Nếu message đã kết thúc bằng một ký tự khác, kiểm tra cẩn thận
    print(f"\n[+] WARNING: Message does not end with '7' as expected")
    print(f"[+] Last 5 bytes of message: {message[-5:].hex()}")
    
    # Kiểm tra xem có phần nào của message cần bỏ đi không
    # Nếu các ký tự cuối không phải printable ASCII
    if any(b < 32 or b > 126 for b in message[-5:]):
        print(f"[+] Last bytes may contain padding or non-printable chars")
        for i in range(1, 6):
            print(f"[+] Truncated {i} bytes: {message[:-i].decode('ascii', errors='replace')}")

# Xác nhận rằng đây là cách giải đúng nhất
print("\n[*] Checking consistency with known format")
known_flag_format = "scriptCTF{s3cr37_m3ss4g3_1337!_"
if known_flag_format in partial_flag:
    print(f"[+] Confirmed message contains expected format")
    # Lấy phần sau format đã biết
    suffix = partial_flag[len(known_flag_format):]
    print(f"[+] Suffix after known format: '{suffix}'")
    
    # Phần cuối cùng nên là: 7e4b3f8d}
    # e4 = k1 (6534), b3 = k2 (6233), f8 = k3 (6638), d} = k4 (647d)
    k1_char = ''.join(chr(c) for c in k1_bytes if 32 <= c <= 126)
    k2_char = ''.join(chr(c) for c in k2_bytes if 32 <= c <= 126)
    k3_char = ''.join(chr(c) for c in k3_bytes if 32 <= c <= 126)
    k4_char = ''.join(chr(c) for c in k4_bytes if 32 <= c <= 126)
    
    final_flag = f"{known_flag_format}{suffix}{k1_char}{k2_char}{k3_char}{k4_char}"
    if not final_flag.endswith('}'):
        final_flag += '}'
    
    print(f"\n[!] FINAL FLAG: {final_flag}")