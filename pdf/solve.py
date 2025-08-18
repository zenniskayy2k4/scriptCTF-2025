import zlib
import re

# Đọc toàn bộ file PDF ở chế độ nhị phân (binary mode)
with open('challenge.pdf', 'rb') as f:
    content = f.read()

# Tìm stream của object 4 bằng regular expression
# Tìm khối từ "4 0 obj" cho đến "endobj"
object_4_match = re.search(rb"4 0 obj.*?endobj", content, re.DOTALL)

if object_4_match:
    object_4_data = object_4_match.group(0)
    
    # Bên trong object 4, tìm dữ liệu giữa "stream" và "endstream"
    # \r\n hoặc \n là các ký tự xuống dòng có thể xuất hiện sau "stream"
    stream_match = re.search(rb"stream(?:\r\n|\n)(.*)(?:\r\n|\n)endstream", object_4_data, re.DOTALL)
    
    if stream_match:
        compressed_stream = stream_match.group(1)
        
        try:
            # Giải nén dữ liệu bằng zlib
            decompressed_data = zlib.decompress(compressed_stream)
            print("Decompressed Stream Content:")
            # In ra dưới dạng string, bỏ qua các lỗi encoding nếu có
            print(decompressed_data.decode('utf-8', errors='ignore'))
        except zlib.error as e:
            print(f"Lỗi giải nén: {e}")
    else:
        print("Không tìm thấy stream trong object 4.")
else:
    print("Không tìm thấy object 4.")