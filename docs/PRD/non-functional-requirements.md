# Non-Functional Requirements

## Performance

**Dashboard Load Times:**
- NFR1.1: Annual dashboard SHALL load in <2 seconds on 4G connection
- NFR1.2: Monthly dashboard SHALL load in <1.5 seconds
- NFR1.3: Dashboard interactions SHALL respond in <100ms
- NFR1.4: Charts SHALL render smoothly at 60fps

**Data Processing:**
- NFR1.5: CSV upload SHALL process 100K transactions in <30 seconds
- NFR1.6: Multi-temporal aggregation SHALL complete within 5 minutes for 1M transactions
- NFR1.7: Cross-tenant benchmarks SHALL calculate in <10 seconds nightly
- NFR1.8: API responses SHALL return in <500ms for p95

**Scalability:**
- NFR1.9: System SHALL support 1000+ concurrent users
- NFR1.10: Platform SHALL handle 10K companies without performance degradation
- NFR1.11: Database SHALL scale to 100M+ transactions per company

**Performance Scalability Monitoring:**
- NFR1.13: System SHALL monitor query performance for PostgreSQL RLS policies from Day 1
- NFR1.14: System SHALL establish performance baseline at 100 companies / 10M transactions
- NFR1.15: System SHALL trigger architectural review if:
  - Dashboard load times exceed 3 seconds (p95)
  - Database query times exceed 1 second (p95)
  - Concurrent user capacity drops below 500
  - Aggregation job duration exceeds 1 hour
- NFR1.16: System SHALL implement query optimization (materialized views, indexes) before considering RLS alternatives
- NFR1.17: Architecture decision: PostgreSQL RLS sufficient for MVP, revisit at 1000+ tenants

**Load Testing Requirement (BLOCKING FOR LAUNCH):**
- NFR1.18: System SHALL complete load testing before public launch:
  - Simulate 1000 concurrent users
  - Simulate 1000 companies / 100M total transactions
  - Validate dashboard load time <2s (p95)
  - Validate aggregation pipeline completes in <30 minutes
- NFR1.19: Performance budgets SHALL be enforced via automated CI/CD checks
- NFR1.20: Load test SHALL identify bottlenecks and trigger optimization sprint if needed

**Performance Monitoring & Alerting:**
- NFR1.21: System SHALL implement Datadog or NewRelic monitoring from Day 1
- NFR1.22: Alerts SHALL trigger for:
  - Dashboard p95 >3 seconds
  - API p95 >500ms
  - Database CPU >70%
  - Aggregation job duration >1 hour
  - CSV upload failures >5%
- NFR1.23: Monthly performance review SHALL analyze trends and trigger optimization if degrading
- NFR1.24: On-call rotation SHALL respond to performance alerts within 15 minutes

## Security

**Data Protection:**
- NFR2.1: All data in transit SHALL use TLS 1.3
- NFR2.2: Passwords SHALL be hashed with bcrypt (cost factor 12)
- NFR2.3: PostgreSQL RLS SHALL enforce tenant isolation at database level
- NFR2.4: System SHALL prevent SQL injection via parameterized queries
- NFR2.5: File uploads SHALL be scanned for malware

**Authentication & Authorization:**
- NFR2.6: JWT tokens SHALL expire after 24 hours
- NFR2.7: Refresh tokens SHALL be rotated on each use
- NFR2.8: Failed login attempts SHALL be rate-limited (5 attempts per 15 minutes)
- NFR2.9: Password reset tokens SHALL expire after 1 hour
- NFR2.10: Email verification SHALL be required before account activation

**Tenant Isolation:**
- NFR2.11: Cross-tenant data access SHALL be impossible at code and database level
- NFR2.12: Tenant ID SHALL never be accepted from client requests
- NFR2.13: All database queries SHALL automatically filter by authenticated tenant
- NFR2.14: System SHALL log all cross-tenant access attempts

**Compliance:**
- NFR2.15: System SHALL comply with Chilean Data Protection Law 19.628
- NFR2.16: Users SHALL have right to data deletion
- NFR2.17: System SHALL maintain audit logs for 1 year
- NFR2.18: Data exports SHALL be encrypted

**Data Processor Compliance:**
- NFR2.19: System SHALL maintain "data processor" classification under Chilean data protection law
- NFR2.20: System SHALL NOT retain raw uploaded CSV files beyond 15 days
- NFR2.21: System SHALL complete all data processing, transformation, anonymization, and aggregation within 15-day retention window
- NFR2.22: System SHALL document and audit data lineage showing PII removal compliance
- NFR2.23: System SHALL provide users with "Data Processing Timeline" documentation showing file deletion schedule

**Privacy Model Clarification:**
- NFR2.24: System SHALL implement k-anonymity with k=10 (minimum 10 companies per sector)
- NFR2.25: Benchmarks SHALL use simple aggregates: sum, average, median, percentiles
- NFR2.26: No noise injection required (aggregation-based anonymization sufficient for Chilean law)
- NFR2.27: True differential privacy (epsilon/delta parameters) deferred to Year 2+ if needed for advanced AI features
- NFR2.28: Current approach meets Chilean Data Protection Law 19.628 requirements

**Data Sovereignty Readiness:**
- NFR2.29: Architecture SHALL support multi-region deployment without code changes
- NFR2.30: Chilean data localization compliance plan SHALL be documented
- NFR2.31: If Chilean law requires data localization, migration playbook SHALL enable seamless transition
- NFR2.32: System SHALL support datacenter selection per company (Chilean companies → Chilean DC, others → global DC)

## Reliability & Availability

**Uptime:**
- NFR3.1: Platform SHALL maintain 99.5% uptime (22 hours downtime/year)
- NFR3.2: Planned maintenance SHALL occur during low-traffic windows
- NFR3.3: System SHALL notify users 48 hours before maintenance

**Backup & Recovery:**
- NFR3.4: Database SHALL be backed up daily
- NFR3.5: Backups SHALL be retained for 30 days
- NFR3.6: System SHALL support point-in-time recovery within 24 hours
- NFR3.7: Critical data SHALL be replicated across availability zones

**Error Handling:**
- NFR3.8: System SHALL gracefully handle API failures
- NFR3.9: User-facing errors SHALL provide clear guidance
- NFR3.10: System errors SHALL be logged with full context
- NFR3.11: Critical errors SHALL trigger alerts to operations team

**Background Job Processing:**
- NFR3.12: CSV uploads >10K transactions SHALL process asynchronously via Celery
- NFR3.13: Users SHALL see real-time progress updates via WebSocket or polling
- NFR3.14: Failed jobs SHALL retry 3x with exponential backoff
- NFR3.15: System SHALL email user on completion/failure with clear next steps
- NFR3.16: Background jobs SHALL have monitoring dashboards showing queue depth, processing time, failure rate

**Zero-Downtime Migration Capability:**
- NFR3.17: Database replication strategy SHALL enable seamless datacenter migrations
- NFR3.18: Gradual cutover process SHALL maintain <100ms latency increase during migration
- NFR3.19: System SHALL support blue-green deployment for major infrastructure changes
- NFR3.20: Migration playbook SHALL be tested annually with simulated datacenter move

## Usability

**Accessibility:**
- NFR4.1: Interface SHALL be keyboard navigable
- NFR4.2: Color contrast SHALL meet WCAG 2.1 AA standards
- NFR4.3: Screen readers SHALL properly announce all UI elements
- NFR4.4: Touch targets SHALL be minimum 44x44px

**Responsiveness:**
- NFR4.5: Interface SHALL work on desktop (1920x1080 to 1366x768)
- NFR4.6: Interface SHALL work on tablet (768x1024)
- NFR4.7: Interface SHALL work on mobile (375x667 minimum)
- NFR4.8: Layout SHALL reflow intelligently at all breakpoints

**Browser Support:**
- NFR4.9: Platform SHALL support Chrome/Edge (last 2 versions)
- NFR4.10: Platform SHALL support Firefox (last 2 versions)
- NFR4.11: Platform SHALL support Safari (last 2 versions)
- NFR4.12: Unsupported browsers SHALL show upgrade notice

## Maintainability

**Code Quality:**
- NFR5.1: Backend SHALL use type hints (Python)
- NFR5.2: Frontend SHALL use TypeScript strict mode
- NFR5.3: Code coverage SHALL exceed 70%
- NFR5.4: Critical paths SHALL have 90%+ coverage

**Documentation:**
- NFR5.5: API SHALL be documented with OpenAPI 3.0
- NFR5.6: All public functions SHALL have docstrings
- NFR5.7: Architecture decisions SHALL be documented
- NFR5.8: Deployment process SHALL be documented

**Monitoring:**
- NFR5.9: System SHALL log all errors with stack traces
- NFR5.10: Performance metrics SHALL be tracked (Datadog/similar)
- NFR5.11: User analytics SHALL be captured (PostHog/similar)
- NFR5.12: Database query performance SHALL be monitored

**Technical Debt Register:**
- NFR5.13: System SHALL maintain technical debt log documenting known performance limitations
- NFR5.14: RLS scalability SHALL be tracked as "Monitor & Optimize" debt item
- NFR5.15: Each debt item SHALL include:
  - Risk level (low/medium/high)
  - Trigger conditions for addressing
  - Estimated effort to resolve
  - Mitigation strategies
- NFR5.16: Technical debt review SHALL occur quarterly with prioritization decisions

---
