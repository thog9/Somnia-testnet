# Script Tự Động Somnia Testnet

Kho lưu trữ này chứa một bộ sưu tập các script Python được thiết kế để tự động hóa nhiều tác vụ trên Somnia Testnet, bao gồm nhận token từ faucet, mint token, hoán đổi token, triển khai hợp đồng, gửi giao dịch và giao dịch memecoin. Các script này được tích hợp với file `main.py` trung tâm để thực thi dễ dàng, hỗ trợ nhiều khóa riêng tư và giao diện CLI thân thiện với người dùng.

## Tính Năng Tổng Quan

### Tính Năng Chung

- **Hỗ Trợ Nhiều Tài Khoản**: Đọc khóa riêng tư từ `pvkey.txt` để thực hiện hành động trên nhiều tài khoản.
- **CLI Màu Sắc**: Sử dụng `colorama` để hiển thị đầu ra hấp dẫn với văn bản và viền màu.
- **Thực Thi Bất Đồng Bộ**: Được xây dựng với `asyncio` để tương tác blockchain hiệu quả.
- **Xử Lý Lỗi**: Bắt lỗi toàn diện cho các giao dịch blockchain và vấn đề RPC.
- **Hỗ Trợ Song Ngữ**: Hỗ trợ đầu ra bằng cả tiếng Việt và tiếng Anh dựa trên lựa chọn của người dùng.

### Các Script Bao Gồm

#### 1. `faucetstt.py` - Nhận Token $STT từ Faucet
- **Mô Tả**: Nhận $STT từ faucet của Somnia Testnet thông qua API.
- **Tính Năng**:
  - Đọc địa chỉ từ `addressFaucet.txt`.
  - Hỗ trợ sử dụng proxy từ `proxies.txt` (tùy chọn).
  - Hiển thị IP công khai qua proxy và phản hồi API.
  - Độ trễ ngẫu nhiên (5-15 giây) giữa các yêu cầu.
- **Cách Dùng**: Chọn từ menu `main.py`; yêu cầu `addressFaucet.txt`.

#### 2. `sendtx.py` - Gửi Giao Dịch
- **Mô Tả**: Gửi giao dịch trên Somnia Testnet, đến địa chỉ ngẫu nhiên hoặc từ `address.txt`.
- **Tính Năng**:
  - Số giao dịch và lượng STT do người dùng cấu hình (mặc định: 0.000001 STT).
  - Độ trễ ngẫu nhiên (1-3 giây) giữa các giao dịch.
  - Nhật ký giao dịch chi tiết với liên kết explorer.
- **Cách Dùng**: Chọn từ menu `main.py`, nhập số giao dịch và lượng STT.

#### 3. `deploytoken.py` - Triển Khai Hợp Đồng Token ERC-20
- **Mô Tả**: Triển khai hợp đồng thông minh ERC-20 tùy chỉnh trên Somnia Testnet.
- **Tính Năng**:
  - Người dùng nhập tên token, ký hiệu, số thập phân (mặc định: 18) và tổng cung.
  - Biên dịch và triển khai bằng `solcx` (Solidity 0.8.22).
  - Lưu địa chỉ hợp đồng vào `contractERC20.txt`.
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần triển khai.
- **Cách Dùng**: Chọn từ menu `main.py`, cung cấp chi tiết token.

#### 4. `sendtoken.py` - Gửi Token ERC-20
- **Mô Tả**: Chuyển token ERC-20 đến địa chỉ ngẫu nhiên hoặc từ `addressERC20.txt`.
- **Tính Năng**:
  - Người dùng nhập địa chỉ hợp đồng và số lượng.
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần chuyển.
  - Nhật ký giao dịch chi tiết với liên kết explorer.
- **Cách Dùng**: Chọn từ menu `main.py`, nhập địa chỉ hợp đồng và số lượng.

#### 5. `deploynft.py` - Triển Khai Hợp Đồng NFT
- **Mô Tả**: Triển khai hợp đồng thông minh NFT trên Somnia Testnet.
- **Tính Năng**:
  - Tự động hóa triển khai hợp đồng NFT cho nhiều ví.
  - Hiển thị địa chỉ hợp đồng đã triển khai.
- **Cách Dùng**: Chọn từ menu `main.py`.

#### 6. `mintpong.py` - Mint $PONG
- **Mô Tả**: Mint 1000 token $PONG trên Somnia Testnet.
- **Tính Năng**:
  - Độ trễ ngẫu nhiên (100-300 giây) giữa các lần mint.
  - Kiểm tra số dư STT trước khi mint (tối thiểu 0.001 STT).
  - Nhật ký giao dịch chi tiết với liên kết explorer.
- **Cách Dùng**: Chọn từ menu `main.py`.

#### 7. `mintping.py` - Mint $PING
- **Mô Tả**: Mint token $PING trên Somnia Testnet.
- **Tính Năng**:
  - Chức năng tương tự `mintpong.py` với thông tin cụ thể của $PING.
  - Độ trễ ngẫu nhiên (100-300 giây) giữa các lần mint.
- **Cách Dùng**: Chọn từ menu `main.py`.

#### 8. `swappong.py` - Hoán Đổi $PONG sang $PING
- **Mô Tả**: Hoán đổi $PONG sang $PING trên Somnia Testnet bằng swap router.
- **Tính Năng**:
  - Người dùng nhập số lượng hoán đổi và số lần hoán đổi.
  - Phê duyệt và hoán đổi token với độ trễ ngẫu nhiên (10-30 giây giữa các lần swap, 100-300 giây giữa các ví).
  - Nhật ký giao dịch chi tiết với liên kết explorer.
- **Cách Dùng**: Chọn từ menu `main.py`, nhập số lượng và số lần hoán đổi.

#### 9. `swapping.py` - Hoán Đổi $PING sang $PONG
- **Mô Tả**: Hoán đổi $PING sang $PONG trên Somnia Testnet bằng swap router.
- **Tính Năng**:
  - Tương tự `swappong.py` nhưng theo hướng ngược lại.
  - Số lượng và chu kỳ hoán đổi do người dùng cấu hình.
- **Cách Dùng**: Chọn từ menu `main.py`, nhập số lượng và số lần hoán đổi.

#### 10. `conftnft.py` - Mint NFT Cộng Đồng (CoNFT)
- **Mô Tả**: Mint NFT Community Member of Somnia (CMS - CoNFT) với chi phí 0.1 STT.
- **Tính Năng**:
  - Kiểm tra xem ví đã mint chưa (qua `balanceOf`).
  - Xác minh số dư STT (tối thiểu 0.1 STT).
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần mint.
  - Nhật ký giao dịch chi tiết với liên kết explorer.
- **Cách Dùng**: Chọn từ menu `main.py`.

#### 11. `mintsusdt.py` - Mint 1000 sUSDT
- **Mô Tả**: Mint 1000 token sUSDT trên Somnia Testnet.
- **Tính Năng**:
  - Kiểm tra xem ví đã mint chưa để tránh lặp lại.
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần mint.
  - Nhật ký giao dịch chi tiết với liên kết explorer.
- **Cách Dùng**: Chọn từ menu `main.py`.

#### 12. `buymeme.py` - Mua Memecoin
- **Mô Tả**: Mua memecoin (SOMI, SMSM, SMI) bằng sUSDT trên Somnia Testnet.
- **Tính Năng**:
  - Người dùng chọn token (SOMI, SMSM, hoặc SMI) và số lượng sUSDT.
  - Phê duyệt và hoán đổi với dung sai trượt giá 5%.
  - Hiển thị số dư, giá và vốn hóa thị trường.
  - Độ trễ ngẫu nhiên (10-30 giây) giữa các lần mua.
- **Cách Dùng**: Chọn từ menu `main.py`, chọn token và số lượng.

#### 13. `sellmeme.py` - Bán Memecoin
- **Mô Tả**: Bán memecoin (SOMI, SMSM, SMI) lấy sUSDT trên Somnia Testnet.
- **Tính Năng**:
  - Người dùng chọn token và số lượng để bán.
  - Phê duyệt và thực hiện hoán đổi với độ trễ ngẫu nhiên (10-30 giây).
  - Hiển thị số dư, giá và vốn hóa thị trường.
- **Cách Dùng**: Chọn từ menu `main.py`, chọn token và số lượng.

## Yêu Cầu
- **Python 3.8+**
- **Phụ Thuộc**: Cài đặt qua `pip install -r requirements.txt` (bao gồm `web3.py`, `colorama`, `aiohttp`, `aiohttp_socks`, `solcx`, và `eth-account`).
- **pvkey.txt**: Thêm khóa riêng tư (mỗi khóa một dòng) để tự động hóa ví.
- **address.txt** / **addressERC20.txt** / **addressFaucet.txt** / **proxies.txt**: File tùy chọn để chỉ định địa chỉ hoặc proxy.

## Cài Đặt

1. **Clone this repository:**
- Open cmd or Shell, then run the command:
```sh
git clone https://github.com/thog9/Somnia-testnet.git
```
```sh
cd Somnia-testnet
```
2. **Install Dependencies:**
- Open cmd or Shell, then run the command:
```sh
pip install -r requirements.txt
```
3. **Prepare Input Files:**
- Open the `pvkey.txt`: Add your private keys (one per line) in the root directory.
```sh
nano pvkey.txt 
```
- Open the `address.txt`(optional): Add recipient addresses (one per line) for `sendtx.py`, `faucetstt.py`, `deploytoken.py`, `sendtoken.py`, `proxies.txt`.
```sh
nano address.txt 
```
```sh
nano addressERC20.txt
```
```sh
nano addressFaucet.txt
```
```sh
nano proxies.txt
```
```sh
nano contractERC20.txt
```
4. **Run:**
- Open cmd or Shell, then run command:
```sh
python main.py
```
- Chọn ngôn ngữ (Tiếng Việt/Tiếng Anh) và chọn script từ menu.

## Liên Hệ

- **Telegram**: [thog099](https://t.me/thog099)
- **Kênh Telegram**: [thogairdrops](https://t.me/thogairdrops)
- **Replit**: Thog
