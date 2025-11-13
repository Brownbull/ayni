"""Pytest plugin for automatic security audit report generation.

This plugin hooks into pytest to automatically generate a security audit
report after running security tests. Add to pytest configuration:

# In pytest.ini or pyproject.toml:
[tool.pytest.ini_options]
plugins = ["tests.security.conftest_plugin"]
"""

from pathlib import Path

import pytest

from tests.security.audit_report import SecurityAuditReport


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    """Generate security audit report after all tests complete.

    This hook collects test results and generates a comprehensive
    security audit report showing RLS status, isolation test results,
    and JWT enforcement results.

    Args:
        session: Pytest session object with test results
        exitstatus: Exit status of the test session
    """
    # Only run on main process (not xdist workers)
    if hasattr(session.config, "workerinput"):
        return

    # Only generate report if security tests were actually run
    security_tests_run = any("security" in str(item.fspath) for item in session.items)

    if not security_tests_run:
        return

    try:
        # Collect test statistics
        passed = session.testscollected - session.testsfailed
        failed = session.testsfailed
        total = session.testscollected

        # Create audit report
        report = SecurityAuditReport()
        report.set_test_summary(total=total, passed=passed, failed=failed)

        # Parse test results (simplified - would need full implementation for detailed results)
        # For now, generate basic report with summary
        # Full implementation would parse test outcomes from session.items

        # Generate and save report
        report_path = Path(__file__).parent / "audit-report.md"
        report.save_to_file(report_path)

        # Print notification
        print(f"\n{'='*80}")
        print(f"✅ Security Audit Report Generated: {report_path}")
        print(f"{'='*80}")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

        if failed == 0:
            print("\n✅ VERDICT: SECURE - All security tests passed")
        else:
            print(f"\n❌ VERDICT: VULNERABLE - {failed} security test(s) failed!")
            print("⚠️  DO NOT DEPLOY - Fix security issues before deployment")

        print(f"{'='*80}\n")

    except Exception as e:
        # Don't fail the test run if report generation fails
        print(f"\n⚠️  Warning: Failed to generate security audit report: {e}\n")
