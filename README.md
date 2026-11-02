# CampusOS — College Club Management

Java Android client, Node.js/Express REST API and MySQL database for campus clubs, memberships, events and announcements. A small browser client is served by the same API for easier demonstrations.

## Project layout
- `backend/`: Express API, MySQL schema, administration scripts, browser UI and automated tests.
- `CampusOS-Android.zip`: complete Android Studio source project. Extract into `android/` before opening/building. Source ZIP excludes builds, caches, machine paths and credentials.
- Original root Flask files: previous implementation, retained for reference. They do not power the Android/Node API. Use `backend/` for the new version.
- `ANALYSIS.md`: original ZIP findings and what changed.
- `TEST_RESULTS.md`: verified checks and outstanding verification.
- `DEPLOYMENT.md`: GitHub-based deployment and Android endpoint setup.

## Features
Student signup; password-verified login; JWT authentication with expiry/revocation; server-assigned student/admin roles; club browsing and membership requests; admin membership approval/rejection; event creation/editing/status changes; capacity-safe registration/cancellation; participant lists and attendance; announcements; profile editing and password changes.

Administrators manage their own clubs and events. Students cannot grant themselves an admin role. Admin accounts are provisioned through a server-side command, not public signup. Fees use integer paise and are informational; no payment gateway is implemented.

## Run the backend
Requires Node.js 22+ and MySQL 8.0.16+ or MariaDB 10.11+.
1. Create an empty database named `campusos_v2`. Use a separate database from the old Flask project.
2. In `backend/`, run `npm ci`.
3. Copy `.env.example` to `.env`. Set DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME and a random JWT_SECRET of at least 32 characters.
4. Run `npm run db:setup` to create tables. It does not drop tables; it is not a migration of the old schema.
5. Set ADMIN_NAME, ADMIN_EMAIL and ADMIN_PASSWORD in your local environment; run `npm run admin:create`. Remove ADMIN_PASSWORD afterward. No administrator password is shipped.
6. Run `npm start`. Browser UI: `http://localhost:5000`. Health check: `/health`.
7. Create a student account in the app/browser. Create a club as admin before creating an event.

For Docker, copy `backend/.env.example` to root `.env`, set DB_PASSWORD, MYSQL_ROOT_PASSWORD and JWT_SECRET, then run `docker compose up --build`. Provision admin using the administration script inside the API container with an administrator password supplied through your environment. The Docker recipe has not been run here.

## Android
Extract `CampusOS-Android.zip` into an `android/` folder, or use the expanded `android/` directory in the complete downloadable package. Open that directory in Android Studio. Use JDK 17, Android SDK 35 and the supplied Gradle wrapper.

The default debug URL is `http://10.0.2.2:5000/` for the Android emulator. On a physical phone choose **Server connection** on the login screen and enter the computer's reachable LAN address, or the deployed HTTPS backend URL. Phone and server must share a network for LAN use. The server address must end with `/`.

Debug builds permit local HTTP. Release builds require HTTPS. Tokens are stored using Android Keystore-backed AES-GCM; backup is disabled. Login role comes from the server. Signing keys and production passwords are intentionally not included.

Build: `./gradlew assembleDebug testDebugUnitTest`. For a preconfigured endpoint use `./gradlew assembleDebug -PAPI_BASE_URL=https://your-api-host/`. The Android CI build and unit tests passed in run 41419979425, which produced a debug APK artifact. No emulator/device run has been completed here.

## Tests
In `backend/`: `npm test` runs core validation/auth/transaction checks. `npm run test:integration` requires TEST_DB_USER / TEST_DB_PASSWORD with temporary database CREATE/DROP privileges. It creates and drops only its randomly named test database. Never run tests with production credentials.

Integration has been run against MariaDB 10.11.14. The GitHub workflow passed its MySQL 8.4 backend checks and Android APK/unit-test build. See TEST_RESULTS.md.

## Security and boundaries
- Public signup creates only students. JWTs are HMAC-signed, short-lived and checked against the user's current token version.
- Ownership is checked on the server; changing a client role or a request ID does not grant admin rights.
- Event row locks and a unique registration key protect capacity and duplicates.
- Registration/cancellation closes when an event starts; cancelled/completed events cannot reopen. Attendance is available once a non-cancelled event starts.
- Club archive keeps historical registrations. It requires active events to be completed/cancelled first.
- Login rate limiting is in process memory; use a shared limiter for a multi-instance production deployment.
- No email verification, password recovery, university SSO, payments, push notifications or store publication is included.
- The old Flask commit contained a database password. It is removed from the current working copy, but **rotate that password** because old Git history may still expose it.

## Deployment status
No live service is claimed in this repository. Deployment needs an authenticated hosting account and a MySQL instance. Follow DEPLOYMENT.md; verify `/health`, login and registration before distributing an APK. GitHub stores source and builds artifacts; it does not itself run an Express/MySQL server through GitHub Pages.
