# Performance Considerations

## Dashboard Load Performance (NFR1.1: <2 seconds)

**Strategy:**
1. **Database Aggregates:** Pre-calculated in `aggregates_*` tables
2. **Redis Caching:** Dashboard data cached for 1 hour
3. **Query Optimization:** Indexed columns (company_id, date)
4. **Pagination:** Limit results to current year by default

**Implementation:**
```python
@router.get("/analytics/dashboard")
@cache(expire=3600)  # 1-hour cache
async def get_dashboard(company_id: int, year: int = 2025):
    # Query pre-calculated aggregates (fast)
    monthly_data = await session.execute(
        select(AggregateMonthly)
        .where(AggregateMonthly.company_id == company_id)
        .where(extract('year', AggregateMonthly.date) == year)
        .order_by(AggregateMonthly.date)
    )

    return {"status": "success", "data": monthly_data}
```

## CSV Processing Performance (NFR1.5: 100K in <30 seconds)

**Strategy:**
1. **Batch Inserts:** Use SQLAlchemy bulk_insert_mappings
2. **gabeda_core:** Single-loop execution for efficiency
3. **Celery:** Async processing, doesn't block API
4. **Validation:** Pre-validate before DB operations

**Implementation:**
```python
from sqlalchemy.dialects.postgresql import insert

@celery_app.task
def process_csv_task(file_path, company_id, mapping):
    # Use gabeda_core for parsing
    result = gabeda_core.process_data(file_path, mapping)

    # Batch insert (1000 rows at a time)
    batch_size = 1000
    for i in range(0, len(result.rows), batch_size):
        batch = result.rows[i:i+batch_size]

        stmt = insert(Transaction).values(batch)
        session.execute(stmt)
        session.commit()

    # Trigger aggregation
    trigger_aggregation.delay(company_id)
```

## API Response Time (NFR1.8: <500ms p95)

**Strategy:**
1. **Async Operations:** FastAPI + asyncpg
2. **Connection Pooling:** Reuse database connections
3. **Minimal Business Logic:** Keep endpoints thin
4. **Caching:** Redis for frequently accessed data

**Monitoring:**
```python
from prometheus_client import Histogram

request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.middleware("http")
async def monitor_performance(request, call_next):
    with request_duration.time():
        response = await call_next(request)
    return response
```

## Frontend Performance

**Bundle Size (<1MB initial load):**
- Code splitting by route
- Lazy load components below fold
- Tree-shake unused dependencies

**Time to Interactive (<3 seconds):**
- Skeleton screens while loading
- Prefetch critical data
- Service worker caching (PWA)

**Chart Rendering (60fps):**
- Recharts optimized for performance
- Limit data points (aggregate if >1000)
- Virtualize long lists

---
