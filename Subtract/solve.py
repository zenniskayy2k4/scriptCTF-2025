from PIL import Image

# Đọc tọa độ từ file
coordinates = []
with open('coordinates.txt', 'r') as file:
    for line in file:
        line = line.strip()
        if line:
            x_str, y_str = line[1:-1].split(',')  # Bỏ dấu ngoặc và tách
            x, y = int(x_str.strip()), int(y_str.strip())
            coordinates.append((x, y))

# Đếm số lần xuất hiện của mỗi tọa độ
from collections import defaultdict
count_dict = defaultdict(int)
for coord in coordinates:
    count_dict[coord] += 1

# Chỉ giữ các tọa độ xuất hiện đúng 1 lần
unique_coords = [coord for coord, count in count_dict.items() if count == 1]

# Tạo ảnh 500x500 (nền trắng)
img = Image.new('1', (500, 500), 1)  # Chế độ '1': ảnh nhị phân (0: đen, 1: trắng)
pixels = img.load()

# Đặt các điểm duy nhất lên ảnh (màu đen)
for (x, y) in unique_coords:
    if 0 <= x < 500 and 0 <= y < 500:
        pixels[x, y] = 0  # Màu đen

# Lưu ảnh
img.save('flag.png')
print("Ảnh đã được lưu: flag.png. Mở ảnh để xem cờ.")