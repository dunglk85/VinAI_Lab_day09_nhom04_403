# Routing Decisions Log — Lab Day 09

**Nhóm:** Nhóm 04
**Ngày:** 2026-04-14

---

## Routing Decision #1

**Task đầu vào:**
> SLA xử lý ticket P1 là bao lâu?

**Worker được chọn:** `retrieval_worker`  
**Route reason (từ trace):** `SLA/incident keyword matched: ['p1', 'sla', 'ticket']`  
**MCP tools được gọi:** None  
**Workers called sequence:** `['retrieval_worker', 'synthesis_worker']`

**Kết quả thực tế:**
- final_answer (ngắn): Phản hồi ban đầu là 15 phút, giải quyết (resolution) là 4 giờ.
- confidence: 1.0
- Correct routing? Yes

**Nhận xét:**
Routing hoàn toàn chính xác. Task chứa các keywords rõ ràng về SLA và Incident, Supervisor đã đưa thẳng tới Retrieval Worker để lấy thông tin từ file `sla-p1-2026.pdf`.

---

## Routing Decision #2

**Task đầu vào:**
> Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `policy keyword matched: ['hoàn tiền']`  
**MCP tools được gọi:** None (LLM reasoning based on chunks)  
**Workers called sequence:** `['retrieval_worker', 'policy_tool_worker', 'synthesis_worker']`

**Kết quả thực tế:**
- final_answer (ngắn): Hoàn tiền trong vòng 7 ngày làm việc nếu chưa mở seal.
- confidence: 0.9
- Correct routing? Yes

**Nhận xét:**
Đúng hướng. Supervisor nhận diện được keyword "hoàn tiền" và chuyển sang Policy Worker. Do code trong graph quy định Policy Worker cần context, nên Retrieval Worker đã chạy trước để lấy file `refund-v4.pdf`.

---

## Routing Decision #3

**Task đầu vào:**
> ERR-403-AUTH là lỗi gì và cách xử lý?

**Worker được chọn:** `human_review` (sau đó route về `retrieval_worker`)  
**Route reason (từ trace):** `unknown error code pattern detected (e.g. ERR-xxx), no domain context | human approved → retrieval`  
**MCP tools được gọi:** None  
**Workers called sequence:** `['human_review', 'retrieval_worker', 'synthesis_worker']`

**Kết quả thực tế:**
- final_answer (ngắn): Lỗi thiếu quyền hạn, cần tạo Ticket Jira IT-ACCESS. 
- confidence: 0.8
- Correct routing? Yes

**Nhận xét:**
Đây là minh chứng cho tính năng HITL. Supervisor phát hiện mã lỗi lạ không thuộc các domain cụ thể nên trigger `human_review`. Sau khi "auto-approve", hệ thống mới tiến hành retrieval.

---

## Routing Decision #4 (Bonus)

**Task đầu vào:**
> Ticket P1 lúc 2am. Cần cấp Level 2 access tạm thời cho contractor để cứu hệ thống.

**Worker được chọn:** `policy_tool_worker`  
**Route reason:** `task contains policy/access keyword`

**Nhận xét: Đây là trường hợp routing khó nhất trong lab. Tại sao?**
Vì nó kết hợp cả yếu tố rủi ro cao (P1, 2am) và yếu tố chính sách (cấp quyền). Supervisor phải quyết định xem có cần can thiệp con người ngay lập tức hay cho phép Policy Worker xử lý dựa trên "emergency procedures". 

---

## Tổng kết

### Routing Distribution

| Worker | Số câu được route | % tổng |
|--------|------------------|--------|
| retrieval_worker | 62 | 52% |
| policy_tool_worker | 57 | 47% |
| human_review | 7 | 5% |

### Routing Accuracy

- Câu route đúng: 14 / 15
- Câu route sai (đã sửa bằng cách nào?): 1 (Câu hỏi về contractor lúc đầu bị route nhầm sang retrieval thuần túy, đã sửa prompt supervisor để ưu tiên policy worker khi có từ khóa "access").
- Câu trigger HITL: 1 (q09)

### Lesson Learned về Routing

1. **Keyword-based initial routing là cứu cánh:** Trong môi trường lab, việc kết hợp keyword matching với LLM reasoning giúp Supervisor hoạt động ổn định và nhanh hơn.
2. **Prioritization:** Luôn ưu tiên Policy Worker khi có xung đột keywords vì Policy Worker có khả năng gọi lại Retrieval, nhưng Retrieval Worker thì không thể tự gọi Policy logic.

### Route Reason Quality

Các `route_reason` hiện tại khá tốt (`keyword matched : [...]`). Tuy nhiên, cần bổ sung thêm đoạn trích dẫn logic của LLM nếu dùng LLM để phân loại, giúp debug các case biên (edge cases) dễ dàng hơn.

