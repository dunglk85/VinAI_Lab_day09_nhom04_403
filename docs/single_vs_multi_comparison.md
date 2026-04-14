# Single Agent vs Multi-Agent Comparison — Lab Day 09

**Nhóm:** AI in Action - Lab 09  
**Ngày:** 2026-04-14

---

## 1. Metrics Comparison

| Metric | Day 08 (Single Agent) | Day 09 (Multi-Agent) | Delta | Ghi chú |
|--------|----------------------|---------------------|-------|---------|
| Avg confidence | 0.72 | 0.55 | -17% | Multi-agent khắt khe hơn (grounded) |
| Avg latency (ms) | 4200 | 6636 | +58% | Multi-agent tốn thêm bước routing/mcp |
| Abstain rate (%) | 5% | 15% | +10% | Đã bao gồm HITL triggered cases |
| Multi-hop accuracy | 40% | 75% | +35% | Cải thiện nhờ Policy Worker chuyên biệt |
| Routing visibility | ✗ Không có | ✓ Có route_reason | N/A | |
| Debug time (estimate) | 20 phút | 5 phút | -75% | Trace giúp khoanh vùng worker lỗi ngay |
| LLM calls per query | 1 | 1-2 | +1 | Synthesis + Optional Tool Use |

---

## 2. Phân tích theo loại câu hỏi

### 2.1 Câu hỏi đơn giản (single-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | Cao | Cao |
| Latency | Thấp | Cao hơn |
| Observation | Single agent nhanh hơn. | Multi-agent tốn overhead routing. |

**Kết luận:** Với câu hỏi đơn giản, Single Agent vẫn hiệu quả hơn về mặt performance (latency/cloud cost).

### 2.2 Câu hỏi multi-hop (cross-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | Trung bình | Cao |
| Routing visible? | ✗ | ✓ |
| Observation | Hay bị lẫn lộn giữa các tài liệu. | Worker chuyên biệt giúp phân tách context tốt hơn. |

**Kết luận:** Multi-agent vượt trội vì mỗi worker có trách nhiệm rõ ràng.

### 2.3 Câu hỏi cần abstain

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Abstain rate | Thấp | Cao |
| Hallucination cases | Có thể xảy ra | Rất ít |
| Observation | Thường cố gắng trả lời mò. | Có cơ chế Fallback và HITL để dừng lại. |

**Kết luận:** Multi-agent an toàn hơn cho các hệ thống cần độ chính xác cao.

---

## 3. Debuggability Analysis

### Day 08 — Debug workflow
```
Khi answer sai → phải đọc toàn bộ RAG pipeline code → tìm lỗi ở indexing/retrieval/generation
Không có trace → không biết bắt đầu từ đâu
Thời gian ước tính: 20 phút
```

### Day 09 — Debug workflow
```
Khi answer sai → đọc trace → xem supervisor_route + route_reason
  → Nếu route sai → sửa supervisor routing logic
  → Nếu retrieval sai → test retrieval_worker độc lập
  → Nếu synthesis sai → test synthesis_worker độc lập
Thời gian ước tính: 5 phút
```

---

## 4. Extensibility Analysis

| Scenario | Day 08 | Day 09 |
|---------|--------|--------|
| Thêm 1 tool/API mới | Phải sửa toàn prompt | Thêm MCP tool + route rule |
| Thêm 1 domain mới | Phải retrain/re-prompt | Thêm 1 worker mới |
| Thay đổi retrieval strategy | Sửa trực tiếp trong pipeline | Sửa retrieval_worker độc lập |
| A/B test một phần | Khó | Dễ |

---

## 5. Cost & Latency Trade-off

| Scenario | Day 08 calls | Day 09 calls |
|---------|-------------|-------------|
| Simple query | 1 LLM call | 1-2 LLM calls |
| Complex query | 1 LLM call | 2+ LLM calls (Worker + Synthesis) |
| MCP tool call | N/A | Tích hợp sâu |

---

## 6. Kết luận

**Multi-agent tốt hơn single agent ở điểm nào?**
1. Khả năng gỡ lỗi và quan sát (Observability).
2. Độ chính xác trong các tác vụ chuyên biệt (Policy/Tool use).
3. Khả năng mở rộng (Extensibility).

**Multi-agent kém hơn ở điểm nào?**
1. Độ trễ (Latency) và chi phí API call (Cost).
2. Độ phức tạp trong việc quản lý state và routing.

**Khi nào KHÔNG nên dùng multi-agent?**
Khi hệ thống chỉ có một domain kiến thức nhỏ, yêu cầu phản hồi nhanh và chi phí thấp.

**Nếu tiếp tục phát triển hệ thống này, nhóm sẽ thêm gì?**
Thêm LLM-based Supervisor và hệ thống đánh giá tự động (RAGAS) cho từng worker.
