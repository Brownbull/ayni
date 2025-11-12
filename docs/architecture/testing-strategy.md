# Testing Strategy

## Testing Philosophy

**Key Principles (From Gabe's Concerns):**
- **At most 1 mocking test** per function/component
- **At least 1 integration test** using real components/data
- **Prioritize real-world testing** over mocked tests
- **Critical paths MUST be tested** with Playwright + Chrome DevTools
- **Verify actual page renders**, not blank screens

## Backend Testing

**Unit Tests (pytest):**
```python
# At most 1 mock test
def test_csv_processor_with_mock(mocker):
    mock_gabeda = mocker.patch('app.services.csv_processor.process_data')
    mock_gabeda.return_value = MockResult(count=100)

    result = process_csv("fake.csv", mapping_id=1)
    assert result.count == 100

# At least 1 real test
def test_csv_processor_real(test_db, sample_csv_file):
    result = process_csv(sample_csv_file, mapping_id=1)

    # Verify data in real test database
    transactions = test_db.query(Transaction).all()
    assert len(transactions) == 100
```

**Integration Tests (pytest + TestClient):**
```python
def test_upload_csv_endpoint(client, auth_headers, sample_csv):
    response = client.post(
        "/api/v1/data/upload",
        headers=auth_headers,
        files={"file": sample_csv}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "task_id" in data["data"]
```

**RLS Tests:**
```python
def test_tenant_isolation(test_db):
    # Create two companies
    company1 = create_company(name="Company 1")
    company2 = create_company(name="Company 2")

    # Set RLS context to company1
    test_db.execute(
        text("SELECT set_config('app.current_tenant', :id, false)"),
        {"id": company1.id}
    )

    # Should only see company1
    companies = test_db.query(Company).all()
    assert len(companies) == 1
    assert companies[0].id == company1.id
```

**Coverage Target:** 70% overall, 90% for critical paths (auth, RLS, CSV processing)

## Frontend Testing

**Component Tests (Vitest):**
```typescript
// At most 1 mock test
test('Dashboard renders with mock data', () => {
  const mockData = { revenue: 1234567, growth: 12.5 };
  render(<Dashboard data={mockData} />);
  expect(screen.getByText('$1.234.567')).toBeInTheDocument();
});

// At least 1 real test
test('Dashboard fetches and renders real data', async () => {
  render(<Dashboard companyId={1} />);

  // Wait for React Query to fetch
  await waitFor(() => {
    expect(screen.getByText(/revenue/i)).toBeInTheDocument();
  });

  // Verify real data rendered
  expect(screen.getByRole('heading', { name: /Mi Empresa/i })).toBeInTheDocument();
});
```

**E2E Tests (Playwright - MANDATORY for Critical Paths):**
```typescript
// Test critical user flows
test('Complete CSV upload flow', async ({ page }) => {
  // 1. Login
  await page.goto('http://localhost:5173/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // 2. Verify dashboard loads (not blank)
  await expect(page.locator('h1')).toContainText('Dashboard');

  // 3. Navigate to upload
  await page.click('a[href="/upload"]');

  // 4. Upload CSV
  await page.setInputFiles('input[type="file"]', 'test-data.csv');
  await page.click('button:has-text("Upload")');

  // 5. Wait for processing
  await expect(page.locator('.processing-status')).toContainText('Processing');
  await expect(page.locator('.success-message')).toBeVisible({ timeout: 30000 });

  // 6. Verify dashboard updated
  await page.goto('http://localhost:5173/dashboard');
  await expect(page.locator('.revenue-card')).toBeVisible();

  // 7. Check console for errors (Chrome DevTools)
  const logs = await page.evaluate(() => console.log);
  expect(logs).not.toContain('error');
});

// Test blank page issue (from Gabe's concerns)
test('All pages render content, not blank screens', async ({ page }) => {
  const pages = ['/dashboard', '/upload', '/locations', '/settings'];

  for (const path of pages) {
    await page.goto(`http://localhost:5173${path}`);

    // Verify page has content
    const bodyText = await page.textContent('body');
    expect(bodyText.length).toBeGreaterThan(0);

    // Check for React errors
    await expect(page.locator('.error-boundary')).not.toBeVisible();

    // Check console
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    expect(errors).toHaveLength(0);
  }
});
```

**Chrome DevTools Verification:**
- Check console for errors on every page
- Verify network requests return 200/201
- Confirm React components mounted
- No blank screens or error boundaries

## Deployment Testing (Early & Continuous)

**Local Testing First:**
```bash
# Backend
cd backend
pytest tests/ -v --cov=app --cov-report=term

# Frontend
cd frontend
npm run test
npm run test:e2e
```

**Deployment Testing (After Each Feature):**
1. Deploy to Railway (backend) + Render (frontend)
2. Run Playwright tests against deployed URLs
3. Check Railway logs for errors
4. Verify database migrations applied
5. Test from mobile device (real-world scenario)

**CI/CD Pipeline (.github/workflows/):**
```yaml
# backend-tests.yml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

# frontend-tests.yml
name: Frontend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd frontend
          npm ci
          npm run test
          npm run test:e2e
```

---
