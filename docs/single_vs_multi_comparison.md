# Single Agent vs Multi-Agent Comparison — Lab Day 09

**Nhóm:** Nhóm 04
**Ngày:** 2026-04-14

---

## 1. Metrics Comparison

| Metric | Day 08 (Single Agent) | Day 09 (Multi-Agent) | Delta | Ghi chú |
|--------|----------------------|---------------------|-------|---------|
| Avg confidence | 0.82 | 0.54 | -0.28 | Day 09 có tiêu chuẩn confidence khắt khe hơn. |
| Avg latency (ms) | 1200 | 6558 | +5358 | Multi-agent tốn nhiều bước xử lý hơn. |
| Abstain rate (%) | 10% | 5% | -5% | Multi-agent giúp tìm ra câu trả lời tốt hơn cho policy. |
| Multi-hop accuracy | 60% | 85% | +25% | Tăng mạnh nhờ workflow tách biệt. |
| Routing visibility | ✗ Không có | ✓ Có route_reason | N/A | |
| Debug time (estimate) | 45 phút | 10 phút | -35 | Dễ dàng cô lập lỗi nhờ trace. |

---

## 2. Phân tích theo loại câu hỏi

### 2.1 Câu hỏi đơn giản (single-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | Cao | Rất cao |
| Latency | Thấp (1s) | Trung bình (4s) |
| Observation | Nhanh và hiệu quả. | Chậm hơn không cần thiết do qua nhiều node. |

**Kết luận:** Với câu hỏi đơn giản, Single Agent vẫn có lợi thế về tốc độ.

### 2.2 Câu hỏi multi-hop (cross-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | Trung bình | Cao |
| Routing visible? | ✗ | ✓ |
| Observation | Hay bị lẫn lộn context. | Xử lý tuần tự và logic qua supervisor. |

**Kết luận:** Multi-agent vượt trội hoàn toàn về khả năng xử lý logic phức tạp.

### 2.3 Câu hỏi cần abstain

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Abstain rate | 10% | 5% |
| Hallucination cases | Thỉnh thoảng | Rất ít |
| Observation | Dễ hallucinate khi thiếu info. | Supervisor/HITL giúp chặn bớt hallucination. |

**Kết luận:** Multi-agent an toàn hơn nhờ các cơ chế kiểm soát rủi ro (`risk_high`).

---

## 3. Debuggability Analysis

### Day 08 — Debug workflow
```
Khi answer sai → phải đọc toàn bộ RAG pipeline code → tìm lỗi ở indexing/retrieval/generation
Không có trace → không biết bắt đầu từ đâu
Thời gian ước tính: 45 phút
```

### Day 09 — Debug workflow
```
Khi answer sai → đọc trace → xem supervisor_route + route_reason
  → Nếu route sai → sửa supervisor routing logic
  → Nếu retrieval sai → test retrieval_worker độc lập
  → Nếu synthesis sai → test synthesis_worker độc lập
Thời gian ước tính: 10 phút
```

**Câu cụ thể nhóm đã debug:** 
Cụ thể là câu q09 về mã lỗi `ERR-403-AUTH`. Ban đầu hệ thống không trả lời được, nhưng nhờ trace thấy `human_review` được trigger, nhóm đã biết Supervisor đã nhận diện đúng rủi ro và cần bổ sung context thông qua manual approval/retrieval.

---

## 4. Extensibility Analysis

| Scenario | Day 08 | Day 09 |
|---------|--------|--------|
| Thêm 1 tool/API mới | Phải sửa toàn prompt | Thêm MCP tool + route rule |
| Thêm 1 domain mới | Phải retrain/re-prompt | Thêm 1 worker mới |
| Thay đổi retrieval strategy | Sửa trực tiếp trong pipeline | Sửa retrieval_worker độc lập |
| A/B test một phần | Khó — phải clone toàn pipeline | Dễ — swap worker |

**Nhận xét:** Day 09 (Multi-agent) mang tính module hóa cao, cực kỳ thuận tiện cho việc phát triển team lớn.

---

## 5. Cost & Latency Trade-off

| Scenario | Day 08 calls | Day 09 calls |
|---------|-------------|-------------|
| Simple query | 1 LLM call | 2 LLM calls (Supervisor + Synthesis) |
| Complex query | 1 LLM call | 3-4 LLM calls (Supervisor + Worker + Synthesis) |
| MCP tool call | N/A | 1 call |

**Nhận xét về cost-benefit:** 
Đánh đổi latency và cost để lấy sự chính xác và khả năng bảo trì. Với các hệ thống Enterprise, sự chính xác quan trọng hơn latency vài giây.

---

## 6. Kết luận

**Multi-agent tốt hơn single agent ở điểm nào?**
1. **Độ ổn định:** Phân rã bài toán lớn thành các phần nhỏ giúp LLM tập trung hơn.
2. **Khả năng quan sát:** Trace JSON giúp hiểu tường tận mọi quyết định của hệ thống.

**Multi-agent kém hơn hoặc không khác biệt ở điểm nào?**
1. **Tốc độ:** Chậm hơn rõ rệt do overhead của việc điều phối (Orchestration).

**Khi nào KHÔNG nên dùng multi-agent?**
Khi bài toán quá đơn giản, yêu cầu real-time phản hồi cực nhanh, hoặc chi phí LLM là rào cản lớn nhất.

**Nếu tiếp tục phát triển hệ thống này, nhóm sẽ thêm gì?**
Thêm **Memory Worker** để duy trì ngữ cảnh dài hạn và **Evaluation Worker** tự chấm điểm chính mình trước khi trả kết quả cho user.
