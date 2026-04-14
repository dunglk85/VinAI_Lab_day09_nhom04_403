# Báo Cáo Cá Nhân Nhóm 04 — Vai trò Trace & Docs Owner

**Họ và tên:** Nguyễn Dương Ninh  
**Nhóm:** Nhóm 04  
**Vai trò:** Trace & Docs Owner  
**Ngày nộp:** 2026-04-14

## 1. Tôi phụ trách phần nào?

Trong lab này, tôi tập trung vào phần bàn giao và khả năng quan sát của hệ thống. Cụ thể, tôi phụ trách file `eval_trace.py`, rà soát các trace trong `artifacts/traces/`, đọc `artifacts/eval_report.json` và tổng hợp các kết quả đó vào phần tài liệu và báo cáo. Công việc của tôi không nằm ở logic routing hay xây worker mới, mà ở việc biến toàn bộ quá trình chạy thành bằng chứng có thể kiểm tra được.

Tôi xem vai trò Trace & Docs Owner như lớp “giải thích hệ thống” cho cả nhóm. Khi supervisor route sai hoặc MCP tool bị gọi chưa đúng lúc, trace là nơi đầu tiên tôi kiểm tra. Khi cần viết báo cáo nhóm, tôi dùng chính dữ liệu từ trace để chứng minh hệ thống đã chạy như thế nào thay vì mô tả cảm tính. Nhờ vậy, phần bàn giao bám sát repo thực tế hơn và dễ đối chiếu hơn khi chấm.

## 2. Quyết định kỹ thuật tôi chọn

Quyết định kỹ thuật quan trọng nhất tôi chọn là **đặt trace làm trung tâm của phần báo cáo**, thay vì viết tài liệu theo hướng mô tả chung. Tôi ưu tiên đọc dữ liệu thật trong `artifacts/traces/` và `artifacts/eval_report.json`, rồi dùng chính các trường như `supervisor_route`, `route_reason`, `workers_called`, `mcp_tools_used`, `confidence` và `latency_ms` để rút ra nhận xét.

Tôi chọn cách này vì báo cáo cho hệ thống multi-agent sẽ không đáng tin nếu không có bằng chứng thực thi. Ví dụ, chỉ riêng việc nhìn `final_answer` không đủ để kết luận hệ thống làm tốt; tôi cần biết câu đó đi qua worker nào, có gọi MCP hay không, và có bị đánh dấu `risk_high` hay không. Trong repo hiện tại, `artifacts/eval_report.json` cho thấy có 59 trace, routing phân bố gần như cân bằng giữa `retrieval_worker` và `policy_tool_worker`, đồng thời MCP được dùng ở 49% số trace. Đây là những con số có giá trị giải thích kiến trúc hơn hẳn một mô tả chung chung.

Trade-off của cách làm này là mất thời gian đọc nhiều file JSON và phải chấp nhận việc trace hiện đang bị lặp do nhiều lần chạy. Tuy vậy, tôi vẫn chọn phương án này vì nó trung thực với hệ thống hơn.

## 3. Tôi đã phát hiện và xử lý vấn đề gì?

Vấn đề lớn nhất tôi nhận ra khi đọc repo là **phần báo cáo cũ chưa bám sát vai trò Trace & Docs Owner và chưa phản ánh đúng trạng thái hiện tại của project**. Một số file đang dùng nội dung mẫu, có chỗ ghi vai trò chưa nhất quán, có chỗ đưa số liệu Day 08/Day 09 theo kiểu ước lượng hoặc để `TODO`, trong khi repo lại đã có sẵn trace và eval report có thể dùng làm bằng chứng.

Symptom của vấn đề này là người đọc báo cáo có thể hiểu sai rằng nhóm đã hoàn thiện toàn bộ phần so sánh baseline, hoặc nghĩ rằng người viết phụ trách nhiều vai trò hơn thực tế. Ngoài ra, khi tài liệu không bám trace thật, phần nhận xét routing và MCP rất dễ trở thành mô tả chung.

Cách tôi xử lý là đọc lại `README.md`, `eval_trace.py`, các docs hiện có, file `artifacts/eval_report.json` và một số trace tiêu biểu như `q09`, `q15`. Từ đó tôi viết lại nội dung theo hướng: nêu đúng phần mình phụ trách, trích đúng số liệu đang có, và chỉ ra rõ đâu là kết quả thực tế, đâu là phần vẫn còn dang dở. Cách này giúp báo cáo trung thực hơn với repo hiện hành.

## 4. Tôi tự đánh giá đóng góp của mình

Điểm tôi làm tốt nhất là khả năng nối phần kỹ thuật với phần bàn giao. Tôi không thêm chức năng mới cho pipeline, nhưng tôi giúp hệ thống “nói được” cách nó hoạt động thông qua trace, metrics và nội dung tài liệu. Với một project multi-agent, đây là phần rất quan trọng vì nếu không có lớp giải thích này, cả nhóm sẽ khó debug và khó bảo vệ quyết định kỹ thuật khi chấm.

Điểm tôi làm chưa tốt là phần so sánh Day 08 và Day 09 vẫn phụ thuộc vào baseline chưa điền đủ trong code. Nói cách khác, tôi đã tổ chức được khung phân tích tốt, nhưng đầu vào để so sánh định lượng vẫn chưa hoàn chỉnh 100%. Nếu nhóm cần một bảng so sánh “đóng số” tuyệt đối thì tôi còn cần thêm dữ liệu từ Day 08.

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì?

Nếu có thêm 2 giờ, tôi sẽ ưu tiên **tách trace theo từng đợt chạy đánh giá** thay vì để toàn bộ 59 file chung trong `artifacts/traces/`. Lý do là hiện tại dữ liệu đang bị lặp theo nhiều lần chạy, làm cho các thống kê tổng hợp chưa phản ánh đúng một batch 15 câu chuẩn. Chỉ cần chuẩn hóa lại cấu trúc thư mục trace theo từng run, phần phân tích routing, MCP usage và HITL rate sẽ sạch hơn và đáng tin hơn rất nhiều.
