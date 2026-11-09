# Handoff BT2 — Tool Calling và thuật toán

Ngày 09/11/2026. Đã đọc đủ 8 trang đề, tách contract và chuẩn bị bốn thư mục dự án độc lập. Trạng thái hiện tại là chuẩn bị học. Chưa có code, fixture, dependency hoặc kết quả chạy của BT2.

| Bài | Thư mục | Kết quả nghiệp vụ |
|---|---|---|
| 01 | `01_invoice_reconciliation` | Tìm đúng hai giao dịch trả đủ phần hóa đơn còn thiếu |
| 02 | `02_production_capacity` | Tính tốc độ tối thiểu và chọn máy rảnh chậm nhất vẫn kịp ca |
| 03 | `03_notification_schedule` | Xếp lịch gửi đề xuất theo opt-in và khoảng cách tối thiểu |
| 04 | `04_incident_impact` | Tìm dịch vụ có thể bị ảnh hưởng và đường ngắn nhất |

## Phạm vi học và phạm vi nộp

BT2 là bài tập của B7. Tri tự làm từng bài, bắt đầu với thuật toán offline của bài 01. Mặc định dùng vòng tool calling của B4, cấu trúc FastAPI phẳng của B5–B6, SQLAlchemy đồng bộ với SQLite khi nối dữ liệu và lưu trace, rồi test theo mẫu B7. `ChatOpenAI` là lựa chọn khi nối model thật, tên model sẽ chọn và kiểm tra tại bước đó. Xem [stack và cách áp dụng theo từng buổi](TOOL_CALLING_GUIDE.md).

PDF gốc chấm cả web chat, cách trình bày, source frontend/backend và ảnh hoặc video demo. Sau khi backend chạy offline, ưu tiên một trang Streamlit theo mẫu chat trong B7 để hiển thị câu trả lời, dữ liệu và trace. API hoặc Swagger dùng để kiểm tra backend trong quá trình học.

## Bước đầu tiên

Mở [contract bài 01](EXERCISE_CONTRACTS.md#bài-01--đối-soát-hóa-đơn). Vẽ tay bảng giao dịch theo thứ tự xử lý. Với mỗi dòng, Tri ghi `được xét hay bị loại`, `lý do`, `số tiền còn thiếu để thành một cặp` và `đã gặp khoản bù trước đó chưa`. Bước này đạt khi Tri giải thích được vì sao `P1 + P2` là cặp đầu tiên hợp lệ và vì sao một giao dịch không thể tự ghép với chính nó. Sau khi review bảng, giao bước tự viết hàm Python thuần và ca kiểm tra đầu tiên.

Để bắt đầu ở session mới: “Đọc `BaiTap/BT2_ToolCalling/AGENTS.md` và tiếp tục theo handoff. Mình tự viết và chạy bài.”
