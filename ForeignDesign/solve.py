# Độ dài flag và dữ liệu mã hóa giữ nguyên vì chúng giống nhau ở cả 2 file
FLAG_LENGTH = 37

data_ll = [
    0x20, 0x5c, 0x04, 0x68, 0x6a, 0x4c, 0x60, 0x71, 0x2a, 0x41, 0x16, 0x2b, 
    0xcb, 0x54, 0xdc, 0x62, 0xd2, 0x47, 0x1d, 0x7b, 0x14, 0x7d, 0xc7
]
data_lll = [
    0x4c, 0xe6, 0x75, 0xf3, 0x54, 0x36, 0x67, 0xc5, 0x68, 0xfb, 0x53, 0xfd, 
    0x80, 0x9f
]
ENCRYPTED_DATA = data_ll + data_lll

def reverse_s2_java_odd(result, i):
    """Hàm đảo ngược của s2() trong Java (dùng cho i lẻ)"""
    temp = result - (i & 0x1)
    base = temp ^ 0x13
    char_code = base - ((i % 7) * 2)
    return chr(char_code)

def reverse_fun_native_even(result, i):
    """Hàm đảo ngược của hàm native (dùng cho i chẵn)"""
    # result = i * 3 + ((i + 0x13) ^ c_code) ^ 0x5a
    temp1 = result ^ 0x5a
    # Sử dụng & 0xFFFFFFFF để xử lý số nguyên 32-bit không dấu như trong C
    temp2 = (temp1 - (i * 3)) & 0xFFFFFFFF
    char_code = temp2 ^ (i + 0x13)
    return chr(char_code)

# Mảng để chứa các ký tự của flag sau khi giải mã nhưng chưa sắp xếp lại
shuffled_flag_chars = [''] * FLAG_LENGTH

# Bước 1: Giải mã từng ký tự với logic đúng
for i in range(FLAG_LENGTH):
    encrypted_val = ENCRYPTED_DATA[i]
    decrypted_char = ''
    
    # Kiểm tra i là chẵn hay lẻ
    if i % 2 == 0:
        # i là số chẵn, dùng hàm đảo ngược của native
        decrypted_char = reverse_fun_native_even(encrypted_val, i)
    else:
        # i là số lẻ, dùng hàm đảo ngược của s2() trong Java
        decrypted_char = reverse_s2_java_odd(encrypted_val, i)
        
    shuffled_flag_chars[i] = decrypted_char

# Mảng để chứa các ký tự của flag gốc
original_flag_chars = [''] * FLAG_LENGTH

# Bước 2: Đảo ngược việc xáo trộn để có flag gốc
for i in range(FLAG_LENGTH):
    idx = (i * 5 + 3) % FLAG_LENGTH
    original_flag_chars[idx] = shuffled_flag_chars[i]

# Ghép các ký tự lại thành flag hoàn chỉnh
flag = "".join(original_flag_chars)
print(f"The flag is: {flag}")