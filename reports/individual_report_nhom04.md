# Individual Report — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Ngô Gia Bảo
**MSSV:** 2A202600385
**Nhóm:** AI in Action (Nhóm 04)

---

## 1. Đóng góp cá nhân (Individual Contributions)

Trong bài Lab này, tôi chịu trách nhiệm chính về:
1. **Implement Supervisor Node (`graph.py`):** Xây dựng logic phân loại query dựa trên từ khóa và độ rủi ro (Risk-based Routing).
2. **Xây dựng Synthesis Worker (`workers/synthesis.py`):** Thiết lập kết nối với Gemini/OpenAI, xử lý lỗi Rate Limit bằng Retry/Backoff và xây dựng hệ thống Fallback an toàn khi không có LLM.
3. **Phân tích Trace & Evaluation:** Chạy đánh giá 15 test questions và viết báo cáo so sánh hiệu năng giữa Single-Agent và Multi-Agent.

---

## 2. Phần tâm đắc nhất (Favorite Part)

Điều tôi thấy thú vị nhất là cơ chế **Supervisor-Worker routing**. Thay vì để một Model duy nhất gánh vác mọi task (dễ bị quá tải context hoặc "hallucinate" lỗi hệ thống), việc tách nhỏ thành các Worker chuyên biệt giúp tôi kiểm soát được luồng dữ liệu. Đặc biệt là khi tích hợp **MCP Tools**, các Worker có thể tự do gọi các công cụ bên ngoài mà không làm ảnh hưởng đến tính ổn định của toàn hệ thống.

---

## 3. Khó khăn và cách giải quyết (Challenges & Solutions)

**Khó khăn:** Gặp lỗi 429 (Rate Limit) liên tục khi chạy Evaluation với Gemini Free Tier, khiến các kết quả Synthesis bị trống.

**Cách giải quyết:**
- Tôi đã viết thêm một lớp logic Retry với thời gian chờ tăng dần (exponential backoff).
- Quan trọng hơn, tôi đã xây dựng hàm `_fallback_synthesis` sử dụng regex và keyword extraction để trích xuất trực tiếp câu trả lời từ context thô. Điều này giúp hệ thống vẫn có thể "trả lời" được các câu hỏi cơ bản ngay cả khi mất kết nối LLM hoàn toàn.

---

## 4. Bài học rút ra (Key Takeaways)

1. **Multi-Agent không phải lúc nào cũng tốt hơn:** Đối với các tác vụ đơn giản, nó làm tăng độ trễ và chi phí. Tuy nhiên, với hệ thống phức tạp, nó là chìa khóa để gỡ lỗi và mở rộng.
2. **Trace là "máu" của hệ thống:** Nếu không có trace, việc debug một chuỗi các agent gọi nhau sẽ là một cơn ác mộng.
3. **Sự đánh đổi:** Việc tăng tính Modular đồng nghĩa với việc quản lý State khó khăn hơn. Cần một Contract (Interface) rất rõ ràng trước khi bắt đầu code.
