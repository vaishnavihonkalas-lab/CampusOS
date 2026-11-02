# Verification status — 2 November 2026

Passed locally:
- 3 backend core tests: input/date/password validation, transaction cleanup, anonymous API rejection and required JWT configuration.
- 15 database integration scenarios (16 test-runner entries including their parent), on MariaDB 10.11.14 through mysql2 and real HTTP requests.
- Integration covers signup, role escalation rejection, duplicates, password login, admin ownership, memberships, event creation/editing, simultaneous registration capacity, cancellation, announcements, attendance, event finalisation, profile/password updates, token revocation, forged/expired JWT rejection and scoped admin statistics.
- JavaScript syntax checks.
- npm production dependency audit reported zero known vulnerabilities at the time checked.

Pending / not claimed as verified:
- Android Gradle build and APK generation: local build dependency download is being investigated. The CI workflow provides a repeatable build command; it has not yet produced a verified artifact.
- Android emulator/physical-device test.
- Browser interaction/visual smoke test: browser installation failed in this environment; no visual validation claim.
- MySQL 8.4 CI result and Docker Compose execution.
- Live Node/MySQL hosting and HTTPS Android connectivity. Hosting connection not confirmed.

A passing API suite does not establish that the Android UI or production deployment has passed its own checks.
