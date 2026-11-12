# Yêu cầu chung
- Làm một web app có ô chat. Người dùng hỏi bằng tiếng Việt và xem được câu trả lời, dữ liệu được dùng, cùng
lịch sử công cụ đã gọi.
- Định nghĩa công cụ bằng LangChain @tool, gắn vào model bằng bind_tools. Khi model trả tool_calls, backend
kiểm tra tên công cụ và tham số, tự chạy công cụ, rồi trả kết quả về model bằng ToolMessage có đúng
tool_call_id. Lặp có giới hạn bước cho đến khi model trả câu trả lời cuối.
- Tool call an toàn, không cho LLM sử dụng Database tùy ý
- Không bịa kết quả

# Bài 1
## Các tools cho AI
- get_open_invoice(invoice_id)
Input: invoice_id
Output: customer_id, currency, missing_money, status
Algo: SQL
SELECT * FROM Invoice
WHERE Invoice.id == invoice_id

- list_unmatched_transfers(customer_id, currency)
Input: customer_id, currency
Output: transfer_id[]
Algo: SQL
SELECT * FROM Transfer
WHERE Transfer.customer_id == customer_id AND Transfer.currency == currency

- find_two_transfer_match(invoice_id)
Input: invoice_id
Output: transfer_id[2] or None
Algo: 2 Sum

- propose_invoice_match(invoice_id, transfer_ids)
Input: invoice_id, transfer_ids
Output: Proposal
Algo: Create and add to Propose table

Câu hỏi
- Yield khác gì return?