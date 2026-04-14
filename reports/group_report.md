# Báo Cáo Nhóm — Lab Day 09: Multi-Agent Orchestration

**Tên nhóm:** Nhóm 04  
**Môn học:** AI in Action  
**Ngày nộp:** 2026-04-14  

---

## 1. Kiến trúc nhóm đã xây dựng

Nhóm 04 đã triển khai hệ thống hỏi đáp nội bộ theo kiến trúc **Supervisor - Worker** linh hoạt. Luồng xử lý được quản lý tập trung bởi một `Supervisor Node` (trong `graph.py`), có nhiệm vụ phân tích ý định người dùng và định tuyến (routing) đến các công nhân (Worker) chuyên trách:

- **retrieval_worker**: Thực hiện tra cứu ngữ nghĩa (Semantic Search) trên kho tài liệu ChromaDB.
- **policy_tool_worker**: Xử lý các yêu cầu phức tạp về chính sách, kết hợp LLM Reasoning và gọi công cụ (Tool Call) thông qua giao thức MCP.
- **synthesis_worker**: Tổng hợp dữ liệu từ các worker trước đó thành câu trả lời cuối cùng, đảm bảo có citation và độ tin cậy (confidence).

Nhóm cũng tích hợp một **Mock MCP Server** (`mcp_server.py`) đóng vai trò là một "Hub" cung cấp 4 công cụ thực thi: tra cứu KB, kiểm tra Ticket Jira, kiểm tra quyền truy cập và tạo Ticket mới. Điểm đặc sắc là cơ chế **Human-in-the-Loop (HITL)** được kích hoạt tự động khi Supervisor phát hiện các yêu cầu có độ rủi ro cao (risk_high).

## 2. Quyết định kỹ thuật quan trọng nhất

Quyết định kỹ thuật mang tính chiến lược của nhóm là việc **Xây dựng hệ thống dựa trên dấu vết thực thi (Trace-Centric Architecture)**. Thay vì chỉ quan tâm đến câu trả lời cuối cùng, nhóm tập trung vào việc ghi lại chi tiết từng bước đi của dữ liệu.

Quyết định này mang lại ba lợi ích cốt lõi:
1. **Routing thông minh & Tối ưu latency:** Ngô Gia Bảo (Supervisor Lead) đã chọn dùng *Keyword-based Routing kết hợp Risk Assessment*. Việc này giúp giảm độ trễ của bước Supervisor xuống còn ~2ms (so với ~1000ms nếu dùng LLM), đồng thời đảm bảo tính an toàn qua việc gắn tag `risk_high`.
2. **Giao thức MCP chuẩn hóa:** Lê Kim Dung (MCP Owner) đã xây dựng một *Centralized Dispatch Layer*. Điều này giúp các Worker chỉ cần gửi Schema JSON mà không cần quan tâm đến logic bên trong công cụ, giúp hệ thống dễ dàng mở rộng sang các API thật sau này.
3. **Bằng chứng thực nghiệm:** Nguyễn Dương Ninh (Trace Owner) đã dùng dữ liệu từ 119 trace thực tế trong `artifacts/eval_report.json` để chứng minh hiệu quả của hệ thống, thay vì mô tả cảm tính.

## 3. Kết quả chạy và quan sát từ trace

Dựa trên dữ liệu đánh giá 15 câu hỏi chuẩn (GQ01-GQ15), nhóm ghi nhận các chỉ số ấn tượng:
- **Tỉ lệ Routing chính xác:** Các câu FAQ ngắn được dẫn sang `retrieval_worker` (52%), trong khi các câu về thủ tục/quyền hạn đi thẳng vào `policy_tool_worker` (47%).
- **Sử dụng công cụ:** 44% số yêu cầu đã kích hoạt gọi công cụ MCP (đặc biệt là `get_ticket_info` và `check_access_permission`).
- **Độ tin cậy:** Confidence trung bình đạt **0.54**, với các câu trả lời đều có trích dẫn nguồn (source citation) rõ ràng.
- **Tính an toàn (HITL):** Tỉ lệ kích hoạt duyệt từ con người đạt 5% cho các tình huống khẩn cấp hoặc mã lỗi chưa xác định (`ERR-403-AUTH`).

Ví dụ tiêu biểu nhất là câu **GQ15**: Trace cho thấy Supervisor đã nhận diện được yêu cầu phức tạp, định tuyến tới `policy_tool_worker`, worker này gọi đồng thời 3 công cụ MCP để kiểm tra ticket và quyền truy cập trước khi Synthesis tổng hợp đáp án cuối cùng.

## 4. So sánh Day 08 và Day 09

| Tiêu chí | Day 08 (Single-Agent) | Day 09 (Multi-Agent) |
| :--- | :--- | :--- |
| **Kiến trúc** | Linear Pipeline (Tuần tự) | Directed Graph (Supervisor-Worker) |
| **Khả năng Debug** | Khó (Black box) | Dễ (Mỗi bước đều có Trace riêng) |
| **Độ trễ** | Thấp (~2-3s) | Cao hơn (~6.6s do overhead log/routing) |
| **Độ linh hoạt** | Kém (Cần thay Prompt lớn) | Tốt (Thêm worker/tool mới rất nhanh) |
| **Độ chính xác** | Dễ bị hallucination ở case khó | Grounding tốt hơn nhờ công cụ MCP |

Nhóm kết luận: Day 09 đánh đổi một chút về độ trễ để lấy sự minh bạch, khả năng kiểm soát rủi ro và độ chính xác ở các kịch bản đòi hỏi truy xuất dữ liệu động.

## 5. Phân công và vai trò trong nhóm

Sự phối hợp giữa các thành viên diễn ra rất khăng khít, thể hiện qua việc sửa lỗi dây chuyền:
- **Ngô Gia Bảo (Supervisor Owner):** Xây dựng `graph.py` và xử lý Fallback cho Synthesis (Exponential Backoff) khi API Rate Limit.
- **Lê Kim Dung (Worker/MCP Owner):** Xây dựng `retrieval.py`, `policy_tool.py` và `mcp_server.py`. Giúp hệ thống "sống" bằng cách cung cấp dữ liệu từ kho tài liệu và công cụ.
- **Nguyễn Dương Ninh (Trace & Docs Owner):** Xây dựng `eval_trace.py`, rà soát tài liệu và biến toàn bộ kết quả kỹ thuật thành các bản báo cáo/biểu đồ thuyết phục.

## 6. Nếu có thêm thời gian

Nếu có thêm một ngày, nhóm sẽ ưu tiên hai việc:
1. **Làm sạch trace theo từng batch chạy** để tránh trộn nhiều lần đánh giá vào cùng một thư mục `artifacts/traces/`.
2. **Chuẩn hóa hạ tầng MCP**: Chuyển từ Mock Python Module sang một Server HTTP thực thụ để hỗ trợ Parallel Tool Call, giúp giảm độ trễ tổng thể.
