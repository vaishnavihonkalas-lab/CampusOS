# Original ZIP review and implementation changes

## What was present
The uploaded Android ZIP contained login and dashboard screens, a Retrofit GET for an event list, three fixed club buttons and static profile/notice screens. Login accepted any nonempty credentials. Event registration only displayed a message. Event creation displayed success without a network request. Most admin buttons were Toast placeholders. The backend/database were absent. The API URL was fixed to a private LAN address. Cleartext traffic was enabled globally. Build configuration targeted a different toolchain.

The existing GitHub repository was a separate Flask/MySQL web implementation. It was preserved as previous work; the new Android/Node schema uses a distinct database.

## Added in the new version
- Node/Express API and non-destructive fresh database schema.
- Student signup, bcrypt passwords, JWT login/expiry/revocation and provisioned administrators.
- Server-side role and club ownership checks.
- Clubs, membership requests, approvals/rejections and withdrawal.
- Events, editing, capacity, registration/cancellation and event finalisation.
- Participant lists and attendance linked to real registrations.
- Announcements, profiles and password change.
- Retrofit integration for these actions and server-returned login roles.
- Configurable server address and encrypted Android token persistence.
- HTTPS-only release manifest and local-HTTP debug manifest.
- Browser demonstration client, backend tests, Docker configuration, deployment documentation and CI definitions.

## Verification limits
Backend core and database integration checks passed on MariaDB locally and MySQL 8.4 in GitHub Actions. The debug Android APK compiled and Android unit tests passed in GitHub Actions. Emulator/device behaviour and hosted deployment still require verification; see TEST_RESULTS.md. The code does not claim university SSO, real payments or store distribution.
