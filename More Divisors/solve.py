import socket
from collections import defaultdict
import time

HOST = 'play.scriptsorcerers.xyz'
PORT = 10419

# (Dán hàm calculate_longest_subsequence đã định nghĩa ở trên vào đây)
def calculate_longest_subsequence(numbers: list[int]) -> int:
    if not numbers:
        return 0
    try:
        max_val = max(numbers)
    except ValueError:
        return 0
    spf = list(range(max_val + 1))
    i = 2
    while i * i <= max_val:
        if spf[i] == i:
            for j in range(i * i, max_val + 1, i):
                if spf[j] == j:
                    spf[j] = i
        i += 1
    prime_counts = defaultdict(int)
    for num in numbers:
        if num <= 1:
            continue
        temp_num = num
        unique_factors = set()
        while temp_num > 1:
            factor = spf[temp_num]
            unique_factors.add(factor)
            while temp_num % factor == 0:
                temp_num //= factor
        for factor in unique_factors:
            prime_counts[factor] += 1
    if not prime_counts:
        return 1 if numbers else 0
    return max(prime_counts.values())


def solve_ctf():
    """
    Hàm chính để kết nối, nhận dữ liệu, tính toán, và gửi kết quả.
    """
    print(f"[*] Đang kết nối tới {HOST}:{PORT}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print("[+] Kết nối thành công!")
            
            # Nhận toàn bộ dữ liệu từ server
            print("[*] Đang nhận dữ liệu...")
            buffer = b''
            # Đặt timeout để tránh bị treo nếu server không đóng kết nối
            s.settimeout(5.0) 
            while True:
                try:
                    data = s.recv(4096)
                    if not data:
                        break # Server đã đóng kết nối
                    buffer += data
                except socket.timeout:
                    # Hết thời gian chờ, giả định đã nhận hết dữ liệu
                    print("[*] Hết thời gian chờ, tiến hành xử lý dữ liệu đã nhận.")
                    break
            
            s.settimeout(None) # Tắt timeout

            # Xử lý dữ liệu: chuyển từ byte -> string -> list các số nguyên
            # .split() sẽ tự động xử lý cả dấu cách và dấu xuống dòng
            all_numbers = [int(n) for n in buffer.decode('utf-8').strip().split()]

            if not all_numbers:
                print("[!] Không nhận được số nào từ server.")
                return

            print(f"[+] Đã nhận được {len(all_numbers)} số.")
            
            # Bắt đầu tính toán
            print("[*] Bắt đầu tính toán...")
            start_time = time.time()
            result = calculate_longest_subsequence(all_numbers)
            end_time = time.time()
            print(f"[*] Thời gian tính toán: {end_time - start_time:.4f} giây")
            
            # Gửi kết quả lên server
            print(f"[*] Đang gửi kết quả: {result}")
            # Thêm ký tự xuống dòng '\n', nhiều server CTF yêu cầu điều này
            payload = f"{result}\n".encode('utf-8')
            s.sendall(payload)
            print("[+] Gửi kết quả thành công!")

            # Lắng nghe phản hồi từ server (nếu có, ví dụ: flag)
            try:
                s.settimeout(5.0)
                response = s.recv(4096)
                print(f"[+] Phản hồi từ server: {response.decode('utf-8').strip()}")
            except socket.timeout:
                print("[*] Không nhận được phản hồi thêm từ server.")

    except socket.error as e:
        print(f"[!] Lỗi kết nối: {e}")
    except ValueError:
        print("[!] Dữ liệu nhận được có định dạng không hợp lệ.")
    except Exception as e:
        print(f"[!] Đã xảy ra lỗi không xác định: {e}")

# Chạy hàm giải
if __name__ == "__main__":
    solve_ctf()