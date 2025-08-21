### Write-up: Giải mã thử thách "Off By One"

#### Giới thiệu

*   **Tên thử thách:** Off By One
*   **Loại:** Forensics, Steganography (Giấu tin)
*   **File được cung cấp:** `hidden.png`
*   **Mô tả:** "i hid a qr inside a qr" (Tôi giấu một mã QR bên trong một mã QR)

Mục tiêu của chúng ta là tìm ra mã QR bí mật được giấu bên trong file `hidden.png`.

---

### Bước 1: Phân tích ban đầu và Thu thập Manh mối

Bước đầu tiên trong bất kỳ thử thách forensics nào là thu thập càng nhiều thông tin cơ bản càng tốt.

1.  **Quét mã QR ban đầu:** Sử dụng một trình quét mã QR bất kỳ, chúng ta quét `hidden.png`.
    *   **Kết quả:** Quét thành công và nhận được một link URL dẫn đến video "Never Gonna Give You Up" của Rick Astley. Đây là một "Rickroll" kinh điển.
    *   **Suy luận ban đầu:** Đây là một thông tin phụ, xác nhận `hidden.png` là một mã QR hợp lệ.

2.  **Kiểm tra metadata và cấu trúc file:**
    *   Sử dụng `exiftool hidden.png`: Không tìm thấy thông tin metadata nào đáng kể.
    *   Sử dụng `file hidden.png` hoặc xem thuộc tính:
        *   **Kích thước:** `963 x 964` pixel. Đây là một manh mối **cực kỳ quan trọng** và khớp với tên bài **"Off By One"**. Hình ảnh không phải là hình vuông.
        *   **Loại màu:** RGB. Mặc dù trông như ảnh đen trắng, nó lại được lưu ở định dạng có 3 kênh màu.

---

### Bước 2: Hành trình đi vào "Hang Thỏ" - Loại bỏ các hướng đi sai lầm

Dựa trên các manh mối ban đầu, chúng ta đã thử nghiệm hàng loạt các giả thuyết. Mặc dù thất bại, quá trình loại trừ này rất quan trọng để chúng ta có thể tập trung vào con đường đúng.

*   **Giả thuyết 1: Phân tích giá trị pixel:** Chúng ta tìm kiếm các pixel có giá trị màu lệch đi 1 đơn vị (ví dụ: `(1,1,1)` hoặc `(254,254,254)`) nhưng không tìm thấy gì đáng kể.
*   **Giả thuyết 2: XOR vi sai:** Dựa trên kích thước `963x964`, chúng ta thử so sánh ảnh với chính nó sau khi dịch chuyển 1 pixel. Kết quả chỉ là các "bộ xương" không thể quét được.
*   **Giả thuyết 3: Dữ liệu ẩn trong file:** Sử dụng `binwalk`, chúng ta phát hiện một khối dữ liệu Zlib nhúng bên trong file. Sau khi trích xuất và giải nén, file dữ liệu thô này không thể được diễn giải thành một hình ảnh hay văn bản có nghĩa. Con đường này được xác định là một "cái bẫy" (red herring) để đánh lạc hướng.

---

### Bước 3: Khoảnh khắc "À há!" - Phát hiện dữ liệu trong LSB

Sau khi loại bỏ các hướng đi phức tạp, chúng ta quay trở lại với kỹ thuật steganography cơ bản và sử dụng công cụ phù hợp nhất: **Stegsolve**.

1.  **Sử dụng Stegsolve:** Chúng ta mở `hidden.png` trong Stegsolve.
2.  **Phát hiện quyết định (phát hiện của bạn):**
    *   Chúng ta sử dụng công cụ **Analyse > Bit Plane Slicing**.
    *   Bằng cách cô lập từng lớp bit của từng kênh màu, một phát hiện quan trọng đã xuất hiện: Khi xem **Lớp Bit 0 (LSB - Least Significant Bit)** của riêng **kênh màu Xanh dương (Blue Channel)**, một mã QR hoàn chỉnh và rõ ràng hiện ra.
    *   Gợi ý "Off By One" có thể ám chỉ đến việc dữ liệu được giấu trong lớp bit cuối cùng này (`off by one bit`).

Phát hiện này đã giải mã toàn bộ bài toán. Mã QR bí mật đã được mã hóa vào LSB của kênh màu Blue trong ảnh `hidden.png`.

---

### Bước 4: Lời giải cuối cùng - Trích xuất và Tái tạo từ dữ liệu LSB

Từ phát hiện trên, chúng ta có hai cách để đi đến đích:

#### Cách 1: Sử dụng Stegsolve (Phương pháp trực quan)

Đây là cách nhanh và trực tiếp nhất:
1.  Trong Stegsolve, đi đến **Analyse > Bit Plane Slicing**.
2.  Chỉ chọn kênh **Blue** và **Bit Plane 0**.
3.  Nhấn nút **Save** để lưu lại hình ảnh mã QR hoàn chỉnh.
4.  Quét mã QR trong file vừa lưu để nhận flag.

#### Cách 2: Trích xuất và Tái tạo bằng Script (Phương pháp lập trình)

Cách này mang lại sự hiểu biết sâu sắc hơn về quá trình xử lý dữ liệu:
1.  **Trích xuất dữ liệu LSB:** Sử dụng công cụ (như Stegsolve hoặc một script riêng) để đọc LSB của kênh Blue từ `hidden.png` và xuất nó ra một file văn bản chứa chuỗi hex.
2.  **Viết Script Tái tạo:** Sử dụng kịch bản Python mà chúng ta đã cùng nhau hoàn thiện. Script này:
    *   Đọc và làm sạch chuỗi hex đã trích xuất.
    *   Sử dụng `bytes.fromhex()` để chuyển chuỗi hex thành dữ liệu byte.
    *   Chuyển đổi dữ liệu byte thành một chuỗi nhị phân dài (0 và 1).
    *   Cắt bớt dữ liệu thừa ở cuối để đảm bảo tổng số bit là một số chính phương (`N x N`).
    *   Tạo một ảnh đen trắng mới và dựng lại mã QR bằng cách tô màu từng pixel dựa trên chuỗi nhị phân.
    *   Tự động giải mã QR bằng thư viện `pyzbar` và in flag ra màn hình.

### Công cụ và Kịch bản

*   **Công cụ chính:** **Stegsolve** (Công cụ quyết định giúp chúng ta tìm ra dữ liệu ẩn trong LSB).
*   **Các công cụ phụ trợ:** `exiftool`, `binwalk` (Hữu ích cho việc loại trừ các giả thuyết).
*   **Thư viện Python:** `Pillow` (để xử lý ảnh), `pyzbar` (để đọc QR).
*   **Kịch bản cuối cùng:** Kịch bản Python `build_flag_qr.py`, đọc chuỗi hex của dữ liệu LSB và dựng lại thành ảnh QR có thể quét được.

### Bài học kinh nghiệm

*   **Trực giác và quan sát là chìa khóa:** Phát hiện về "vệt đen" trong LSB của kênh Blue là bước ngoặt quyết định. Trong forensics, tin vào những gì mắt mình thấy trong các công cụ phân tích thường hiệu quả hơn các giả thuyết phức tạp.
*   **LSB Steganography là một kỹ thuật kinh điển:** Giấu dữ liệu vào bit cuối cùng của pixel là một trong những kỹ thuật steganography cơ bản và phổ biến nhất.
*   **Không phải mọi manh mối đều dẫn đến con đường chính:** Manh mối "Rickroll" và dữ liệu Zlib nhúng có thể là những "cái bẫy" (red herrings) được thiết kế để đánh lạc hướng chúng ta khỏi phương pháp LSB đơn giản hơn.
*   **Kiên trì và loại trừ:** Con đường giải một bài CTF không bao giờ thẳng. Quá trình thử nghiệm và loại bỏ các giả thuyết sai lầm là một phần không thể thiếu.