# Báo Cáo Nhóm — Lab Day 09: Multi-Agent Orchestration

**Tên nhóm:** AI in Action  
**Thành viên:**
| Tên | Vai trò | Email |
|-----|---------|-------|
| Ngô Gia Bảo | Supervisor & Synthesis Owner | bao.ngogia@gmail.com |
| Trần Thị B | Worker Owner | b@gmail.com |
| Lê Văn C | MCP Owner | c@gmail.com |
| Phạm Thị D | Trace & Docs Owner | d@gmail.com |

**Ngày nộp:** 2026-04-14  
**Repo:** [N/A]

---

## 1. Kiến trúc nhóm đã xây dựng

Hệ thống của chúng tôi sử dụng mô hình **Supervisor-Worker** với cấu trúc 3 Worker chính và 1 nút Human Review để xử lý các trường hợp rủi ro cao.

**Hệ thống tổng quan:**
- 1 Supervisor (`graph.py`) chịu trách nhiệm phân loại intent.
- 3 Workers: Retrieval (với ChromaDB), Policy Tool (với rule-based logic + MCP), và Synthesis (với Gemini LLM + fallback).
- 1 nút Human Review kích hoạt khi hệ thống gặp mã lỗi không rõ (`ERR-`) hoặc các yêu cầu khẩn cấp không tự tin xử lý.

**Routing logic cốt lõi:**
Chúng tôi sử dụng **Keyword-based Routing kết hợp Risk Assessment**. Supervisor tìm kiếm các từ khóa đặc trưng (hoàn tiền, SLA, P1, access) để chọn worker. Ngoài ra, nó còn quét các tín hiệu rủi ro (emergency, 2am) để đặt cờ `risk_high`.

**MCP tools đã tích hợp:**
- `search_kb`: Tìm kiếm kiến thức bổ sung từ vector database.
- `get_ticket_info`: Lấy thông tin ticket Jira (mock).
- `check_access_permission`: Kiểm tra quyền truy cập dựa trên level và vai trò.

---

## 2. Quyết định kỹ thuật quan trọng nhất

**Quyết định:** Tích hợp cơ chế **Rule-based Fallback cho Synthesis Worker**.

**Bối cảnh vấn đề:**
Trong quá trình lab, chúng tôi gặp vấn đề với Quota API Gemini và mã lỗi 401 của OpenAI. Nếu không có LLM, hệ thống sẽ trả về lỗi, làm sụp đổ toàn bộ pipeline cho các câu hỏi đơn giản.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Chỉ dùng Gemini | Dễ code, trình bày đẹp | Dễ bị rate limit (429) làm hỏng demo |
| Thêm Retry/Backoff | Giúp vượt qua lỗi tạm thời | Vẫn tốn thời gian chờ đợi |
| **Rule-based Fallback** | Đảm bảo luôn trả lời đúng context | Trình bày không mượt bằng LLM |

**Phương án đã chọn và lý do:**
Chúng tôi chọn kết hợp **Retry + Fallback**. Nếu LLM fail sau 3 lần thử, hệ thống sẽ gọi hàm `_fallback_synthesis` để trích xuất text trực tiếp từ context và định dạng thành bullet points có citation. Điều này đảm bảo tính ổn định tối đa cho hệ thống.

**Bằng chứng từ code:**
```python
def _call_llm(messages: list) -> str:
    # ... try OpenAI, then Gemini with Retries ...
    if errors:
        print(f"  ⚠️  LLM errors: {errors}")
    return _fallback_synthesis(messages)
```

---

## 3. Kết quả grading questions

**Tổng điểm raw ước tính:** 90 / 96 (Dựa trên 15 câu test_questions)

**Câu pipeline xử lý tốt nhất:**
- ID: q02 — "Hoàn tiền Flash Sale". Reason: Policy Worker nhận diện chính xác ngoại lệ trong code và trích xuất đúng lý do không được hoàn.

**Câu pipeline fail hoặc partial:**
- ID: q08 — "Quy trình P1". Reason: Context quá dài khiến fallback synthesis trích xuất không đủ các bước chi tiết.

**Câu gq09 (multi-hop):** 
Trace ghi nhận Supervisor gọi `policy_tool_worker`, sau đó worker này gọi MCP `check_access_permission` và kết hợp với dữ liệu từ `access_control_sop.txt` để trả lời.

---

## 4. So sánh Day 08 vs Day 09

**Metric thay đổi rõ nhất:**
- **Debug time:** Giảm từ 20 phút xuống còn 5 phút nhờ JSON trace rõ ràng.
- **Latency:** Tăng từ 4s lên 6.7s do thêm lớp Supervisor và MCP overhead.

**Điều nhóm bất ngờ nhất:**
Khả năng "tự hiểu" của hệ thống khi mình tách biệt concern. Dù Supervisor chỉ là keyword-based, nhưng vì Task-Worker contract chặt chẽ nên kết quả cuối cùng rất grounded.

**Trường hợp multi-agent KHÔNG giúp ích:**
Đối với các câu hỏi FAQ cực kỳ đơn giản (SLA là gì?), kiến trúc này làm chậm phản hồi mà không tăng độ chính xác so với Day 08.

---

## 5. Phân vùng và đánh giá nhóm

**Phân công thực tế:**
- Ngô Gia Bảo: Build Supervisor Routing & Synthesis Worker (Sprint 1-2).
- Trần Thị B: Build Retrieval Worker & Indexing (Sprint 2).
- Lê Văn C: MCP Server & Tool dispatching (Sprint 3).
- Phạm Thị D: Trace evaluation & Documentation (Sprint 4).

**Điều nhóm làm tốt:**
Phối hợp contract interface sớm (yaml) nên khi ghép code rất ít lỗi.

**Điều nhóm làm chưa tốt:**
Quản lý API Key chưa tốt dẫn đến bị rate limit giữa chừng.

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì?

Chúng tôi sẽ chuyển Supervisor sang dùng **LLM Routing** thay vì keyword để xử lý các câu hỏi lắt léo mang tính chất so sánh giữa các chính sách khác nhau.
