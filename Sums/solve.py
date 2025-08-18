import socket
import sys

HOST = "play.scriptsorcerers.xyz"  # Thay bằng địa chỉ IP hoặc domain của server
PORT = 10499       # Thay bằng cổng của server
# -----------------------------------------

def solve():
    # Tạo một đối tượng socket và kết nối tới server
    # AF_INET là cho IPv4, SOCK_STREAM là cho kết nối TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"[*] Connecting to {HOST}:{PORT}...", file=sys.stderr)
        s.connect((HOST, PORT))
        print("[*] Connected!", file=sys.stderr)

        # Tạo một file-like object từ socket để có thể dùng readline() tiện lợi
        # 'rb' và 'wb' là đọc/ghi ở dạng bytes
        f = s.makefile('rw', buffering=1) # line-buffered

        # 1. Đọc dòng đầu tiên chứa mảng các số
        line = f.readline()
        nums = list(map(int, line.strip().split()))
        n = len(nums)
        print(f"[*] Received array of {n} numbers.", file=sys.stderr)

        # 2. Xây dựng mảng tiền tố
        prefix_sums = [0] * (n + 1)
        for i in range(n):
            prefix_sums[i+1] = prefix_sums[i] + nums[i]
        print("[*] Prefix sum array built.", file=sys.stderr)

        # 3. Xử lý n truy vấn
        for i in range(n):
            query_line = f.readline()
            if not query_line:
                break
            l, r = map(int, query_line.strip().split())

            # Tính toán kết quả
            result = prefix_sums[r + 1] - prefix_sums[l]

            # Gửi câu trả lời cho server
            # Thêm '\n' vì readline() cần ký tự xuống dòng
            # flush=True là cực kỳ quan trọng để dữ liệu được gửi đi ngay lập tức
            f.write(f"{result}\n")
            f.flush()
            
            # In tiến độ ra stderr để không ảnh hưởng đến giao tiếp với server
            if (i + 1) % 10000 == 0:
                print(f"[*] Answered {i+1}/{n} queries.", file=sys.stderr)

        print("[*] All answers sent. Waiting for the flag...", file=sys.stderr)
        
        # 4. Đọc tất cả output còn lại từ server để lấy flag
        # Dùng một vòng lặp để đọc cho đến khi server đóng kết nối
        final_output = ""
        while True:
            data = f.readline()
            if not data:
                break
            final_output += data

        print("\n[+] Received final output from server:")
        print(final_output)

# Chạy hàm giải
if __name__ == "__main__":
    solve()