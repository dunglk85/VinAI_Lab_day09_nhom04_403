# Báo Cáo Nhóm — Lab Day 09: Multi-Agent Orchestration
**Tên nhóm:** Nhóm 04  
**Môn học:** AI in Action  
**Ngày nộp:** 2026-04-14  

## 1. Kiến trúc nhóm đã xây dựng

Nhóm triển khai hệ thống hỏi đáp nội bộ theo kiến trúc **Supervisor - Worker**. `graph.py` đóng vai trò điều phối, nhận câu hỏi và quyết định route sang `retrieval_worker`, `policy_tool_worker`, hoặc nhánh `human_review` khi truy vấn có tín hiệu rủi ro. Sau khi worker chuyên trách xử lý, `synthesis_worker` tổng hợp câu trả lời cuối cùng, kèm nguồn và confidence.

Kiến trúc này phù hợp với bài toán lab vì câu hỏi không đồng nhất: có câu chỉ cần tra cứu tài liệu, có câu phải kiểm tra policy, và có câu cần phối hợp thêm MCP tool. Việc tách vai trò giúp hệ thống dễ quan sát hơn so với pipeline một khối của Day 08. Trong trace hiện có, toàn bộ luồng đều ghi lại `supervisor_route`, `route_reason`, `workers_called`, `mcp_tools_used`, `confidence`, `latency_ms` và lịch sử xử lý trong `history`, nên nhóm có thể lần ngược từng bước khi câu trả lời chưa đúng.

Ba thành phần quan trọng nhất của hệ thống là:
- `workers/retrieval.py`: lấy bằng chứng từ kho tài liệu.
- `workers/policy_tool.py`: xử lý câu hỏi liên quan policy/access và gọi MCP.
- `workers/synthesis.py`: tổng hợp đáp án cuối cùng từ dữ liệu đã được ground.

## 2. Quyết định kỹ thuật quan trọng nhất

Quyết định kỹ thuật quan trọng nhất của nhóm là **ghi trace theo từng lần chạy và chuẩn hóa phân tích trong `eval_trace.py`** thay vì chỉ xem kết quả trả lời cuối cùng. Với cách này, nhóm không phải đoán câu trả lời sai do route sai, do worker sai, hay do synthesis chưa bám đúng context.

Trong `eval_trace.py`, nhóm tách rõ ba việc:
1. `run_test_questions()` để chạy toàn bộ bộ câu hỏi và lưu từng trace riêng.
2. `analyze_traces()` để tính các chỉ số như routing distribution, average confidence, latency, MCP usage rate và HITL rate.
3. `compare_single_vs_multi()` để tạo phần khung so sánh Day 08 và Day 09.

Quyết định này tạo ra lợi ích thực tế rõ ràng. Từ `artifacts/eval_report.json`, repo hiện có 59 trace đã lưu, trong đó:
- `retrieval_worker`: 30/59 trace.
- `policy_tool_worker`: 29/59 trace.
- `avg_confidence`: 0.552.
- `avg_latency_ms`: 6636 ms.
- `mcp_usage_rate`: 29/59 (49%).
- `hitl_rate`: 3/59 (5%).

Nếu không có lớp trace này, nhóm rất khó chứng minh được routing hoạt động ra sao, tài liệu nào được dùng nhiều nhất, hoặc MCP được gọi ở những tình huống nào.

## 3. Kết quả chạy và quan sát từ trace

Dựa trên các trace trong `artifacts/traces/`, nhóm quan sát được một số pattern ổn định:

- Các câu tra cứu ngắn như `q01`, `q04`, `q05`, `q06`, `q08`, `q11`, `q14` chủ yếu đi vào `retrieval_worker` với `route_reason = "default route"`.
- Các câu hỏi có tín hiệu policy như `q02`, `q03`, `q07`, `q10`, `q12`, `q13`, `q15` đi vào `policy_tool_worker` với `route_reason = "task contains policy/access keyword"`.
- Truy vấn rủi ro hơn như `q15` có `route_reason = "task contains policy/access keyword | risk_high flagged"` và worker gọi thêm MCP để lấy dữ liệu ticket/access.
- Trường hợp `q09` chứa mã lỗi `ERR-403-AUTH` thể hiện rõ cơ chế an toàn: trace ghi `unknown error code + risk_high → human review | human approved → retrieval`, tức hệ thống không bỏ qua bước kiểm soát trước khi tiếp tục trả lời.

Một trace tiêu biểu là `q15`, nơi hệ thống phải xử lý đồng thời quy trình P1 và cấp quyền tạm thời cho contractor. Trace này cho thấy:
- route sang `policy_tool_worker`;
- gọi 3 MCP tools: `search_kb`, `get_ticket_info`, `check_access_permission`;
- chuyển sang `synthesis_worker`;
- trả lời với confidence `0.66`;
- dùng hai nguồn chính là `access_control_sop.txt` và `sla_p1_2026.txt`.

Điều này chứng minh kiến trúc multi-agent phát huy tác dụng rõ nhất ở các câu hỏi multi-step hoặc cross-document.

## 4. So sánh Day 08 và Day 09

Từ `artifacts/eval_report.json` và các tài liệu trong `docs/`, nhóm rút ra ba khác biệt lớn giữa Day 08 và Day 09:

**Thứ nhất, khả năng debug tốt hơn rõ rệt.**  
Ở Day 08, khi câu trả lời sai, rất khó biết lỗi nằm ở retrieval hay generation. Sang Day 09, chỉ cần mở trace là có thể biết route nào đã được chọn, worker nào đã chạy, MCP nào đã được gọi và confidence ra sao.

**Thứ hai, độ trễ tăng lên.**  
`avg_latency_ms` hiện tại của Day 09 là khoảng `6636 ms`, cao hơn đáng kể so với baseline single-agent mà nhóm dùng để thảo luận trong docs. Đây là trade-off dễ hiểu vì pipeline đã có thêm supervisor, tool call và logging.

**Thứ ba, hệ thống mở rộng tốt hơn.**  
Thay vì nhồi thêm logic vào một prompt lớn, nhóm có thể thêm worker mới hoặc MCP tool mới mà không phải viết lại toàn bộ luồng.

Tóm lại, Day 09 không tối ưu cho các câu FAQ rất ngắn, nhưng phù hợp hơn nhiều cho các truy vấn cần định tuyến rõ, cần bằng chứng, hoặc cần khả năng audit sau khi chạy.

## 5. Phân công và vai trò trong nhóm

Nhóm phân vai theo đúng cấu trúc lab:
- Supervisor Owner: phụ trách `graph.py`, state và routing.
- Worker Owner: phụ trách các worker và contract.
- MCP Owner: phụ trách `mcp_server.py` và tích hợp tool call.
- Trace & Docs Owner: phụ trách `eval_trace.py`, các tài liệu trong `docs/` và hoàn thiện báo cáo.

Trong đó, phần Trace & Docs Owner có nhiệm vụ kết nối toàn bộ sản phẩm kỹ thuật thành một bộ bàn giao có thể đọc, có thể chấm và có thể debug. Đây là vai trò không trực tiếp tạo answer, nhưng quyết định việc nhóm có chứng minh được hệ thống của mình hoạt động đúng hay không.

## 6. Nếu có thêm thời gian

Nếu có thêm một ngày, nhóm sẽ ưu tiên hai việc:
1. Làm sạch trace theo từng batch chạy để tránh trộn nhiều lần đánh giá vào cùng một thư mục `artifacts/traces/`.
2. Hoàn thiện số liệu baseline Day 08 trong `compare_single_vs_multi()` để phần so sánh không còn các trường `TODO`.

Hai việc này sẽ giúp báo cáo nhất quán hơn và làm cho kết luận kỹ thuật của nhóm thuyết phục hơn khi đối chiếu trực tiếp giữa single-agent và multi-agent.
M Routing** thay vì keyword để xử lý các câu hỏi lắt léo mang tính chất so sánh giữa các chính sách khác nhau.
 Routing** thay vì keyword để xử lý các câu hỏi lắt léo mang tính chất so sánh giữa các chính sách khác nhau.
M Routing** thay vì keyword để xử lý các câu hỏi lắt léo mang tính chất so sánh giữa các chính sách khác nhau.
