import socket
from collections import defaultdict
import sys

HOST = "play.scriptsorcerers.xyz"
PORT = 10376

N = 1000000
WINDOW_SIZE = N // 2
MAX_VAL = 100001

def log(message):
    print(message, file=sys.stderr)

# ----------------- HÀM TIỀN XỬ LÝ (CHO VÒNG 8) -----------------
phi = list(range(MAX_VAL))
divs = [[] for _ in range(MAX_VAL)]
precomputed = False

def precompute_for_gcd():
    global precomputed
    if precomputed: return
    log("[*] Tiền xử lý cho Vòng 8 (Sieve)...")
    for i in range(2, MAX_VAL):
        if phi[i] == i:
            for j in range(i, MAX_VAL, i): phi[j] -= phi[j] // i
    for i in range(1, MAX_VAL):
        # Bỏ qua i = 0 để tránh vòng lặp vô tận/lỗi
        if i == 0: continue
        for j in range(i, MAX_VAL, i): divs[j].append(i)
    precomputed = True
    log("[+] Tiền xử lý hoàn tất.")

# ----------------- LỚP FENWICK TREE (CHO VÒNG 4) -----------------
class FenwickTree:
    def __init__(self, size): self.tree, self.size = [0] * (size + 1), size
    def update(self, i, delta):
        i += 1
        while i <= self.size: self.tree[i] += delta; i += i & (-i)
    def query(self, i):
        i += 1; s = 0
        while i > 0: s += self.tree[i]; i -= i & (-i)
        return s
    def find_kth(self, k):
        low, high, ans = 0, self.size - 1, -1
        while low <= high:
            mid = (low + high) // 2
            if self.query(mid) >= k: ans = mid; high = mid - 1
            else: low = mid + 1
        return ans

# ----------------- HÀM TÍNH TOÁN CHO TỪNG VÒNG (1-7 không đổi) -----------------
def solve_round_1_sums(nums, window_size):
    current_sum = sum(nums[0:window_size]); results = [current_sum]
    for i in range(N - window_size): current_sum = current_sum - nums[i] + nums[i + window_size]; results.append(current_sum)
    return results

def solve_round_2_xors(nums, window_size):
    current_xor = 0;
    for i in range(window_size): current_xor ^= nums[i]
    results = [current_xor]
    for i in range(N - window_size): current_xor = current_xor ^ nums[i] ^ nums[i + window_size]; results.append(current_xor)
    return results

def solve_round_3_means(nums, window_size):
    current_sum = sum(nums[0:window_size]); results = [current_sum // window_size]
    for i in range(N - window_size): current_sum = current_sum - nums[i] + nums[i + window_size]; results.append(current_sum // window_size)
    return results

def solve_round_4_median(nums, window_size):
    kth_element_idx = (window_size // 2) - 1; bit = FenwickTree(MAX_VAL)
    for i in range(window_size): bit.update(nums[i], 1)
    results = [bit.find_kth(kth_element_idx + 1)]
    for i in range(N - window_size):
        bit.update(nums[i], -1); bit.update(nums[i + window_size], 1)
        results.append(bit.find_kth(kth_element_idx + 1))
    return results

def solve_round_5_modes(nums, window_size):
    freq, counts, max_freq = defaultdict(int), defaultdict(set), 0
    for i in range(window_size):
        val = nums[i]
        if freq[val] > 0: counts[freq[val]].discard(val)
        freq[val] += 1; counts[freq[val]].add(val)
        if freq[val] > max_freq: max_freq = freq[val]
    results = [max(counts[max_freq])]
    for i in range(N - window_size):
        old_val, new_val = nums[i], nums[i + window_size]
        counts[freq[old_val]].discard(old_val)
        if not counts[freq[old_val]] and freq[old_val] == max_freq: max_freq -= 1
        freq[old_val] -= 1
        if freq[old_val] > 0: counts[freq[old_val]].add(old_val)
        if freq[new_val] > 0: counts[freq[new_val]].discard(new_val)
        freq[new_val] += 1; counts[freq[new_val]].add(new_val)
        if freq[new_val] > max_freq: max_freq = freq[new_val]
        results.append(max(counts[max_freq]))
    return results

def solve_round_6_mex(nums, window_size):
    freq, current_mex = defaultdict(int), 0
    for i in range(window_size): freq[nums[i]] += 1
    while freq[current_mex] > 0: current_mex += 1
    results = [current_mex]
    for i in range(N - window_size):
        old_val, new_val = nums[i], nums[i + window_size]
        freq[old_val] -= 1
        if freq[old_val] == 0 and old_val < current_mex: current_mex = old_val
        freq[new_val] += 1
        while freq[current_mex] > 0: current_mex += 1
        results.append(current_mex)
    return results

def solve_round_7_distinct(nums, window_size):
    freq = defaultdict(int)
    for i in range(window_size): freq[nums[i]] += 1
    distinct_count = len(freq); results = [distinct_count]
    for i in range(N - window_size):
        old_val, new_val = nums[i], nums[i + window_size]
        freq[old_val] -= 1
        if freq[old_val] == 0: distinct_count -= 1
        if freq[new_val] == 0: distinct_count += 1
        freq[new_val] += 1; results.append(distinct_count)
    return results

# ----------------- HÀM GIẢI VÒNG 8 - ĐÃ SỬA LỖI SỐ 0 -----------------
def solve_round_8_gcd_efficient(nums, window_size):
    precompute_for_gcd()
    
    multiples_count = [0] * MAX_VAL
    gcd_sum_non_zeros, sum_non_zeros, zero_count = 0, 0, 0
    results = []

    def add_nonzero(val):
        nonlocal gcd_sum_non_zeros, sum_non_zeros
        for d in divs[val]: gcd_sum_non_zeros += phi[d] * multiples_count[d]
        for d in divs[val]: multiples_count[d] += 1
        sum_non_zeros += val

    def remove_nonzero(val):
        nonlocal gcd_sum_non_zeros, sum_non_zeros
        for d in divs[val]: multiples_count[d] -= 1
        for d in divs[val]: gcd_sum_non_zeros -= phi[d] * multiples_count[d]
        sum_non_zeros -= val
    
    # Khởi tạo cửa sổ đầu tiên
    for i in range(window_size):
        val = nums[i]
        if val == 0: zero_count += 1
        else: add_nonzero(val)
    
    results.append(gcd_sum_non_zeros + sum_non_zeros * zero_count)
    
    # Trượt cửa sổ
    for i in range(N - window_size):
        old_val, new_val = nums[i], nums[i + window_size]
        
        # Xóa old_val
        if old_val == 0: zero_count -= 1
        else: remove_nonzero(old_val)
        
        # Thêm new_val
        if new_val == 0: zero_count += 1
        else: add_nonzero(new_val)
        
        results.append(gcd_sum_non_zeros + sum_non_zeros * zero_count)
        
    return results

# ----------------- HÀM TƯƠNG TÁC VỚI SERVER -----------------
class Remote:
    def __init__(self, host, port):
        self.sock, self.buffer = socket.socket(socket.AF_INET, socket.SOCK_STREAM), b''
        self.sock.connect((host, port))
    def recv_until(self, delim=b'\n'):
        while delim not in self.buffer:
            chunk = self.sock.recv(4096)
            if not chunk: return None
            self.buffer += chunk
        line, self.buffer = self.buffer.split(delim, 1); return line.decode()
    def send_line(self, data): self.sock.sendall(data.encode() + b'\n')
    def close(self): self.sock.close()

def main():
    conn = Remote(HOST, PORT)
    try:
        num_line = ""; 
        while not num_line or "Round" in num_line: num_line = conn.recv_until()
        log("[*] Đang nhận dãy số..."); nums = list(map(int, num_line.split()))
        log(f"[+] Đã nhận {len(nums)} số.")
        solvers = [
            solve_round_1_sums, solve_round_2_xors, solve_round_3_means,
            solve_round_4_median, solve_round_5_modes, solve_round_6_mex,
            solve_round_7_distinct, solve_round_8_gcd_efficient
        ]
        for i, solver in enumerate(solvers):
            round_prompt = conn.recv_until()
            if not round_prompt or "uh oh" in round_prompt.lower():
                log(f"[!] Lỗi từ Server sau Vòng {i}: {round_prompt.strip() if round_prompt else 'Kết nối đã đóng'}")
                break
            log(f"[<] Server: {round_prompt.strip()}"); 
            log(f"[*] Đang tính toán cho Vòng {i+1}...")
            results = solver(nums, WINDOW_SIZE); answer = ' '.join(map(str, results))
            log(f"[+] Đã tính xong. Gửi kết quả...")
            conn.send_line(answer)
        flag = conn.recv_until()
        if flag:
            print("\n======================================")
            print(f"[+] FLAG: {flag.strip()}")
            print("======================================\n")
    except Exception as e: log(f"[!] Lỗi: {e}")
    finally: conn.close(); log("[*] Đã đóng kết nối.")

if __name__ == "__main__":
    main()