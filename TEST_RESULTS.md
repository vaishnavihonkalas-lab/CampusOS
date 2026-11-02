# Verification status — 2 November 2026

Passed locally:
- 3 backend core tests: input/date/password validation, transaction cleanup, anonymous API rejection and required JWT configuration.
- 15 database integration scenarios (16 test-runner entries including their parent), on MariaDB 10.11.14 through mysql2 and real HTTP requests.
- Integration covers signup, role escalation rejection, duplicates, password login, admin ownership, memberships, event creation/editing, simultaneous registration capacity, cancellation, announcements, attendance, event finalisation, profile/password updates, token revocation, forged/expired JWT rejection and scoped admin statistics.
- GitHub Actions backend job passed against MySQL 8.4 (run 41419979425).
- A fresh download of the GitHub backend passed all 3 core tests.
- GitHub Actions compiled the debug Android APK and passed Android unit tests; artifact CampusOS-debug-APK was produced in run 41419979425.
- JavaScript syntax checks.
- npm production dependency audit reported zero known vulnerabilities at the time checked.

Pending / not claimed as verified:
- Android emulator/physical-device test.
- Browser interaction/visual smoke test: browser installation failed in this environment; no visual validation claim.
- Docker Compose execution.
- Live Node/MySQL hosting and HTTPS Android connectivity. Hosting connection not confirmed.

A passing API suite does not establish that the Android UI or production deployment has passed its own checks.
