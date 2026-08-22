# Djoser + JWT Authentication Migration Plan

## Goal

Migrate organizer API authentication from Django session authentication to Djoser with Simple JWT, while retaining Django sessions for anonymous jobs, attendee context, CSRF, and Django admin.

## Decisions

- [x] Use `djoser` as the account/authentication foundation.
- [x] Use `djangorestframework-simplejwt` for bearer access and refresh tokens.
- [x] Use JWT for organizer API authentication.
- [x] Keep Django sessions enabled for anonymous users, attendees, CSRF, and admin.
- [x] Preserve `/api/auth/register/`, `/api/auth/login/`, `/api/auth/logout/`, and `/api/auth/me/` initially through compatibility endpoints.
- [x] Expose standard Djoser endpoints under a separate, non-conflicting prefix for future clients.
- [x] Keep access tokens in memory and refresh tokens in `sessionStorage`.
- [x] Enable refresh-token rotation and blacklist support.
- [x] Do not automatically adopt anonymous jobs into organizer accounts after login.
- [x] Ensure organizer logout never calls Django `logout()` or destroys attendee/session context.

## Phase 1 — Dependency and compatibility checks

- [ ] Confirm Djoser compatibility with Django 6.0.4, DRF 3.17, and Python 3.13.
- [ ] Confirm Simple JWT compatibility with the installed Django and DRF versions.
- [x] Add `djoser` to `paintober_backend/pyproject.toml`.
- [x] Add `djangorestframework-simplejwt` to `paintober_backend/pyproject.toml`.
- [ ] Regenerate and review `poetry.lock`.
- [ ] Verify dependency installation in the project virtual environment.
- [ ] Record exact selected package versions in the implementation PR.

## Phase 2 — Django and DRF configuration

File: `paintober_backend/paintober_backend/settings.py`

- [x] Add `djoser` to `INSTALLED_APPS`.
- [x] Add `rest_framework_simplejwt` to `INSTALLED_APPS` if required by the selected setup.
- [x] Add `rest_framework_simplejwt.token_blacklist` to `INSTALLED_APPS`.
- [x] Keep `django.contrib.sessions` installed.
- [x] Keep `SessionMiddleware` enabled.
- [x] Keep `AuthenticationMiddleware` enabled for admin and Django session behavior.
- [x] Keep `CsrfViewMiddleware` enabled for session-backed requests.
- [x] Change DRF’s default authentication class to `rest_framework_simplejwt.authentication.JWTAuthentication`.
- [ ] Decide whether any legacy API view needs explicit `SessionAuthentication`; do not retain it globally without a deliberate compatibility reason.
- [x] Add `DJOSER` configuration for email-based login and custom serializers.
- [x] Preserve `username=email` compatibility with existing Django user rows.
- [x] Configure password validation and decide whether registration requires `re_password`.
- [x] Add `SIMPLE_JWT` configuration with Bearer headers.
- [x] Configure access-token lifetime.
- [x] Configure refresh-token lifetime.
- [x] Enable refresh-token rotation.
- [x] Enable blacklist-after-rotation.
- [x] Keep signing keys server-side and environment-specific.
- [x] Add environment-backed JWT settings to `.env.example`.
- [ ] Keep CORS credential support because attendee and anonymous flows still use cookies.
- [ ] Keep CSRF settings and the `/api/csrf/` endpoint.

## Phase 3 — Djoser serializers and organizer profile handling

File: `paintober_backend/events/serializers.py`

- [x] Add a Djoser user-create serializer.
- [x] Accept the existing registration fields: email, password, and first name.
- [x] Add `re_password` if password confirmation is enabled.
- [x] Normalize and lowercase email addresses consistently.
- [x] Set `username=email` for newly created users.
- [x] Preserve Django password hashing and validation.
- [x] Create `OrganizerProfile` during registration.
- [x] Preserve the existing duplicate-email behavior.
- [x] Add a Djoser current-user serializer.
- [x] Use the Django user shape for the standard Djoser serializer.
- [x] Preserve the existing organizer response shape for compatibility routes.
- [x] Confirm behavior when an existing user has no `OrganizerProfile`.

## Phase 4 — Compatibility authentication endpoints

Files: `paintober_backend/events/auth_views.py`, `paintober_backend/events/auth_urls.py`

- [x] Remove `django.contrib.auth.login()` from organizer registration and login.
- [x] Remove `django.contrib.auth.logout()` from organizer logout.
- [x] Update registration to return access token, refresh token, and organizer data.
- [x] Update login to issue access and refresh tokens.
- [x] Preserve the current email/password request contract where practical.
- [x] Keep `/api/auth/me/` protected by JWT and return organizer data.
- [x] Implement logout using the submitted refresh token.
- [x] Blacklist the refresh token during logout.
- [x] Make logout idempotent for missing or already-invalid refresh tokens where appropriate.
- [x] Ensure logout does not clear `request.session`.
- [x] Ensure logout does not remove `paintober_attendee_context`.
- [x] Ensure logout does not remove anonymous session-owned jobs.
- [x] Add clear response serializers for token-bearing compatibility responses.

## Phase 5 — Standard Djoser routes

Files: `paintober_backend/paintober_backend/urls.py`, `events/auth_urls.py`

- [x] Add standard Djoser user routes under `/api/djoser-auth/`.
- [x] Add standard Djoser JWT create route.
- [x] Add standard Djoser JWT refresh route.
- [x] Add standard Djoser JWT verify route.
- [x] Add standard Djoser current-user route.
- [x] Avoid route collisions with the existing `/api/auth/` compatibility routes.
- [x] Add blacklist migrations after enabling the blacklist app.

## Phase 6 — Mixed JWT/session authorization

Files: `paintober_backend/jobs/views.py`, `paintober_backend/jobs/throttles.py`, `paintober_backend/events/views.py`

- [x] Verify organizer `IsAuthenticated` views authenticate through JWT.
- [x] Verify organizer `IsAdminUser` behavior remains correct.
- [x] Keep public event resolution unauthenticated.
- [x] Keep attendee entry unauthenticated and session-backed.
- [x] Keep anonymous job creation session-backed.
- [x] Keep anonymous job ownership based on `request.session.session_key`.
- [x] Keep attendee context based on `paintober_attendee_context` in the Django session.
- [x] Keep authenticated organizer job ownership based on `request.user`.
- [x] Verify throttle keys remain user-scoped for JWT organizers and session-scoped for anonymous users.
- [x] Define precedence when a JWT and attendee session coexist.
- [x] Make attendee context authoritative for attendee job access if that remains the intended behavior.
- [x] Ensure an organizer JWT cannot access another organizer’s events or jobs.
- [x] Ensure signed download URLs continue to enforce authorization.
- [x] Confirm no job model migration is required.
- [x] Confirm no worker authentication changes are required.

## Phase 7 — Anonymous job ownership policy

- [x] Document that anonymous jobs remain session-owned after organizer login.
- [x] Confirm organizer history remains user-scoped.
- [x] Confirm anonymous history remains session-scoped.
- [x] Confirm attendee/event jobs are never adopted into an organizer account.
- [x] Add regression tests for the selected ownership policy.

## Phase 8 — Frontend token lifecycle

File: `paintober_frontend/src/api/jobs.js`

- [x] Add an access-token provider or shared token utility.
- [x] Attach `Authorization: Bearer <access-token>` when an access token is available.
- [x] Continue sending `credentials: 'include'` for cookie-backed attendee and anonymous flows.
- [x] Continue sending CSRF headers for unsafe session-backed requests.
- [x] Add refresh-token request handling.
- [x] Retry an expired-token request once after a successful refresh.
- [ ] Prevent multiple concurrent requests from triggering conflicting refresh operations.
- [x] Clear authentication state when refresh fails.
- [x] Avoid blindly replaying consumed multipart upload requests.
- [x] Preserve existing API error details and status handling.

File: `paintober_frontend/src/api/auth.js`

- [x] Update registration handling for token-bearing responses.
- [x] Update login handling for token-bearing responses.
- [x] Add refresh-token API support.
- [x] Add blacklist logout API support.
- [x] Keep `/me/` support.
- [x] Normalize Djoser validation errors for the existing views.

File: `paintober_frontend/src/stores/authStore.js`

- [x] Track organizer state separately from token state.
- [x] Store the refresh token in `sessionStorage`.
- [x] Keep the access token in memory where practical.
- [x] Restore authentication during hydration using refresh plus `/me/`.
- [x] Clear access and refresh tokens after logout.
- [x] Clear tokens after an unrecoverable refresh failure.
- [x] Do not clear attendee `sessionStorage` state during organizer logout.
- [x] Do not call a backend operation that destroys the Django session during organizer logout.

Files: `paintober_frontend/src/main.js`, `src/views/LoginView.vue`, `src/views/RegisterView.vue`

- [x] Preserve CSRF initialization for session-backed flows.
- [x] Add authentication hydration without blocking public pages unnecessarily.
- [x] Add `re_password` to registration if required.
- [x] Handle Djoser field-level errors such as email, password, and re_password.
- [x] Confirm organizer views continue using the shared API wrapper.
- [x] Leave attendee context storage and event entry behavior unchanged.

## Phase 9 — Backend tests

Files: `paintober_backend/events/tests.py` and additional auth tests as needed

- [x] Test registration returns the selected token and organizer response shape.
- [x] Test registration creates exactly one `OrganizerProfile`.
- [x] Test duplicate email rejection is case-insensitive.
- [x] Test valid login returns access and refresh tokens.
- [x] Test invalid login behavior and status code.
- [x] Test `/me/` with a valid bearer token.
- [x] Test `/me/` without credentials.
- [x] Test malformed and expired tokens.
- [x] Test refresh-token rotation.
- [x] Test blacklisted refresh tokens cannot be reused.
- [ ] Test organizer logout does not clear attendee context.
- [ ] Test organizer logout does not remove anonymous session-owned jobs.
- [x] Test organizer event, credit, kit, attendee, and rename endpoints with JWT.
- [x] Test another organizer cannot access protected resources.
- [x] Test admin-only restrictions remain correct.
- [ ] Retain session-based tests for Django admin or deliberately session-authenticated behavior.

## Phase 10 — Anonymous and attendee regression tests

- [x] Test anonymous job creation still creates or uses a Django session.
- [x] Test anonymous job listing remains session-scoped.
- [x] Test anonymous job detail fails for a different session.
- [ ] Test anonymous free-tier limits remain session-scoped.
- [ ] Test anonymous throttling remains session-scoped.
- [x] Test event resolution works without authentication.
- [x] Test attendee entry works without authentication.
- [x] Test attendee context is stored in the Django session.
- [x] Test attendee job polling works with only the session cookie.
- [x] Test attendee access fails with another session.
- [x] Test attendee context survives organizer login.
- [x] Test attendee context survives organizer logout.
- [x] Test explicit JWT-plus-attendee precedence.
- [ ] Test attendee throttling remains independent if that is the selected policy.

## Phase 11 — OpenAPI and documentation

Files: `paintober_backend/Paintober API (1).yaml` and project specification files

- [x] Generate the schema using drf-spectacular.
- [x] Add a bearer JWT security scheme.
- [ ] Remove or clearly mark `sessionid` cookie authentication as legacy for organizer APIs.
- [ ] Document compatibility authentication endpoints.
- [ ] Document standard Djoser endpoints.
- [ ] Update auth request and response schemas.
- [ ] Keep public endpoints unauthenticated in the schema.
- [ ] Document session-backed anonymous and attendee endpoints.
- [x] Update frontend authentication and CSRF documentation.
- [x] Update event-host account implementation documentation.
- [x] Document the separate anonymous and organizer job histories.

## Phase 12 — Environment and deployment verification

- [ ] Add JWT lifetime settings to `paintober_backend/.env.example`.
- [ ] Keep JWT signing secrets server-side only.
- [ ] Retain session cookie settings for cross-origin attendee/anonymous flows.
- [ ] Verify `CORS_ALLOWED_ORIGINS` includes the Netlify origin.
- [ ] Verify CORS allows the `Authorization` header.
- [ ] Verify CORS handles `OPTIONS` preflight requests.
- [ ] Verify HTTPS is used for production token and session traffic.
- [ ] Confirm the Cloud Run worker requires no JWT changes.
- [ ] Confirm Django admin remains session-authenticated.

## Verification checklist

- [ ] Resolve dependencies successfully.
- [ ] Run blacklist migrations.
- [ ] Run `python manage.py check`.
- [ ] Run the complete backend test suite.
- [ ] Generate and inspect the OpenAPI schema.
- [ ] Run `npm run build` in `paintober_frontend`.
- [ ] Verify anonymous upload and history manually.
- [ ] Verify event resolve and attendee entry manually.
- [ ] Verify organizer registration and login manually.
- [ ] Verify page-refresh authentication hydration.
- [ ] Verify access-token refresh after expiry.
- [ ] Verify invalid refresh tokens redirect to login.
- [ ] Verify organizer logout revokes refresh tokens.
- [ ] Verify organizer logout preserves attendee and anonymous session state.
- [ ] Verify organizer requests include the bearer header.
- [ ] Verify cross-origin CORS preflight.
- [ ] Verify multipart upload behavior around token refresh.

## Scope boundaries

- [ ] Do not migrate to a custom Django user model as part of this change.
- [ ] Do not replace attendee or anonymous sessions with JWT.
- [ ] Do not migrate anonymous jobs into organizer ownership in the first implementation.
- [ ] Do not change worker authentication.
- [ ] Do not modify unrelated pipeline, storage, or credit-ledger behavior.
