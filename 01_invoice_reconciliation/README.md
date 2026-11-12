# Bài 01 — Đối soát hóa đơn

Bài tập thực hành FastAPI, SQLAlchemy, LangChain Tool Calling và Two Sum. Kế toán nhập mã hóa đơn trong câu hỏi tiếng Việt để tìm hai khoản chuyển cộng đúng số tiền còn thiếu. Khi được yêu cầu, app lưu một bản nháp đối soát chờ duyệt. Số dư hóa đơn và trạng thái giao dịch giữ nguyên khi tạo bản nháp.

## Chạy demo trên Windows

Mở PowerShell trong thư mục `01_invoice_reconciliation`. Bài được kiểm trên Python 3.14. Nếu đã có `.venv`, có thể bỏ qua lệnh tạo môi trường.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nếu chưa có `.env`, chép từ `.env.example`. Để chạy demo bằng SQLite trên máy, đặt các giá trị sau trong `.env`.

```dotenv
DATABASE_URL=sqlite:///./demo.db
OPENAI_API_KEY=
OPENAI_MODEL=
```

Nếu dùng Supabase, giữ `DATABASE_URL` của PostgreSQL trong `.env`. Dùng database dành cho dữ liệu mẫu của bài.

```powershell
.\.venv\Scripts\python.exe seed_demo.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

`seed_demo.py` tạo các bảng còn thiếu, nạp hóa đơn `I-77` và năm giao dịch trong đề. Kết quả in ra là `I-77: P1 + P2`.

Mở [http://127.0.0.1:8000](http://127.0.0.1:8000/) và bấm **Thử demo I-77**. App chạy tool tìm cặp trực tiếp và hiện kết quả cùng lịch sử gọi tool. Bảng bên dưới hiển thị hóa đơn, giao dịch và đề xuất đang có trong database.

## Thử chat với OpenAI

Điền `OPENAI_API_KEY` và `OPENAI_MODEL` trong `.env`, rồi khởi động lại Uvicorn. Bấm **Gửi câu hỏi** để thử các câu sau.

- `Hai khoản chuyển nào trả đủ phần còn thiếu của hóa đơn I-77?`
- `Tạo bản nháp đối soát cho hóa đơn I-77 bằng hai giao dịch P1 và P2.`

Sau khi tạo thành công, bản nháp xuất hiện trong bảng **Đề xuất**. FastAPI lưu câu hỏi, các lần gọi tool và câu trả lời vào `chat_trace.jsonl`. Giữ `.env`, `demo.db` và `chat_trace.jsonl` trên máy khi nộp source.

## Vì sao AI cần gọi tool?

Backend dùng `bind_tools` để khai báo các tool. AI đọc câu hỏi tiếng Việt và đề nghị gọi tool với tham số phù hợp. Backend kiểm tên và tham số trước khi chạy, rồi gửi kết quả về model bằng `ToolMessage` có đúng `tool_call_id`. App thực thi tối đa bốn vòng gọi tool. Dữ liệu hóa đơn và giao dịch đến từ DB, còn thuật toán Python quyết định cặp hợp lệ. Model dùng kết quả đó để trả lời người dùng.

| Tool | Việc backend làm |
|---|---|
| `get_open_invoice` | Đọc khách hàng, tiền tệ, số tiền còn thiếu và trạng thái hóa đơn. |
| `list_unmatched_transfers` | Liệt kê mã giao dịch chưa ghép có số tiền dương, đúng khách và tiền tệ. |
| `find_two_transfer_match` | Đọc lại dữ liệu từ DB và dùng Two Sum để tìm cặp giao dịch. |
| `propose_invoice_match` | Kiểm lại hai mã giao dịch và tổng tiền trước khi lưu bản nháp. |

## Two Sum trong bài này

1. Lấy số tiền còn thiếu làm mục tiêu. Lọc các giao dịch cùng khách, cùng tiền tệ, chưa ghép và có số tiền dương. Sắp theo thời điểm nhận, rồi theo mã giao dịch.
2. Với mỗi khoản `amount`, tính `missing_amount - amount` và tra trong `dict` chứa những số tiền đã gặp. Tra trước khi lưu khoản đang xét để một giao dịch không tự ghép với chính nó. Khi số tiền lặp, giữ vị trí xuất hiện đầu tiên.
3. Trả cặp đầu tiên tìm thấy. Nếu duyệt hết mà chưa có cặp, tool trả `no_match`. Sau khi sắp xếp, phần tìm cặp mất trung bình `O(n)` thời gian và dùng tối đa `O(n)` bộ nhớ.

Với `I-77`, khoản còn thiếu là **1.500.000 VND**. `P4` thuộc khách khác và `P5` dùng USD, nên cả hai bị loại. `P1` là 900.000 VND, `P2` và `P3` đều là 600.000 VND. `P2` đến sớm hơn nên kết quả là **P1 + P2**.

## Chạy test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s test -v
```

Hai test trong repo kiểm ca tìm được cặp có giao dịch ở chỉ số `0` và ca một giao dịch không thể tự ghép. Các test Two Sum chạy bằng Python thuần.

## Vị trí source

- [`frontend/index.html`](frontend/index.html) là trang HTML/CSS/JavaScript được FastAPI phục vụ tại `/`.
- [`app/main.py`](app/main.py) khai báo các endpoint và điều phối vòng gọi tool.
- [`app/tools.py`](app/tools.py) đọc dữ liệu, kiểm điều kiện đối soát và lưu đề xuất.
- [`app/algorithm.py`](app/algorithm.py) chứa hàm Two Sum độc lập.
- [`app/model_db.py`](app/model_db.py) khai báo các bảng. [`seed_demo.py`](seed_demo.py) tạo bảng và nạp dữ liệu mẫu theo [đề bài, trang 4](../03-11-2026-12-31-55-bai-tap-langchain-tool-calling-va-thuat-toan.pdf#page=4).
