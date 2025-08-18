import socket
import sys

HOST = 'play.scriptsorcerers.xyz'
PORT = 10089
N = 100

def count_factors(n, factor):
    if n == 0: return 1
    count = 0
    while n > 0 and n % factor == 0:
        count += 1
        n //= factor
    return count

def solve():
    print(f"[*] Đang kết nối tới {HOST}:{PORT}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print("[+] Kết nối thành công!")
            
            buffer = b''
            s.settimeout(5.0)
            while True:
                try:
                    data = s.recv(8192)
                    if not data: break
                    buffer += data
                    if buffer.strip().count(b'\n') >= N - 1: break
                except socket.timeout:
                    break
            s.settimeout(None)

            all_lines = [line for line in buffer.decode('utf-8').strip().split('\n') if line]
            grid = [list(map(int, line.strip().split())) for line in all_lines]

            if len(grid) != N or any(len(row) != N for row in grid):
                print(f"[!] Lỗi: Nhận được ma trận không hợp lệ.")
                return
            print(f"[+] Đã nhận ma trận {N}x{N}.")

            factors_grid = [[(count_factors(grid[i][j], 2), count_factors(grid[i][j], 5)) for j in range(N)] for i in range(N)]

            print("[*] Bắt đầu quy hoạch động (Knapsack-style)...")
            
            # Ước tính số thừa số 5 tối đa có thể có
            MAX_FIVES = (N + N - 1) * 5 
            
            # dp[i][j][k]: số thừa số 2 lớn nhất tại (i,j) với k thừa số 5
            dp = [[[-1] * (MAX_FIVES + 1) for _ in range(N)] for _ in range(N)]
            ans_grid = [[0] * N for _ in range(N)]

            # Xử lý ô bắt đầu (0,0)
            c2, c5 = factors_grid[0][0]
            dp[0][0][c5] = c2
            ans_grid[0][0] = min(c2, c5)

            # Điền toàn bộ bảng DP
            for i in range(N):
                for j in range(N):
                    if i == 0 and j == 0:
                        continue
                    
                    c2, c5 = factors_grid[i][j]
                    
                    # Lấy kết quả từ ô trên và ô trái
                    for k in range(MAX_FIVES + 1):
                        from_up = -1
                        if i > 0 and k >= c5 and dp[i-1][j][k-c5] != -1:
                            from_up = dp[i-1][j][k-c5] + c2
                        
                        from_left = -1
                        if j > 0 and k >= c5 and dp[i][j-1][k-c5] != -1:
                            from_left = dp[i][j-1][k-c5] + c2
                        
                        dp[i][j][k] = max(from_up, from_left)

                    # Tính câu trả lời cho ô (i,j)
                    max_zeros_for_cell = 0
                    for k in range(MAX_FIVES + 1):
                        if dp[i][j][k] != -1:
                            max_zeros_for_cell = max(max_zeros_for_cell, min(k, dp[i][j][k]))
                    ans_grid[i][j] = max_zeros_for_cell

            print("[+] Tính toán hoàn tất.")

            output_str = "\n".join([" ".join(map(str, row)) for row in ans_grid]) + "\n"
            
            print("[*] Đang gửi kết quả...")
            s.sendall(output_str.encode('utf-8'))
            print("[+] Gửi thành công!")
            
            print("[*] Đang chờ phản hồi từ server...")
            s.settimeout(10.0)
            response = s.recv(4096).decode('utf-8').strip()
            print("\n========================================")
            print(f"Flag: {response}")
            print("========================================\n")

    except Exception as e:
        print(f"[!] Đã xảy ra lỗi: {e}")

if __name__ == "__main__":
    solve()