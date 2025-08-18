"""
Giải mã flag bằng cách lấy chênh lệch giữa mã Unicode của emoji
và địa chỉ gốc của khối ký tự liên quan (0x1F000).
"""

domino_string = "🁳🁣🁲🁩🁰🁴🁃🁔🁆🁻🀳🁭🀰🁪🀱🁟🀳🁮🁣🀰🁤🀱🁮🁧🁟🀱🁳🁟🁷🀳🀱🁲🁤🁟🀴🁮🁤🁟🁦🁵🁮🀡🀱🁥🀴🀶🁤🁽"

# Địa chỉ base được suy ra bằng cách làm ngược từ ký tự đầu tiên của flag
# ord('🁳') - ord('s') = 0x1F073 - 0x73 = 0x1F000
UNICODE_BASE = 0x1F000

flag = ""
try:
    for char in domino_string:
        # Lấy mã codepoint của ký tự
        codepoint = ord(char)
        
        # Tính toán giá trị ASCII bằng cách lấy offset từ địa chỉ gốc
        ascii_value = codepoint - UNICODE_BASE
        
        # Chuyển mã ASCII thành ký tự và ghép vào flag
        flag += chr(ascii_value)

    print(flag)
    
except ValueError as e:
    print(f"Đã xảy ra lỗi. Có thể do dữ liệu đầu vào bị hỏng. Lỗi: {e}")