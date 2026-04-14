# Routing Decisions Log — Lab Day 09

**Nhóm:** ___________  
**Ngày:** ___________

> **Hướng dẫn:** Ghi lại ít nhất **3 quyết định routing** thực tế từ trace của nhóm.
> Không ghi giả định — phải từ trace thật (`artifacts/traces/`).
> 
> Mỗi entry phải có: task đầu vào → worker được chọn → route_reason → kết quả thực tế.

---

## Routing Decision #1

**Task đầu vào:**
> _________________

**Worker được chọn:** `___________________`  
**Route reason (từ trace):** `___________________`  
**MCP tools được gọi:** _________________  
**Workers called sequence:** _________________

**Kết quả thực tế:**
- final_answer (ngắn): _________________
- confidence: _________________
- Correct routing? Yes / No

**Nhận xét:** _(Routing này đúng hay sai? Nếu sai, nguyên nhân là gì?)_

_________________

---

## Routing Decision #2

| ID | Câu hỏi (Task) | Route Decision | Lý do (Reason) | Risk High? |
|----|--------------|----------------|---------------|------------|
| 1 | SLA xử lý ticket P1 là bao lâu? | `retrieval_worker` | task is a general knowledge retrieval request | Yes (incident) |
| 2 | Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày? | `policy_tool_worker` | task relates to policy analysis or access control | No |
| 3 | ERR-403-AUTH là lỗi gì và cách xử lý? | `human_review` | unknown error code or vague high-risk task → human review | Yes |

---

## Routing Decision #3

**Task đầu vào:**
> ERR-403-AUTH là lỗi gì và cách xử lý?

**Worker được chọn:** `human_review`  
**Route reason (từ trace):** `unknown error code or vague high-risk task → human review`  
**MCP tools được gọi:** None  
**Workers called sequence:** `supervisor -> human_review`

**Kết quả thực tế:**
- final_answer (ngắn): Cần kỹ thuật viên kiểm tra log hệ thống.
- confidence: 1.0
- Correct routing? Yes

**Nhận xét:**

Đây là cơ chế an toàn quan trọng của kiến trúc Multi-Agent để tránh hallucination nguy hiểm khi gặp mã lỗi lạ.

---

## Routing Decision #4 (tuỳ chọn — bonus)

**Task đầu vào:**
> _________________

**Worker được chọn:** `___________________`  
**Route reason:** `___________________`

### Case 1: Knowledge Retrieval (SLA Policy)
- **Input:** "SLA xử lý ticket P1 là bao lâu?"
- **Routing Decision:** `retrieval_worker`
- **Tại sao đúng?** Câu hỏi này yêu cầu tìm kiếm thông tin tĩnh trong tài liệu `sla_p1_2026.txt`. Không cần thực hiện logic kiểm tra điều kiện phức tạp hay gọi tool đặc thù của policy.
- **Quan sát:** Supervisor nhận diện keyword "SLA" và "P1", đánh dấu `risk_high=True` nhưng vẫn gửi cho retrieval vì đây là câu hỏi tra cứu.

### Case 2: Policy Analysis (Refund)
- **Input:** "Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?"
- **Routing Decision:** `policy_tool_worker`
- **Tại sao đúng?** Từ khóa "hoàn tiền" kích hoạt logic policy. Worker này sẽ kiểm tra `policy_refund_v4.txt` và có thể gọi MCP tool nếu cần định danh khách hàng.
- **Quan sát:** Việc tách riêng giúp Synthesis nhận được context đã được filter kỹ hơn bởi Policy Worker.

### Case 3: Human-in-the-Loop (Unknown Error)
- **Input:** "ERR-403-AUTH là lỗi gì và cách xử lý?"
- **Routing Decision:** `human_review`
- **Tại sao đúng?** Task chứa mã lỗi lạ "ERR-" và được đánh dấu `risk_high`. Hệ thống không tự tin xử lý lỗi hệ thống chưa biết nên chuyển cho con người.
- **Quan sát:** Đây là cơ chế an toàn quan trọng của kiến trúc Multi-Agent để tránh hallucination nguy hiểm.

---

## 4. Đánh giá độ chính xác của Supervisor

**Tỉ lệ routing đúng (ước tính):** 95% 

**Các trường hợp Supervisor hay nhầm:**
1. Các câu hỏi có cả keyword policy và retrieval (ví dụ: "SLA của quy trình hoàn tiền").
2. Câu hỏi quá ngắn, thiếu keyword rõ ràng.

**Cải tiến đề xuất:**
- Sử dụng LLM-based Router thay vì keyword-based để hiểu ngữ nghĩa tốt hơn.
- Thêm cơ chế feedback loop: nếu worker báo "không phải việc của tôi", supervisor route lại.

**Nhận xét: Đây là trường hợp routing khó nhất trong lab. Tại sao?**

_________________

---

## Tổng kết

### Routing Distribution

| Worker | Số câu được route | % tổng |
|--------|------------------|--------|
| retrieval_worker | ___ | ___% |
| policy_tool_worker | ___ | ___% |
| human_review | ___ | ___% |

### Routing Accuracy

> Trong số X câu nhóm đã chạy, bao nhiêu câu supervisor route đúng?

- Câu route đúng: ___ / ___
- Câu route sai (đã sửa bằng cách nào?): ___
- Câu trigger HITL: ___

### Lesson Learned về Routing

> Quyết định kỹ thuật quan trọng nhất nhóm đưa ra về routing logic là gì?  
> (VD: dùng keyword matching vs LLM classifier, threshold confidence cho HITL, v.v.)

1. ___________________
2. ___________________

### Route Reason Quality

> Nhìn lại các `route_reason` trong trace — chúng có đủ thông tin để debug không?  
> Nếu chưa, nhóm sẽ cải tiến format route_reason thế nào?

_________________
