# Event Hosts, Accounts, Credits, and Event Access

Implementation checklist for evolving Paintober from anonymous/session-based usage into organizer and event-attendee experiences.

## Product Decisions

- Organizer authentication uses Django session authentication with email/password.
- Anonymous usage remains available alongside event-based usage.
- Attendee phone verification is configurable per event and disabled by default.
- Without OTP, the attendee is recovered using the event link and phone number.
- Attendee phone numbers are stored normalized as plaintext, with strict access controls.
- Credits are funded through manual/admin grants in v1. Real checkout is deferred.
- A credit is reserved atomically when a generation is submitted.
- The reservation is finalized when the job succeeds.
- The reservation is released when the job permanently fails.
- Retries keep the same reservation and do not consume additional credits.
- Attendee kit limits are configurable per event.
- Expired or disabled events block new generations but preserve existing results.
- Organizer v1 includes account access, credit balance, event setup, sharing, usage summary, and attendee viewing/blocking.
- Kit names are optional for anonymous, attendee, and organizer-created kits, and organizers may rename kits they own afterward.
- Organizers may create personal kits or event-associated kits from Studio; event-associated organizer kits consume one event credit and have no attendee attached.
- The event kit grid includes all submitted jobs. Completed jobs reuse `quantized_color.png` as the card thumbnail; pending, processing, and failed jobs show status placeholders.
- The event detail page provides a Create kit action, while the general Studio page provides an active-event selector plus a personal/non-event option.

## Phase 1: Domain and Data Model

- [x] Add an application for organizer/event/account domain models, or place the models in an existing app after confirming ownership boundaries.
- [x] Add an organizer account/profile model or establish the supported fields and constraints on Django's user model.
- [x] Add organizer email uniqueness and account status fields where required.
- [x] Add an `Event` model owned by an organizer.
- [x] Add a cryptographically secure, unguessable event token.
- [x] Add event name, event date, status, created/updated timestamps, and optional branding fields.
- [x] Add event credit allocation fields or ledger relationships without relying on a single mutable counter.
- [x] Add event rules including maximum kits per attendee and OTP-required flag.
- [x] Add event lifecycle fields for active, expired, and disabled behavior.
- [x] Add an event-scoped `Attendee` model with normalized phone number, status, timestamps, and usage counters or derived usage relationships.
- [x] Add attendee uniqueness scoped to `(event, normalized_phone_number)`.
- [x] Add optional attendee verification fields for future OTP support.
- [x] Extend `Job` with event and attendee relationships while preserving existing user/session ownership for anonymous jobs.
- [x] Add a job credit reservation relationship or reservation identifier.
- [x] Add a credit ledger model supporting purchase/grant, event allocation, reservation, finalization, release/refund, and manual adjustment entries.
- [x] Add immutable ledger entry types and references to the organizer, event, job, and administrator where applicable.
- [ ] Add database constraints preventing negative available balances and duplicate active reservations where practical.
- [x] Create and apply migrations.
- [x] Add Django admin registration for organizer accounts, events, attendees, jobs, and ledger entries.

## Phase 2: Authentication and Organizer API

- [x] Add organizer registration endpoint using email/password.
- [x] Add organizer login endpoint using Django sessions.
- [x] Add organizer logout endpoint.
- [x] Add current-organizer/session endpoint for frontend hydration.
- [x] Add authentication validation and password handling through Django's auth APIs.
- [x] Add permission classes separating organizer endpoints from public/event-attendee endpoints.
- [x] Add organizer credit-balance endpoint based on ledger state.
- [x] Add admin/manual credit-grant operation with an auditable ledger entry.
- [x] Add organizer event list endpoint.
- [x] Add event creation endpoint that validates allocation against unallocated organizer credits.
- [x] Add event detail endpoint for the owning organizer.
- [x] Add event disable/enable endpoint.
- [x] Add organizer event usage summary including allocated, reserved, consumed, released, and remaining credits.
- [ ] Add organizer attendee activity endpoint with privacy-conscious identifiers and usage information.
- [ ] Add organizer attendee block/unblock endpoint.
- [ ] Add tests for registration, login, logout, permissions, and organizer ownership.

## Phase 3: Event Access and Attendee Identity

- [x] Add public event-resolution endpoint for `/join/<event-token>`.
- [x] Return only event information appropriate for an unauthenticated attendee.
- [x] Define responses for invalid, expired, disabled, and exhausted events.
- [x] Add attendee entry endpoint accepting an event token and phone number.
- [x] Normalize phone numbers consistently before lookup or creation.
- [x] Create or retrieve the attendee within the resolved event.
- [x] Establish a signed, event-scoped attendee session/context after entry.
- [ ] Ensure attendee context cannot be used to access another event or attendee.
- [x] Add configurable OTP fields and service boundaries without requiring OTP by default.
- [ ] Add rate limiting for event resolution, phone lookup, attendee entry, and generation submission.
- [x] Avoid exposing full phone numbers in attendee-facing responses.
- [ ] Add tests for attendee creation, repeat entry, event scoping, invalid tokens, and blocked attendees.
- [ ] Add tests covering the documented no-OTP impersonation risk and the selected mitigations.

## Phase 4: Credit Reservation and Job Lifecycle

- [x] Define the credit state transitions: available -> reserved -> consumed, or reserved -> released.
- [x] Add a transaction/service boundary for reserving one event credit.
- [x] Reserve credits inside an atomic database transaction during job submission.
- [x] Lock the event/credit balance rows during reservation to prevent oversubscription.
- [x] Reject new event jobs when available credits are exhausted, including credits already reserved by processing jobs.
- [x] Apply attendee kit and event rules in the same transaction as reservation.
- [x] Attach the reservation to the newly created job before making it processable.
- [x] Keep the reservation unchanged when a job moves from processing back to pending for retry.
- [x] Finalize the reservation and create the consumption ledger entry only when the job reaches `done`.
- [x] Release the reservation and create a release ledger entry when the job reaches terminal `failed` status.
- [ ] Define behavior for unexpected worker crashes, abandoned processing jobs, and manual job cancellation.
- [x] Make finalization and release idempotent so repeated worker actions cannot double-consume or double-release credits.
- [x] Preserve existing anonymous free-tier behavior without creating event credit reservations for anonymous jobs.
- [ ] Add transaction/concurrency tests for one remaining credit and multiple simultaneous submissions.
- [x] Add lifecycle tests for success, retry, permanent failure, and repeated finalization/release.

## Phase 5: Job Ownership, History, and Downloads

- [x] Add optional kit names to job creation, detail, and history responses.
- [x] Add organizer-only kit rename support for organizer-owned personal and event kits.
- [x] Add an organizer-authorized event kits collection with status, creation date, name, and completed thumbnail URL.

- [x] Fix `JobDetailView` to enforce the existing owner filter.
- [x] Enforce ownership or attendee-context authorization on job downloads.
- [x] Extend job list queries to support organizer-owned jobs and attendee-within-event jobs.
- [x] Keep anonymous session history working for non-event jobs.
- [x] Associate event jobs with both the event and attendee identity.
- [ ] Ensure an organizer can view their event activity without granting organizer access to attendee-only routes.
- [x] Ensure an attendee can view only their own jobs within the current event context.
- [x] Preserve completed results after an event expires or is disabled.
- [ ] Add tests for cross-user, cross-session, cross-event, and cross-attendee access attempts.
- [ ] Add tests for signed download URLs combined with authorization checks.

## Phase 6: Frontend Routing and State

- [x] Add optional kit-name input to the general Studio page.
- [x] Add an authenticated-organizer event selector with active events and a personal-kit option.
- [x] Pass organizer-selected event context with generation requests.

- [x] Add `/join/:eventToken` route.
- [x] Add organizer authentication routes for registration, login, and logout.
- [x] Add organizer event/overview routes with the smallest usable dashboard surface.
- [x] Add an event context store containing event details, token, attendee context, and lifecycle state.
- [x] Add an organizer auth store for current-user hydration and session state.
- [x] Add an organizer credit/event store for balances, events, and usage summaries.
- [x] Add attendee entry state without creating a full account flow.
- [x] Persist only the minimum event/attendee context needed for same-session navigation.
- [x] Add API modules for authentication, events, attendee entry, credits, and organizer summaries.
- [x] Preserve the existing `StudioView`, `UploadPanel`, processing, polling, and results components where possible.
- [ ] Pass event/attendee context with generation requests.
- [x] Make the shared history panel load the correct history source based on anonymous, organizer, or attendee context.

## Phase 7: Attendee Experience

- [x] Build the event landing screen showing event name, date, status, and relevant branding.
- [x] Add phone-number entry for attendees.
- [x] Show clear states for invalid, expired, disabled, and exhausted events.
- [x] Show a blocked-attendee state without exposing internal moderation details.
- [x] Transition a valid attendee into the existing Studio generation flow.
- [ ] Display event-specific remaining/availability messaging without leaking other attendee information.
- [x] Keep processing and results visually consistent with the existing Studio experience.
- [ ] Allow returning attendees to enter the same phone number and view their event history.
- [ ] Preserve completed results when the event can no longer accept new jobs.
- [ ] Add an attendee-facing history view or adapt the existing history panel.
- [ ] Add frontend tests for the event-entry and return-attendee paths.

## Phase 8: Organizer Experience

- [x] Add a Create kit action from the organizer event detail page.
- [x] Display all event kits in a responsive grid below the copy-link section.
- [x] Show kit name, creation date, status, and the `quantized_color.png` thumbnail when complete.
- [x] Add organizer kit rename interaction with ownership enforcement.

- [x] Build registration and login screens.
- [x] Build a minimal organizer home screen showing available credits and events.
- [x] Build event creation with name, date, allocation, attendee limit, and OTP setting.
- [x] Validate allocation against unallocated organizer credits before submission.
- [x] Display the event's secure share link.
- [ ] Add QR-code generation for the event link, preferably as a frontend presentation of the canonical URL.
- [ ] Add copy/download/share actions for the event link and QR code.
- [x] Display event credit totals: allocated, reserved, consumed, released, and remaining.
- [x] Display attendee activity and generation counts.
- [x] Add attendee block/unblock controls.
- [x] Add event disable/enable controls with confirmation.
- [ ] Add organizer loading, empty, expired, and permission-error states.
- [ ] Add frontend tests for event creation, allocation errors, sharing, and usage display.

## Phase 9: Security, Privacy, and Operations

- [x] Use a cryptographically secure event token with sufficient entropy and no sequential identifier exposure.
- [x] Do not use the event database ID as the public event token.
- [x] Add server-side authorization checks to every job, event, attendee, ledger, and download endpoint.
- [x] Add CSRF coverage for session-authenticated state-changing requests.
- [x] Add rate limits to phone lookup and job submission endpoints.
- [x] Add brute-force protections for repeated phone-number attempts on one event.
- [ ] Define logging that avoids writing full attendee phone numbers or sensitive tokens.
- [x] Add privacy-aware organizer responses and audit access to attendee information.
- [ ] Add cleanup/retention rules for uploaded images, generated files, attendee records, and ledger records.
- [x] Confirm production database configuration supports row locking and transactional credit reservation.
- [ ] Add monitoring for reservation leaks, failed releases, oversubscription attempts, and worker crashes.
- [ ] Document the no-OTP security tradeoff and the conditions for enabling OTP.

## Phase 10: Documentation and Release Validation

- [ ] Update the API documentation/OpenAPI schema for all new endpoints.
- [ ] Document organizer setup and manual credit grants.
- [ ] Document event creation and attendee sharing.
- [ ] Document event expiration and disabled-event behavior.
- [ ] Document credit reservation, finalization, release, and retry behavior.
- [ ] Document the retained anonymous flow and its limits.
- [ ] Add an end-to-end test for organizer registration/login -> credit grant -> event creation -> link access.
- [ ] Add an end-to-end test for attendee entry -> upload -> generation -> results.
- [ ] Add an end-to-end test for attendee return -> phone entry -> history/results.
- [ ] Add an end-to-end test for event exhaustion under concurrent submissions.
- [ ] Add an end-to-end test for failed generation and credit release.
- [ ] Add an end-to-end test for expired/disabled event behavior.
- [x] Run backend migrations and the full backend test suite.
- [ ] Run the frontend build and frontend tests.
- [ ] Review the production settings for authentication cookies, CORS, CSRF, database, and storage.
- [ ] Review the implementation against this checklist before launch.

## Suggested Delivery Order

1. [ ] Fix current job ownership and download authorization.
2. [ ] Add organizer authentication and the domain models.
3. [ ] Add the credit ledger and atomic reservation lifecycle.
4. [ ] Add event creation and secure event resolution.
5. [ ] Add attendee entry and event-scoped job ownership.
6. [ ] Integrate event context into the existing Studio flow.
7. [ ] Add organizer sharing, QR, and usage screens.
8. [ ] Add attendee history and organizer attendee activity.
9. [ ] Complete security, concurrency, and end-to-end validation.
