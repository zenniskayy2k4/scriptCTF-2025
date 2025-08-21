from Crypto.Cipher import AES
from binascii import unhexlify

# Ciphertext được hardcode trong chương trình
ciphertext_hex = "e2ea0d318af80079fb56db5674ca8c274c5fd0e92019acd01e89171bb889f6b1"
ciphertext = unhexlify(ciphertext_hex)

print("Starting brute-force attack with all key sizes...")

found = False
# Brute force 256 giá trị cho byte đầu tiên
for b1 in range(256):
    if b1 % 16 == 0:
        print(f"[*] Trying b1 = 0x{b1:02x}...")
        
    # Brute force 256 giá trị cho byte thứ hai
    for b2 in range(256):
        try:
            # Xây dựng IV. Giả định IV luôn có 2 byte đầu thay đổi
            iv = bytes([b1, b2]) + b'\x00' * 14
            
            key_candidates = [
                bytes([b1, b2]) + b'\x00' * 14, # AES-128 (16 bytes)
                bytes([b1, b2]) + b'\x00' * 22, # AES-192 (24 bytes)
                bytes([b1, b2]) + b'\x00' * 30  # AES-256 (32 bytes)
            ]

            for key in key_candidates:
                cipher = AES.new(key, AES.MODE_CBC, iv)
                decrypted_data = cipher.decrypt(ciphertext)
                
                padding_len = decrypted_data[-1]
                if 0 < padding_len <= 16:
                    if decrypted_data.endswith(bytes([padding_len]) * padding_len):
                        plaintext = decrypted_data[:-padding_len]
                        # Thường flag sẽ là dạng printable ASCII
                        if all(32 <= c < 127 for c in plaintext):
                            print(f"    Key Size: {len(key)} bytes")
                            print(f"    Key Bytes: 0x{b1:02x}, 0x{b2:02x}")
                            print(f"    FLAG: {plaintext.decode('ascii')}")
                            found = True
                            break
            if found:
                break
        except Exception:
            continue
    if found:
        break

if not found:
    print("\n[-] Brute-force failed. The logic is something else.")