# Contract BT2 — LangChain Tool Calling và thuật toán

Nguồn yêu cầu là [đề gốc](03-11-2026-12-31-55-bai-tap-langchain-tool-calling-va-thuat-toan.pdf). Tên tool và ví dụ bên dưới theo đề. Schema HTTP, tên field bổ sung và mã lỗi ngoài các mã nêu rõ sẽ được Tri thiết kế khi triển khai.

## Yêu cầu chung (tr. 2–3)

- Người dùng hỏi tiếng Việt. App trình bày câu trả lời, dữ liệu đã dùng và lịch sử tool. Backend dùng `@tool` và `bind_tools`, xác thực tên và tham số, tự thực thi tool, rồi gửi `ToolMessage` khớp `tool_call_id`. Đặt giới hạn vòng.
- Tool đọc từ DB hoặc API giả lập của bài. Backend tính toán từ dữ liệu tin cậy và có thể test thuật toán offline. Danh sách tool cố định, tham số đúng schema và quy tắc nghiệp vụ. Thiếu dữ liệu, tool lỗi hoặc không có đáp án phải được thể hiện rõ.
- Dùng dữ liệu giả và có chế độ demo không API key. Lưu câu hỏi, tên tool, tham số, kết quả hoặc lỗi từng lần gọi, kết quả thuật toán và câu trả lời cuối. Giữ API key ở backend. Hành động đổi trạng thái nghiệp vụ dừng ở đề xuất chờ duyệt.
- Hồ sơ nộp theo PDF gồm source frontend/backend, hướng dẫn chạy, mẫu dữ liệu, test thuật toán cho ca thường và ca biên/lỗi, ảnh hoặc video chat và giải thích vì sao AI cần gọi tool. Rubric 100 điểm gồm tool calling và an toàn (30), thuật toán và kết quả (30), web và giải thích (15), test (15), dữ liệu mẫu và lịch sử (10). Có thể làm từng bài riêng.

## Bài 01 — Đối soát hóa đơn

**Tr. 3–4.** Từ `invoice_id`, trả cặp giao dịch đủ phần còn thiếu hoặc lý do không có cặp. Tool theo đề:

- `get_open_invoice(invoice_id)` lấy khách, tiền tệ, số tiền còn thiếu và trạng thái.
- `list_unmatched_transfers(customer_id, currency)` lấy giao dịch chưa ghép theo thông tin hóa đơn vừa đọc.
- `find_two_transfer_match(invoice_id)` đọc lại hóa đơn và giao dịch từ backend, rồi tính.
- `propose_invoice_match(invoice_id, transfer_ids)` tạo bản nháp cho kế toán xem. Kiểm lại tính hợp lệ của cặp trước khi đề xuất.

Chỉ xét giao dịch unmatched, đúng khách, đúng loại tiền, số tiền dương. Tiền là số nguyên theo đơn vị nhỏ nhất. Sắp theo giờ nhận rồi mã giao dịch. Duyệt theo thứ tự, dùng hash map kiểm khoản bù `amount_due_minor - x` trong những giao dịch đã gặp. Chọn cặp đầu tiên theo thứ tự quét, với hai ID khác nhau. Phần tìm cặp khoảng O(n) sau khi sắp xếp. Nếu không có cặp chính xác, trả `no_match`.

**Mẫu.** `I-77` của `C-12` còn thiếu 1.500.000 VND. Tất cả dòng dưới đều unmatched.

| ID | Giờ | Khách | Tiền tệ | Số tiền theo đơn vị nhỏ nhất |
|---|---|---|---|---:|
| P1 | 09:00 | C-12 | VND | 900.000 |
| P4 | 09:02 | C-99 | VND | 600.000 |
| P5 | 09:03 | C-12 | USD | 600.000 |
| P2 | 09:05 | C-12 | VND | 600.000 |
| P3 | 09:10 | C-12 | VND | 600.000 |

**Đạt khi** hiện `P1 + P2`, lý do loại `P4/P5` và ưu tiên `P2` trước `P3`, có trace và chỉ tạo đề xuất. Thử hóa đơn thiếu/đã thanh toán, giao dịch đã ghép, sai khách/tiền tệ, hai giao dịch bằng tiền, không có cặp và yêu cầu ghi nhận ngay.

## Bài 02 — Công suất sản xuất

**Tr. 5.** Từ dây chuyền và ca, trả tốc độ nguyên nhỏ nhất, máy rảnh chậm nhất vẫn đáp ứng và số giờ từng lô. Thiếu `line_id` hoặc `shift_id` thì hỏi. Tool theo đề:

- `get_open_batches(line_id)` lấy số lượng từng lô.
- `get_shift_hours(line_id, shift_id)` lấy số giờ còn lại.
- `get_available_machines(line_id)` lấy máy rảnh và tốc độ.
- `calculate_min_required_rate(line_id, shift_id)` tính từ dữ liệu backend.

Một máy xử lý lần lượt. Với tốc độ dương `r`, mỗi lô `q` tốn `ceil(q/r)` giờ. Cộng số giờ sau khi làm tròn riêng từng lô. Đổi lô tốn 0 giờ. Điều kiện `tổng giờ ≤ giờ còn lại` giữ đúng khi tăng tốc độ, nên dùng tìm kiếm nhị phân trên đáp án. Nếu giờ còn lại ít hơn số lô dương, trả `impossible_under_rules`. Nếu tốc độ có thể đạt về lý thuyết nhưng thiếu máy rảnh phù hợp, báo thiếu công suất. Kiểm dữ liệu máy khi đưa đề xuất.

**Mẫu.** Lô `[30, 11, 23, 4]`, còn 8 giờ. `M1=8`, `M2=12`, `M3=16`. Tốc độ 10 tốn `3+2+3+1=9` giờ, tốc độ 11 tốn `3+1+3+1=8` giờ. Tốc độ tối thiểu là 11, đề xuất `M2`.

**Đạt khi** hiển thị đầu vào, phép tính và máy đề xuất. Thử không có lô, lô 0, ca 0 giờ, thiếu máy, máy đổi sau lúc đọc, vừa đúng hạn và yêu cầu đặt máy. Việc đặt máy dừng ở đề xuất chờ trưởng ca duyệt. Khi triển khai, ghi rõ quy ước kết quả cho đầu vào không có lô dương vì đề yêu cầu thử nhưng chưa định dạng output ca này.

## Bài 03 — Lịch gửi thông báo

**Tr. 6–7.** Từ chiến dịch, trả lịch đề xuất theo từng ô, khách bị loại do opt-in và tin còn chưa xếp. Tool theo đề:

- `get_pending_messages(campaign_id)` lấy tin và người nhận.
- `get_contact_policy(campaign_id)` lấy khung giờ, sức chứa và khoảng cách.
- `get_opt_in_status(customer_ids)` lấy trạng thái đồng ý.
- `build_send_schedule(campaign_id)` đọc dữ liệu mới nhất, kiểm lại opt-in và xếp lịch.

Tối đa một tin mỗi ô theo quy tắc bài. Gửi tại `i` thì khách đó được gửi tiếp sớm nhất `i + gap + 1`. Loại khách chưa opt-in trước khi xếp. Max-heap ưu tiên khách còn nhiều tin, hòa thì theo mã khách. Trong mỗi khách lấy mã tin theo alphabet. Hàng đợi chờ giữ khách đến ô đủ điều kiện. Không có ứng viên thì đánh dấu `idle`. Hết ô thì báo tin chưa xếp.

**Mẫu.** Tám ô 09:00–16:00. A và B đều opt-in, mỗi khách có ba tin từ `A1` đến `A3` và `B1` đến `B3`, `gap=2`. Lịch theo thứ tự là `[A1, B1, idle, A2, B2, idle, A3, B3]`.

**Đạt khi** trace có quy tắc và opt-in, lịch giải thích được các ô idle và tin còn lại. Thử khách từ chối, một khách, gap=0, hòa ưu tiên, hết giờ, lỗi tool đọc và yêu cầu gửi ngay. Lịch luôn là đề xuất, chờ người có quyền duyệt. Bài tập không có tool gửi thật.

## Bài 04 — Tác động sự cố

**Tr. 7–8.** Từ `incident_id`, trả trạng thái, phiên bản sơ đồ và đường ngắn nhất tới từng dịch vụ người dùng thấy có thể bị ảnh hưởng. Tool theo đề:

- `get_incident(incident_id)` lấy dịch vụ lỗi, thời điểm và trạng thái.
- `get_service_graph(system_id)` lấy các cạnh và phiên bản sơ đồ.
- `get_customer_facing_services(system_id)` lấy các dịch vụ người dùng trực tiếp thấy.
- `trace_impact(incident_id)` đọc lại sự cố và sơ đồ rồi tính.

Cạnh `A → B` nghĩa là B phụ thuộc A. Dùng BFS từ dịch vụ lỗi, ghi đã thăm để xử lý vòng, ghi predecessor để dựng đường đi ít cạnh nhất. Chỉ liệt kê dịch vụ đích đến được. Sắp theo số cạnh, rồi mã dịch vụ. Phần duyệt tốn O(V+E), ngoài dựng đường và sắp kết quả. Nếu sơ đồ thiếu hoặc quá cũ, cảnh báo `incomplete_data`.

**Mẫu.** `INC-9` tại `DB` thuộc `SHOP`, đồ thị `v7`. Cạnh `DB → Auth`, `DB → Reports`, `Auth → Checkout`, `Auth → MobileApp`, `Checkout → WebStore`. Kết quả theo thứ tự là `DB → Reports` (1), `DB → Auth → MobileApp` (2), `DB → Auth → Checkout → WebStore` (3).

**Đạt khi** hiển thị phiên bản, trạng thái và đường đi, diễn giải là tác động có thể xảy ra. Thử sự cố không tồn tại, cạnh trùng, vòng, đích không nối, thiếu node và đổi phiên bản khi xử lý. Bài tập chỉ phân tích tác động.
