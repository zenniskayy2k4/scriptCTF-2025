import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from binascii import unhexlify

# 1. Byte đầu vào chính xác mà chúng ta đã tìm thấy
input_byte = 0x60
byte_to_hash = bytes([input_byte])

# 2. Tính toán hash Blake2b 64-byte
hasher = hashlib.blake2b(digest_size=64)
hasher.update(byte_to_hash)
full_hash = hasher.digest()

# 3. Trích xuất Key và IV từ CÙNG MỘT HASH (logic tràn bộ đệm)
# Key là 32 byte đầu tiên
key = full_hash[0:32]

# IV là 16 byte tiếp theo
iv = full_hash[32:48]

# 4. Chuẩn bị ciphertext
ciphertext_hex = "713d7f2c0f502f485a8af0c284bd3f1e7b03d27204a616a8340beaae23f130edf65401c1f99fe99f63486a385ccea217"
ciphertext = unhexlify(ciphertext_hex)

# In ra để xác nhận
print(f"[*] Using input byte: {hex(input_byte)}")
print(f"[*] Full 64-byte hash: {full_hash.hex()}")
print(f"[*] Derived AES Key (bytes 0-31):  {key.hex()}")
print(f"[*] Derived AES IV (bytes 32-47):   {iv.hex()}")

# 5. Giải mã
try:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(ciphertext)
    
    # Bỏ padding
    flag_bytes = unpad(decrypted_padded, AES.block_size)
    flag = flag_bytes.decode('utf-8')
    
    print("\n[+] Success! The correct flag is:")
    print(flag)
    
except Exception as e:
    print(f"\n[-] An error occurred: {e}")