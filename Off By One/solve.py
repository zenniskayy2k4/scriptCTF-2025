from PIL import Image, ImageChops

# --- Cấu hình ---
CHALLENGE_FILE = 'hidden.png'
FLAG_IMAGE = 'SCAN_THIS_QR_CODE.png'

try:
    print(f"[*] Đang mở file '{CHALLENGE_FILE}'...")
    img = Image.open(CHALLENGE_FILE)
    img_bw = img.convert('1')
    
    print("[*] Tạo một bản sao và dịch chuyển xuống 1 pixel...")
    img_shifted = ImageChops.offset(img_bw, 0, 1)

    print("[*] Thực hiện XOR vi sai...")
    xor_result = ImageChops.logical_xor(img_bw, img_shifted)

    # ----- BƯỚC QUAN TRỌNG NHẤT -----
    print("[*] Đảo ngược màu sắc của kết quả để có thể quét được...")
    final_qr = ImageChops.invert(xor_result)

    # Lưu lại ảnh kết quả cuối cùng
    final_qr.save(FLAG_IMAGE)
    
    print("\n" + "="*50)
    print("#####         CHÚC MỪNG! BẠN ĐÃ GIẢI ĐƯỢC!         #####")
    print(f"#####    MỞ FILE '{FLAG_IMAGE}' VÀ QUÉT MÃ QR!    #####")
    print("="*50)

except FileNotFoundError:
    print(f"[!] Lỗi: Không tìm thấy file '{CHALLENGE_FILE}'.")
except Exception as e:
    print(f"[!] Đã xảy ra lỗi: {e}")