# Deploy from GitHub

## Hosting requirement
Use a host that runs Node.js/Express plus a reachable MySQL database. Railway is one option; a connection was offered but has not been confirmed. No paid plan or service has been selected. Review provider pricing/quotas before provisioning resources.

GitHub Pages cannot host this backend. Publishing a static page alone would not make Android login/registration work.

## Railway deployment
1. Connect the GitHub account to your hosting account and select the CampusOS repository.
2. Add a MySQL database. Keep its credentials in the hosting provider's secret/environment settings.
3. Create the API service from this repository with **Root Directory = backend**. The service can use `backend/Dockerfile`, or `npm ci` as the build command and `node src/server.js` as the start command.
4. Configure DB_HOST, DB_PORT, DB_USER, DB_PASSWORD and DB_NAME from the database service. Set a random JWT_SECRET (32+ characters), NODE_ENV=production and TRUST_PROXY=1 for a single trusted provider reverse proxy. Let the provider supply PORT.
5. Run `npm run db:setup` once against the new database. Provision the admin with `npm run admin:create`, setting ADMIN_NAME / ADMIN_EMAIL / ADMIN_PASSWORD only for that command; remove the password afterward. Do not expose admin provisioning as a public API.
6. Generate the public HTTPS service domain. Verify `/health` returns `{ "status": "ok", "service": "CampusOS" }`.
7. Test student signup/login, admin-created club/event, membership approval, registration, cancellation and logout over HTTPS.
8. Put that HTTPS URL into the Android **Server connection** setting, or build with `-PAPI_BASE_URL=https://your-host/`.

## Android artifacts
The Android source archive is extracted by the GitHub workflow into `android/`. The workflow builds a debug APK and uploads it as an Actions artifact if compilation succeeds. Debug signing is for demonstrations. A store/release APK needs your own protected signing key; never commit it.

## Completion checklist
- API deployed and health endpoint verified.
- Database schema installed and backups configured.
- Admin provisioned without shipping a default password.
- Android endpoint points to the deployed service.
- Actual emulator/phone smoke test completed.
- No private credentials or local SDK paths committed.

Until these checks are complete, deployment is pending rather than live.
