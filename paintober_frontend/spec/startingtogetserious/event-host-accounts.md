I want to introduce accounts, credits, and event-based access to Paintober.

Paintober currently allows a user to upload a photo, configure a palette, and asynchronously generate a paint-by-numbers kit. The backend is Django + Django REST Framework and the frontend is Vue.

I want to evolve the product from anonymous/session-based usage into two distinct experiences:

1. Organizers / paying customers
2. Event attendees

Please first inspect the existing codebase and understand the current models, API patterns, authentication approach, generation/job lifecycle, and frontend routing/state management before proposing implementation details.

Do not immediately start coding. First, identify the existing architecture and ask me any important questions that cannot be safely inferred from the codebase.

## Core product concept

An event organizer should be able to:

- Create a Paintober account.
- Purchase credits.
- Create an event.
- Allocate a number of credits to that event.
- Receive a unique event link.
- Share that link with attendees, including via a QR code.
- Monitor how many credits/generations remain for the event.

Example:

Organizer:
Tsholo

Event:
Tsholo's Sip & Paint

Event date:
31 October 2026

Allocated credits:
20

Event link:

https://paintober.example/join/UNIQUE_EVENT_TOKEN

The token must be sufficiently secure and unguessable. It should not simply be an incrementing ID or short predictable event code.

The organizer should be able to share this link directly or turn it into a QR code.

## Attendee experience

Attendees should NOT need to create a Paintober account.

The intended experience should be extremely lightweight:

1. Attendee scans the event QR code or opens the event link.
2. The event is already identified from the URL.
3. The attendee enters their phone number.
4. Paintober identifies or creates an attendee record within that event.
5. The attendee can access the Paintober generation flow.
6. Their generated jobs/results are associated with that attendee and event.

The same attendee should be able to return later using the same event link and phone number and access their previous work/history.

The phone number is intended to act as a lightweight identity within the context of an event. I do not necessarily want attendees to create passwords or full accounts.

Please evaluate whether phone-number verification/OTP is necessary for the first version, considering the balance between simplicity and preventing one attendee from impersonating another or consuming their allowance.

## Event access

The event link is the primary access mechanism.

For example:

/join/<secure-event-token>

When someone visits this URL:

- The backend/frontend resolves the event from the token.
- The attendee should not have to manually type the event code.
- They should see event-specific branding/information where appropriate.
- They enter their phone number and continue.

Please also consider how expired, disabled, exhausted, or invalid event links should behave.

## Credits

Credits are purchased by organizers.

I want to distinguish between:

1. Credits owned by the organizer.
2. Credits allocated or reserved for a specific event.
3. Credits consumed by attendee generations.

For example:

Organizer purchases:
50 credits

They create:

Event A
Allocated: 20 credits

Event B
Allocated: 15 credits

Remaining unallocated:
15 credits

The system should clearly track where credits come from and where they are used.

Please think carefully about whether this should use a credit/transaction ledger rather than simply maintaining and decrementing a `credits` integer.

The system eventually needs to support concepts such as:

- Credit purchases
- Event allocation
- Event credit usage
- Failed generation/refund
- Manual adjustment
- Potential future refunds or promotional credits

I prefer a design that makes these things auditable.

However, do not over-engineer the initial implementation unnecessarily.

## Credit consumption and generations

One important product question is when a credit should actually be consumed.

A naive model would consume a credit immediately whenever an attendee starts a generation.

However, a generation may fail technically, or the attendee may not like the result.

Please inspect how the existing asynchronous generation pipeline and job lifecycle currently work and propose a sensible credit reservation/consumption strategy.

For example, possible concepts include:

- Reserve a credit when a generation is submitted.
- Consume/finalize it when generation succeeds.
- Automatically release the reservation if the job fails.

Do not assume this is the correct solution; evaluate it against the existing job architecture.

Also consider concurrency. We need to avoid a situation where an event has 1 remaining credit but multiple attendees simultaneously start generations.

## Attendee limits

I want the architecture to support configurable event rules.

For example, an event may eventually specify:

- Total event credits.
- Maximum completed generations per attendee.
- Maximum attempts per attendee.
- Whether an attendee can create multiple kits.

For the initial version, keep this simple, but avoid designing the data model in a way that makes these rules impossible later.

A possible initial configuration could be:

- Each successful/finalized kit consumes one event credit.
- An attendee may have a configurable maximum number of kits.

Please discuss the simplest sensible version based on the current codebase.

## History

Currently, generation history is session/browser based.

I want to improve this:

- Organizer-owned generations should belong to the authenticated organizer.
- Attendee generations should belong to the attendee identity within the event.
- If an attendee returns to the same event link and provides the same phone number, they should be able to see their previous jobs/results.

Please determine how this should fit into the existing job/history implementation rather than creating an entirely parallel system unless necessary.

## Organizer experience

At a minimum, an authenticated organizer should eventually have access to:

- Their available credit balance.
- Their events.
- Event-specific credit allocation and usage.
- The unique event link.
- A QR code for the event link.
- A list or summary of attendee activity/generations.

For the initial implementation, prioritize the flows required to actually run an event.

Do not build an unnecessarily complex admin dashboard.

## Existing frontend flow

The current frontend roughly has:

Landing page
    ↓
Studio
    ↓
Upload image
    ↓
Choose/configure palette
    ↓
Generate asynchronous job
    ↓
Processing
    ↓
Results

There is currently no dedicated account or sign-in flow, and history is session-based.

I want to preserve the simplicity of the attendee flow.

Ideally, an attendee entering through:

/join/<event-token>

should experience something like:

Event link / QR
    ↓
Event identified
    ↓
Enter phone number
    ↓
Welcome to [Event Name]
    ↓
Existing Paintober studio flow
    ↓
Generate kit
    ↓
Processing
    ↓
Results
    ↓
Return later using same event link + phone number

The existing studio/generation UI should be reused where possible rather than creating a separate generation system specifically for events.

The authorization/context around the generation should change, but the actual generation experience should remain as consistent as possible.

## Important constraints

- Django + Django REST Framework backend.
- Vue frontend.
- Existing asynchronous generation/job pipeline should remain intact.
- Avoid unnecessary microservices or infrastructure.
- Do not replace working parts of the existing generation pipeline unless required.
- Prefer extending the current models and API patterns where appropriate.
- Preserve anonymous/simple usage where it still makes sense, unless we explicitly decide otherwise.
- Attendees should not need full user accounts.
- The event URL/token should be secure and unguessable.
- Credit handling must be safe under concurrent requests.
- Failed generation jobs must not permanently consume credits without a clear reason.
- We should have an auditable understanding of credit movements.

## What I want from you first

Before writing code:

1. Inspect the existing codebase.
2. Summarize your understanding of the current relevant architecture.
3. Identify which existing models/services/endpoints should be extended.
4. Identify anything that conflicts with this proposal.
5. Ask me the important architectural/product questions that require my decision.
6. Propose a high-level implementation plan.
7. Only after I approve the plan, begin implementing it.

Do not make assumptions about authentication, payments, job ownership, or the current database structure without first inspecting the existing code.