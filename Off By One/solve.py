from PIL import Image
import math
from pyzbar.pyzbar import decode

hex_data = "000000000000000fe423f8416cd042e9c0ba175ae5d0ba28ae841519043faaafe00010000fbedd507ce16a80a9763e120e6a20ffd7e6842356b025f148610054e20a38ffa800734683fb6ab610425100bad1fb85d4638c2eb1d5210519710feaa058000000000000007fff"
try:
    print("\n--- BƯỚC 1: Xử lý dữ liệu hex ---")
    
    # Chuyển đổi chuỗi hex thành một chuỗi nhị phân (0 và 1)
    data_bytes = bytes.fromhex(hex_data)
    bin_str = ''.join(format(byte, '08b') for byte in data_bytes)
    print(f"[*] Chiều dài chuỗi nhị phân ban đầu: {len(bin_str)} bits.")

    print("\n--- BƯỚC 2: Tìm kích thước hình vuông hoàn hảo ---")
    # Cắt bớt các bit thừa ở cuối cho đến khi chiều dài là một số chính phương
    while True:
        length = len(bin_str)
        if length == 0:
            raise ValueError("Dữ liệu không hợp lệ, không còn bit nào sau khi xử lý.")
            
        size = int(math.isqrt(length)) 
        if size * size == length:
            break 
        bin_str = bin_str[:-1]

    print(f"[+] Dữ liệu cuối cùng có độ dài: {len(bin_str)} bits.")
    print(f"[+] Kích thước mã QR hoàn hảo là: {size}x{size}")

    print("\n--- BƯỚC 3: Dựng lại hình ảnh mã QR ---")
    img = Image.new("1", (size, size))

    for i, bit in enumerate(bin_str):
        x = i % size
        y = i // size
        img.putpixel((x, y), 0 if bit == "1" else 1)
    print("[+] Đã dựng lại ảnh thành công.")

    print("\n--- BƯỚC 4: Phóng to và lưu ảnh ---")
    img_resized = img.resize((size * 10, size * 10), Image.NEAREST)

    output_filename = "flag.png"
    img_resized.save(output_filename)
    print(f"[+] Đã lưu mã QR tại: '{output_filename}'")
    
    # ----- BƯỚC 5: TỰ ĐỘNG ĐỌC MÃ QR VÀ TRÍCH XUẤT FLAG -----
    print("\n--- BƯỚC 5: Tự động giải mã QR để lấy FLAG ---")
    
    # Sử dụng ảnh đã được phóng to để giải mã
    decoded_objects = decode(img_resized)
    
    if decoded_objects:
        # Lấy kết quả đầu tiên và giải mã từ bytes sang string
        flag = decoded_objects[0].data.decode('utf-8')
        
        print("\n" + "="*55)
        print(f"\nFLAG: {flag}")
        print("\n" + "="*55)
    else:
        print("\n[!] Không thể tự động giải mã được mã QR.")
        print(f"    Tuy nhiên, file ảnh đã được lưu tại '{output_filename}'.")
        print("    Vui lòng thử quét nó bằng một ứng dụng khác.")


except Exception as e:
    print(f"\n[!] Đã xảy ra lỗi: {e}")
    print("    Vui lòng kiểm tra lại chuỗi hex_data hoặc đảm bảo đã cài đặt đủ thư viện.")