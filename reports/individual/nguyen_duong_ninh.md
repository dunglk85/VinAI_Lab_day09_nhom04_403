# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Nguyễn Dương Ninh  
**Vai trò trong nhóm:** Trace & Docs Owner  
**Ngày nộp:** 2026-04-14

## 1. Tôi phụ trách phần nào?

Trong bài lab này, tôi phụ trách phần trace, đánh giá và tài liệu bàn giao. File tôi bám sát nhất là `eval_trace.py`, nơi hệ thống chạy hàng loạt câu hỏi test, lưu từng trace vào `artifacts/traces/`, sau đó tổng hợp metrics trong `analyze_traces()` và tạo báo cáo so sánh ở `compare_single_vs_multi()`. Ngoài phần code đánh giá, tôi cũng chịu trách nhiệm rà soát các tài liệu trong thư mục `docs/` và chuyển các quan sát kỹ thuật thành báo cáo nhóm, báo cáo cá nhân.

Công việc của tôi kết nối trực tiếp với phần của các thành viên khác. Supervisor, workers và MCP chỉ thực sự “đo được” khi trace ghi lại đầy đủ `supervisor_route`, `route_reason`, `workers_called`, `mcp_tools_used`, `confidence`, `latency_ms`. Vì vậy, vai trò của tôi là biến phần thực thi thành bằng chứng để cả nhóm có thể debug, so sánh Day 08 với Day 09 và hoàn thiện phần nộp bài.

**Bằng chứng cụ thể:**
- `eval_trace.py`: có `run_test_questions()`, `analyze_traces()`, `compare_single_vs_multi()`.
- `artifacts/eval_report.json`: chứa các metrics tổng hợp của Day 09.
- `artifacts/traces/run_20260414_111857.json`: là một trace multi-hop tiêu biểu tôi dùng để đọc routing và MCP usage.

## 2. Tôi đã ra một quyết định kỹ thuật gì?

Quyết định kỹ thuật quan trọng nhất tôi đưa ra là **đặt trace thật làm nguồn chính cho phần báo cáo**, thay vì viết tài liệu theo mô tả cảm tính. Trong project multi-agent, nếu chỉ nhìn đáp án cuối thì không thể biết lỗi nằm ở supervisor, worker hay synthesis. Vì vậy, khi làm phần Trace & Docs Owner, tôi ưu tiên đọc trace JSON trước rồi mới rút ra kết luận.

Tôi đã cân nhắc hai cách. Cách thứ nhất là mô tả kiến trúc theo README và các file docs có sẵn; cách này nhanh nhưng dễ chung chung. Cách thứ hai là đi từ trace thật trong `artifacts/traces/` và `artifacts/eval_report.json`; cách này chậm hơn nhưng bám sát trạng thái thực tế của repo. Tôi chọn cách thứ hai vì nó giúp báo cáo có bằng chứng cụ thể.

Hiệu quả của quyết định này thể hiện khá rõ trong số liệu hiện có. `artifacts/eval_report.json` ghi nhận:
- `total_traces = 59`
- `retrieval_worker = 30/59`
- `policy_tool_worker = 29/59`
- `avg_confidence = 0.552`
- `avg_latency_ms = 6636`
- `mcp_usage_rate = 29/59 (49%)`
- `hitl_rate = 3/59 (5%)`

Nhờ đọc trace, tôi cũng thấy được các case đặc biệt như `q09` có route reason `unknown error code + risk_high → human review | human approved → retrieval`, tức hệ thống có bước kiểm soát trước khi tiếp tục trả lời.

## 3. Tôi đã sửa một lỗi gì?

Lỗi lớn nhất tôi xử lý trong phần mình phụ trách không phải lỗi runtime của pipeline, mà là **lỗi không nhất quán giữa báo cáo và trạng thái thực tế của repo**. Khi đọc lại project, tôi thấy nhiều phần báo cáo cũ vẫn còn mang tính template, có chỗ ghi vai trò quá rộng, có chỗ mô tả Day 08 vs Day 09 như đã hoàn thiện hoàn toàn, trong khi `compare_single_vs_multi()` vẫn còn các trường `TODO` cho baseline Day 08.

Symptom của lỗi này là nếu nộp nguyên trạng, người chấm có thể hiểu nhầm rằng nhóm đã có đầy đủ số liệu baseline, hoặc rằng cá nhân tôi phụ trách nhiều vai trò hơn thực tế. Đây là lỗi ở tầng tài liệu và trace interpretation, không nằm trong indexing hay worker logic, nhưng vẫn ảnh hưởng trực tiếp tới chất lượng bàn giao.

Cách tôi sửa là đọc lại `README.md`, `eval_trace.py`, `artifacts/eval_report.json` và các trace tiêu biểu, rồi viết lại phần báo cáo theo đúng vai trò `Trace & Docs Owner`. Tôi giữ nguyên những gì repo thật sự có, đồng thời nói rõ phần nào vẫn chưa hoàn thiện, ví dụ baseline Day 08 trong `compare_single_vs_multi()` vẫn chưa điền đủ. Sau khi sửa, nội dung báo cáo bám dữ liệu hơn, ít suy đoán hơn và nhất quán hơn với những gì có trong repo.

## 4. Tôi tự đánh giá đóng góp của mình

Điểm tôi làm tốt nhất là tôi giúp phần kỹ thuật của nhóm trở nên “đọc được” và “chứng minh được”. Với bài toán multi-agent, đây là phần rất quan trọng vì hệ thống càng nhiều bước thì càng cần trace và tài liệu rõ để debug. Tôi làm tốt ở chỗ kết nối dữ liệu chạy thật với phần giải thích và phần báo cáo.

Điểm tôi còn yếu là phần so sánh Day 08 và Day 09 chưa thể đóng hoàn toàn bằng số liệu thật vì repo hiện chưa cung cấp đầy đủ baseline Day 08. Điều đó có nghĩa là tôi đã tổ chức tốt lớp quan sát và báo cáo, nhưng vẫn còn phụ thuộc vào dữ liệu đầu vào từ pipeline cũ để hoàn thiện phần so sánh định lượng.

Nhóm phụ thuộc vào tôi ở phần tổng hợp trace, metrics và bàn giao tài liệu. Nếu tôi chưa hoàn tất, nhóm vẫn có code chạy được nhưng sẽ khó giải thích hệ thống, khó chứng minh routing đúng và khó nộp báo cáo hoàn chỉnh.

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì?

Nếu có thêm 2 giờ, tôi sẽ làm một việc duy nhất: **chuẩn hóa lại thư mục `artifacts/traces/` theo từng batch chạy**. Lý do là hiện tại thư mục này đang chứa 59 trace từ nhiều lần test, khiến các thống kê tổng hợp bị lặp mẫu. Nếu tách riêng trace theo từng lần chạy 15 câu chuẩn, phần `analyze_traces()` sẽ phản ánh đúng hơn routing distribution, MCP usage và HITL rate của một lần đánh giá hoàn chỉnh.
