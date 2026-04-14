# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Ngô Gia Bảo  
**Vai trò trong nhóm:** Supervisor Owner / Synthesis Worker Lead  
**Ngày nộp:** 2026-04-14  

---

## 1. Tôi phụ trách phần nào? (100–150 từ)

Trong bài Lab này, tôi chịu trách nhiệm chính về việc xây dựng "bộ não" điều phối của hệ thống và giải pháp tổng hợp câu trả lời an toàn.

**Module/file tôi chịu trách nhiệm:**
- File chính: `graph.py`, `workers/synthesis.py`
- Functions tôi implement: `supervisor_node`, `_call_llm`, `_fallback_synthesis`, `synthesis_worker_node`

**Cách công việc của tôi kết nối với phần của thành viên khác:**
Công việc của tôi là điểm bắt đầu và điểm kết thúc của Pipeline. Tôi nhận task từ User, phân loại và gửi đến Retrieval Worker (do bạn B làm) hoặc Policy Worker (do bạn C làm). Sau khi các Worker trả về kết quả, tôi tiếp nhận dữ liệu đó vào Synthesis Worker để tạo ra câu trả lời cuối cùng cho người dùng.

**Bằng chứng:** 
Các hàm `supervisor_node` trong `graph.py` và toàn bộ logic xử lý LLM trong `workers/synthesis.py` đều do tôi hoàn thiện, bao gồm cả việc cấu hình Retry và Fallback.

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

**Quyết định:** Sử dụng **Keyword-based Routing kết hợp Risk Assessment** cho Supervisor thay vì dùng LLM Classifier.

**Lý do:**
Ban đầu nhóm định dùng một LLM nhỏ để phân loại query. Tuy nhiên, tôi nhận thấy qua các câu hỏi test, các từ khóa như "hoàn tiền", "P1", "SLA" xuất hiện rất đặc trưng. Việc dùng Regex/Keyword matching giúp giảm độ trễ xuống gần như bằng 0ms (~2ms trong trace) so với việc gọi LLM (~1000ms), đồng thời tránh lãng phí token.

Tôi cũng thêm logic đánh dấu `risk_high=True` khi phát hiện các từ khóa rủi ro như "khẩn cấp" hoặc "emergency", điều này giúp kích hoạt chế độ Human-in-the-Loop một cách chủ động.

**Trade-off đã chấp nhận:**
Hệ thống có thể routing sai nếu người dùng đặt câu hỏi quá lắt léo mà không chứa từ khóa định danh. Tuy nhiên, tôi đã xử lý bằng cách đặt route mặc định là `retrieval_worker`.

**Bằng chứng từ trace/code:**
```python
if any(kw in task for kw in risk_keywords):
    risk_high = True
    route_reason += " | risk_high flagged (incident or emergency)"
```
Trace ID `run_20260414_111839.json` ghi nhận routing chính xác cho câu hỏi SLA với latency supervisor chỉ 15ms.

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

**Lỗi:** LLM Synthesis bị treo hoặc trả về chuỗi trống khi gặp lỗi Rate Limit (429) của Gemini API.

**Symptom:**
Khi chạy file `eval_trace.py`, hệ thống liên tục báo lỗi `429 You exceeded your current quota`. Answer trả về là chuỗi rỗng hoặc thông báo lỗi khô khan, làm giảm điểm đánh giá của toàn bộ pipeline.

**Root cause:**
Tài khoản Gemini Free Tier bị giới hạn số lượng request mỗi phút. Code cũ không có cơ chế đợi (wait) và thử lại (retry).

**Cách sửa:**
Tôi đã implement cơ chế **Exponential Backoff Retry** trong hàm `_call_llm`. Hệ thống sẽ đợi 5s, sau đó 10s nếu gặp lỗi 429. Bên cạnh đó, tôi xây dựng hàm `_fallback_synthesis` để trích xuất text trực tiếp từ context nếu sau 3 lần retry vẫn thất bại.

**Bằng chứng trước/sau:**
- **Trước khi sửa:** Trace báo `[SYNTHESIS ERROR] Không thể gọi LLM`.
- **Sau khi sửa:** Trace báo `⏳ Gemini rate limit (gemini-2.0-flash), retry in 5s...` và sau đó trả về câu trả lời có citation đầy đủ.

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

**Tôi làm tốt nhất ở điểm nào?**
Tôi tự tin vào khả năng xử lý lỗi ngoại lệ (exception handling). Việc xây dựng cơ chế Fallback giúp hệ thống của nhóm tôi là nhóm duy nhất vẫn trả lời được bài Lab ngay cả khi toàn bộ API key bị khóa.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Phần routing logic hiện tại vẫn còn đơn giản, chưa xử lý tốt các câu hỏi "multi-intent" (câu hỏi chứa 2 yêu cầu khác nhau).

**Nhóm phụ thuộc vào tôi ở đâu?**
Nếu tôi không hoàn thành `graph.py` và `synthesis.py`, toàn bộ pipeline sẽ không thể chạy end-to-end, vì đây là hai nút thắt đầu và cuối của graph.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

Tôi sẽ thử chuyển Supervisor sang dùng **Small Language Model (như Phi-3 hoặc Gemma 2B)** để routing vì trace của câu q11 cho thấy nếu người dùng dùng từ đồng nghĩa, hệ thống keyword hiện tại vẫn có thể bỏ sót.
