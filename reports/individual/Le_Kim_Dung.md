# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Lê Kim Dung
**Vai trò trong nhóm:** Worker Owner / MCP Owner
**Ngày nộp:** 2026-04-14
**Độ dài yêu cầu:** 500–800 từ

---

> **Lưu ý quan trọng:**
> - Viết ở ngôi **"tôi"**, gắn với chi tiết thật của phần bạn làm
> - Phải có **bằng chứng cụ thể**: tên file, đoạn code, kết quả trace, hoặc commit
> - Nội dung phân tích phải khác hoàn toàn với các thành viên trong nhóm

---

## 1. Tôi phụ trách phần nào? (150 từ)

Trong dự án này, tôi chịu trách nhiệm chính về lớp thực thi (Execution Layer) của hệ thống. Công việc của tôi tập trung vào việc hiện thực hóa các Worker chuyên biệt và xây dựng giao diện công thức hóa cho các công cụ thông qua giao thức MCP (Model Context Protocol).

**Module/file tôi chịu trách nhiệm:**
- `workers/retrieval.py`: Xây dựng worker thực hiện Dense Retrieval từ ChromaDB, đảm bảo kết quả trả về đúng format contract (chunks & sources).
- `workers/policy_tool.py`: Phát triển worker xử lý các câu hỏi lắt léo về quy định (policy), kết hợp logic phân tích LLM và gọi công cụ MCP.
- `mcp_server.py`: Thiết kế Mock MCP Server với 4 công cụ: tra cứu Knowledge Base, kiểm tra Ticket Jira, kiểm tra quyền truy cập (Access Permission) và tạo Ticket.
- `contracts/worker_contracts.yaml`: Định nghĩa cấu trúc dữ liệu trao đổi giữa các thành phần để đảm bảo tính nhất quán.

**Cách công việc của tôi kết nối với phần của thành viên khác:**
Tôi nhận yêu cầu đã được phân loại từ Supervisor (do bạn Bảo làm). Nếu supervisor quyết định cần công cụ, tôi sẽ kích hoạt MCP server để lấy thêm dữ liệu "sống" từ hệ thống giả lập. Kết quả từ worker của tôi là đầu vào duy nhất để Synthesis Worker tổng hợp câu trả lời cho User.

**Bằng chứng:** Các file `workers/retrieval.py`, `workers/policy_tool.py` và `mcp_server.py` đều chứa logic xử lý lõi do tôi trực tiếp implement.

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (200 từ)

**Quyết định:** Thiết kế hệ thống công cụ theo mô hình **Centralized Dispatch Layer** trong MCP Server thay vì để các Worker gọi trực tiếp các hàm API.

**Lý do:**
Thay vì để `policy_tool_worker` trực tiếp import và gọi các hàm database hay Jira API, tôi xây dựng hàm `dispatch_tool(tool_name, tool_input)` trong `mcp_server.py`. Quyết định này mô phỏng đúng kiến trúc của giao thức MCP thực tế.
- **Tính đóng gói:** Worker không cần biết công cụ đó được code bằng thư viện nào, nó chỉ cần gửi đúng schema JSON.
- **Khả năng mở rộng:** Khi nhóm muốn nâng cấp từ "Mock data" sang API thật (như kết nối Jira thật hoặc FastAPI), tôi chỉ cần thay đổi nội dung bên trong `TOOL_REGISTRY` mà không phải sửa một dòng code nào trong logic của Worker.
- **Dễ dàng Debug:** Tại `mcp_server.py`, tôi có thể log lại toàn bộ lịch sử gọi tool của Agent tại một điểm duy nhất, giúp các thành viên khác dễ dàng tổng hợp metrics về tỉ lệ sử dụng công cụ.

**Trade-off đã chấp nhận:**
Việc đi qua một lớp Dispatch trung gian làm tăng thêm một chút độ phức tạp về code (phải định nghĩa Tool Schemas rõ ràng), nhưng nó giải quyết triệt để vấn đề "Spaghetti code" khi hệ thống mở rộng lên hàng chục công cụ.

**Bằng chứng từ code:**
```python
# mcp_server.py: Lớp điều phối tập trung
TOOL_REGISTRY = {
    "search_kb": tool_search_kb,
    "get_ticket_info": tool_get_ticket_info,
    "check_access_permission": tool_check_access_permission,
}

def dispatch_tool(tool_name, tool_input):
    # Logic thực thi tập trung giúp dễ quản lý và audit
    tool_fn = TOOL_REGISTRY[tool_name]
    return tool_fn(**tool_input)
```

---

## 3. Tôi đã sửa một lỗi gì? (180 từ)

**Lỗi:** `retrieval_worker` bị crash khi khởi chạy lần đầu tiên do Collection trong ChromaDB chưa tồn tại hoặc bị trống.

**Symptom:**
Khi Supervisor gửi câu hỏi đầu tiên, hệ thống văng lỗi `chromadb.errors.InvalidCollectionException`. Pipeline bị dừng ngay lập tức và không có trace nào được lưu lại, gây khó khăn cho việc đánh giá tự động.

**Root cause:**
Hàm `client.get_collection("rag_lab")` trong `retrieval.py` mặc định sẽ ném lỗi nếu tên collection chưa có trong database. Điều này thường xảy ra khi người cộng tác khác trong nhóm clone repo về nhưng chưa kịp chạy script build index.

**Cách sửa:**
Tôi đã thay đổi logic kết nối trong hàm `_get_collection()`. Thay vì chỉ `get`, tôi sử dụng `get_or_create_collection`. Đồng thời, tôi thêm một bước kiểm tra `collection.count() == 0` để đưa ra cảnh báo thân thiện (Warning) thay vì để chương trình bị crash.

**Bằng chứng trước/sau:**
- **Trước khi sửa:** Trace dừng ở bước Supervisor, báo lỗi hệ thống về database.
- **Sau khi sửa:** Worker trả về danh sách rỗng kèm log: `⚠️ Collection 'rag_lab' chưa có data. Chạy index script trước.` Giúp pipeline vẫn chạy tiếp đến bước Synthesis để báo lỗi lịch sự cho người dùng.

---

## 4. Tôi tự đánh giá đóng góp của mình (120 từ)

**Tôi làm tốt nhất ở điểm nào?**
Tôi đã xây dựng được một hệ thống Worker rất "sạch" và tuân thủ chặt chẽ Contract. Việc tích hợp thành công LLM Analysis vào `policy_tool_worker` giúp nhóm xử lý được các câu hỏi cực khó về ngoại lệ chính sách (Flash Sale, Digital License) mà Single-Agent của Day 08 thường làm sai.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Phần logic xử lý của `retrieval_worker` hiện tại chỉ mới dừng ở Dense Retrieval cơ bản. Nếu có thời gian, tôi muốn áp dụng thêm kỹ thuật Re-ranking để tăng độ chính xác của bằng chứng trước khi đưa vào Synthesis.

**Nhóm phụ thuộc vào tôi ở đâu?**
Toàn bộ "khả năng thực thi" của nhóm nằm ở tôi. Nếu các worker tôi làm không chạy hoặc trả về dữ liệu sai cấu trúc, Supervisor sẽ không có dữ liệu để điều phối và Synthesis sẽ không có thông tin để trả lời.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (70 từ)

Tôi sẽ dành 2 giờ để hiện thực hóa một **Real HTTP MCP Server** bằng thư viện `mcp-sdk-python` thay vì dùng Mock class hiện tại. Trace của câu `q15` cho thấy việc gọi nhiều công cụ đồng lúc (Ticket + Access) có thể được tối ưu bằng Parallel Tool Call nếu chúng ta có một Server MCP thực thụ đứng sau.

---

*Lưu file này với tên: `reports/individual/Le_Kim_Dung.md`*
