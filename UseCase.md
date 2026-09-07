# Use Case Specifications — Publications Management System (PMS)

**Source SRS:** Publications Management System, Software Engineering Group 1, Vrije Universiteit Brussel, Thierry Coppens (Requirements Manager), v0.10, 14‑05‑2008
**Companion document:** `Part1_Requirement_Scope.docx` (SE3002 Assignment 01, Part 1)
**Format:** Extended / Fully‑Dressed Use Case (Cockburn style)
**Status:** Specification only — **no implementation** is included in this document, per assignment scope.
**Target technology stack:** Python + Django (informs the "Technology and Data Variations" notes below only; no code is written here).

Each use case below corresponds to one of the 7 Functional Requirements (R01–R07) selected in Part 1. Actor names, roles and the six‑level user hierarchy (Guest → VUB‑Network User → Member → Publisher → Moderator → Administrator) follow SRS §2.1 and §2.3.

---

## UC‑01: Register for an Account

| Field | Detail |
|---|---|
| **Use Case ID** | UC‑01 |
| **Related Requirement** | R01 (FR) |
| **Goal in Context** | A Guest obtains a usable Member‑level account on the PMS. |
| **Scope** | PMS (web interface) |
| **Level** | User goal |
| **Primary Actor** | Guest |
| **Secondary Actors** | Administrator (receives notification), Mail/Notification subsystem |
| **Stakeholders and Interests** | **Guest:** wants an account quickly and simply. **Administrator:** wants only genuine, uniquely‑identified users admitted. **PMS:** wants no duplicate or invalid accounts in the database. |
| **Preconditions** | The actor has a computer with internet access, or is connected to the VUB network. The actor is not already logged in. |
| **Success Guarantee (Postconditions)** | A new, unconfirmed user record exists with a unique username; a confirmation token has been issued; the Administrator has been notified. Once confirmed, the account is active at Member level. |
| **Trigger** | The Guest selects "Register" from the PMS home/login screen. |

**Main Success Scenario**
1. The Guest selects the *Register* function.
2. The PMS displays a registration form requesting: first name, last name, desired login name, password, email address, university and department.
3. The Guest fills in the form and submits it.
4. The PMS validates that all mandatory fields are present and well‑formed (e.g. email format).
5. The PMS checks that the chosen username does not already exist.
6. The PMS creates a new, unconfirmed account record and generates a confirmation token.
7. The PMS issues the confirmation token to the Guest (design decision: displayed on‑screen / logged via Django's console/`EmailBackend` in development, in place of a real SMTP mail server — see R01 AI‑assumption, Part 1) and notifies the Administrator that a new account is pending.
8. The Guest submits the confirmation token back to the PMS.
9. The PMS activates the account at Member level and confirms success to the actor.

**Extensions (Alternate / Exception Flows)**
- **4a. Missing or malformed field:** The PMS rejects the form, highlights the offending field(s), and redisplays the form with previously entered data retained. Use case resumes at step 3.
- **5a. Username already exists:** The PMS rejects the form with an "username already exists" message and returns to step 2. Use case resumes at step 3.
- **8a. Confirmation token not submitted within the validity window:** The pending account and token expire; the Guest must restart at step 1.
- **8b. Wrong/invalid token submitted:** The PMS rejects the confirmation and allows the Guest to re‑enter the token (bounded retry count, e.g. 5 attempts) or request a new token.

**Special Requirements**
- Passwords must never be stored or transmitted in plain text — Django's default `PBKDF2PasswordHasher` (or a stronger configured hasher) satisfies this without custom code (see NFR N01 — Security).
- The registration form must comply with the W3C XHTML 1.0 Transitional standard (SRS §2.2.2); rendered via a Django template.

**Technology and Data Variations List**
- Step 7 may be satisfied by an on‑screen token (project substitute, Django's console email backend) or by a real email (Django's SMTP backend) in a production deployment.
- User records extend Django's built‑in `AbstractUser`/`User` model; the confirmation token is a separate model or field, not part of core `auth`.

**Frequency of Occurrence** Low–moderate (once per new user).

**Open Issues**
- Maximum token validity period is not specified by the SRS — to be fixed as a team design decision and documented.
- No explicit "resend confirmation" function is described in the SRS; assumed out of scope unless added later.

---

## UC‑02: Authenticate and Control Access (Log In / Log Off)

| Field | Detail |
|---|---|
| **Use Case ID** | UC‑02 |
| **Related Requirement** | R02 (FR) |
| **Goal in Context** | An actor establishes (or ends) an authenticated session at the correct privilege level. |
| **Scope** | PMS (web interface) |
| **Level** | User goal |
| **Primary Actor** | Guest / VUB‑Network User / Member / Publisher / Moderator / Administrator |
| **Secondary Actors** | none |
| **Stakeholders and Interests** | **Actor:** wants fast, reliable access to the privileges their role grants. **PMS:** must never grant a privilege level higher than the actor is entitled to. |
| **Preconditions** | For login: the actor holds a confirmed, valid account (except when accessing as a VUB‑Network User, which requires no account). For log off: the actor currently holds an active session. |
| **Success Guarantee (Postconditions)** | On login: an authenticated session exists at the correct role level (Member/Publisher/Moderator/Administrator), or Guest/VUB‑Network‑User privileges are recognised without a session. On logoff: the session is destroyed and the actor is returned to an appropriate unauthenticated screen. |
| **Trigger** | The actor selects "Log in" or "Log off", or arrives at the PMS while connected to the VUB network. |

**Main Success Scenario (Login from the internet)**
1. The actor navigates to the PMS from a general internet connection.
2. The PMS presents a login screen.
3. The actor enters their username and password and submits.
4. The PMS verifies the credentials against the stored (encrypted) password.
5. The PMS creates an authenticated session at the actor's assigned role (Member, Publisher, Moderator or Administrator).
6. The PMS redirects the actor to their default landing screen (e.g. search).

**Main Success Scenario (Login via the VUB network)**
1. The actor's browser reaches the PMS while connected to the VUB network.
2. The PMS recognises the connection as originating from the VUB network (project substitute: an explicit "network mode" selection, in place of true IP‑address detection that would otherwise use Django `HttpRequest.META['REMOTE_ADDR']` against an allow‑listed IP range — see R02 AI‑assumption, Part 1).
3. The PMS grants VUB‑Network‑User privileges without requiring login, while still offering a login option to reach a higher role.

**Main Success Scenario (Log off)**
1. The authenticated actor selects "Log off".
2. The PMS destroys the session.
3. If the actor is connected to the VUB network, the PMS redirects them to the search page (falling back to VUB‑Network‑User privileges); otherwise it redirects to the login page.

**Extensions**
- **4a. Invalid username or password:** The PMS displays a generic authentication‑failure message (not revealing which field was wrong) and returns to step 3 of the internet‑login flow.
- **4b. Account not yet confirmed (see UC‑01):** The PMS blocks login and explains that confirmation is pending.
- **4c. Account locked/expelled by an Administrator:** The PMS blocks login and shows an appropriate message.
- **2a (VUB‑network flow). Network mode cannot be determined:** The PMS defaults the actor to Guest privileges and offers a normal login.

**Special Requirements**
- Credentials must be transmitted and stored encrypted — password storage via Django's built‑in hasher, transit via HTTPS/TLS (NFR N01 — Security).
- Session/role logic must correctly implement the inheritance hierarchy of SRS §2.3 (each higher role inherits all functions of the one below it).

**Technology and Data Variations List**
- VUB‑network recognition may later be replaced with genuine IP‑range detection (Django middleware) without changing this use case's outcome.
- Login/session handling uses Django's built‑in `django.contrib.auth` (session‑based authentication) and role/permission checks via Django `Group`/`Permission` or a custom role field mapped to the six‑level hierarchy.

**Frequency of Occurrence** Very high (every session).

**Open Issues**
- Session timeout duration is not specified by the SRS; to be defined as a design decision.

---

## UC‑03: Search for Publications and View Results

| Field | Detail |
|---|---|
| **Use Case ID** | UC‑03 |
| **Related Requirement** | R03 (FR) |
| **Goal in Context** | An actor locates publications of interest and reviews the result list. |
| **Scope** | PMS (web interface) |
| **Level** | User goal |
| **Primary Actor** | VUB‑Network User, Member, Publisher, Moderator, or Administrator |
| **Secondary Actors** | none |
| **Stakeholders and Interests** | **Actor:** wants relevant results quickly, ordered usefully. **PMS:** must return only publications the actor is authorised to see the metadata of. |
| **Preconditions** | The actor holds at least VUB‑Network‑User privileges (a plain Guest cannot search — SRS §2.3.1). |
| **Success Guarantee (Postconditions)** | A result list (possibly empty) matching the search criteria is displayed, showing title and main author per entry, with ordering and pagination available. |
| **Trigger** | The actor selects "Search" and submits search criteria. |

**Main Success Scenario**
1. The actor selects the Search Publications function.
2. The PMS displays a search form with fields for keyword(s), author(s), and a publication date range.
3. The actor fills in one or more criteria, optionally combining keywords with logical operators (AND, OR, NOT) per SRS §2.3.2, and submits.
4. The PMS validates the query syntax.
5. The PMS executes the search against the publication database.
6. The PMS displays the result list (title + main author per row), with options to order results by title, author, or year, and to page through additional screens.
7. The actor selects "View" on a specific result to proceed to publication details (see related, non‑selected SRS function §3.2.8).

**Extensions**
- **4a. Invalid query syntax:** The PMS reports the syntax error and redisplays the form with the actor's input retained; resumes at step 3.
- **6a. No results match the criteria:** The PMS displays an explicit "no results" message instead of an empty list (SRS §3.2.7 exception).
- **6b. Advanced search requested:** The actor extends the query with additional keyword/reference criteria (SRS §2.3.2 "Advanced Search"); flow rejoins at step 5.

**Special Requirements**
- Result screens must be reachable within a small, structured number of clicks (SRS §2.5 — "least amount of clicks").
- Because R03's AI assumption flags a simplified substring‑match implementation instead of true logical‑operator parsing (Part 1, R03), step 3/4 must be re‑verified against SRS §2.3.2 during testing; this is an explicitly unsupported point to defend at the demo/viva.

**Technology and Data Variations List**
- Search may later be extended to full‑text search of publication contents (e.g. Django's `SearchVector`/PostgreSQL full‑text search); out of current scope.
- Baseline search/filtering uses the Django ORM `QuerySet` API (`filter`, `Q` objects for AND/OR/NOT combinations); pagination uses Django's built‑in `Paginator`.

**Frequency of Occurrence** Very high (primary daily‑use function).

**Open Issues**
- Exact precedence/grouping rules for combined logical operators are not specified by the SRS.

---

## UC‑04: Download Publication(s)

| Field | Detail |
|---|---|
| **Use Case ID** | UC‑04 |
| **Related Requirement** | R04 (FR) |
| **Goal in Context** | An actor obtains an electronic copy of one or more publications from a search result. |
| **Scope** | PMS (web interface + file storage) |
| **Level** | User goal |
| **Primary Actor** | VUB‑Network User, Member, Publisher, Moderator, or Administrator |
| **Secondary Actors** | File storage subsystem |
| **Stakeholders and Interests** | **Actor:** wants a correct, complete copy of the requested publication(s). **PMS:** must serve only publications the actor is entitled to access (per SRS §2.1 access‑control note). |
| **Preconditions** | The actor has executed a Search (UC‑03) and is viewing a non‑empty result list, or is viewing the detail screen of one publication. |
| **Success Guarantee (Postconditions)** | The requested file(s) have been transferred to the actor unmodified. |
| **Trigger** | The actor clicks "Download" next to a single result, on a publication's detail screen, or "Download All" at the bottom of a result list. |

**Main Success Scenario (Single publication)**
1. The actor selects "Download" for one publication, either from the result list or from its detail screen.
2. The PMS locates the stored file (pdf/ps) for that publication.
3. The PMS streams the file to the actor.

**Main Success Scenario (Multiple publications)**
1. The actor selects "Download All" (or a ticked subset) from a result list.
2. The PMS locates the stored files for all selected publications.
3. The PMS packages the files into a single archive (design decision — SRS does not name a bundling format; see R04, Part 1).
4. The PMS streams the archive to the actor.

**Extensions**
- **2a. Full text is not available for the requested publication (abstract only):** The PMS informs the actor that no downloadable file exists for that entry, and the use case ends without a transfer for that item (see SRS §3.2.14 exception, applied analogously).
- **2b. File storage temporarily unreachable:** The PMS displays an error and logs it for the Administrator (SRS §2.2.2 error‑handling requirement); use case ends in failure.

**Special Requirements**
- Access to file content must respect the same role/permission rules as viewing the publication's metadata.

**Technology and Data Variations List**
- Supported single‑file formats: pdf, ps (per SRS §1.2). Archive format for bulk download: to be fixed as .zip, built with Python's `zipfile` and streamed via Django's `FileResponse`/`HttpResponse`.
- Stored files are managed through Django's `FileField`/`MEDIA_ROOT` (or an equivalent storage backend), referenced by path/ID from the publication model.

**Frequency of Occurrence** High.

**Open Issues**
- Maximum file size for a publication is explicitly listed as TBD in the SRS (§2.2.4); no enforced limit is defined by this use case.

---

## UC‑05: Manage Own Publications (Upload / View / Edit)

| Field | Detail |
|---|---|
| **Use Case ID** | UC‑05 |
| **Related Requirement** | R05 (FR — CRUD‑style, entity: Publication owned by a Publisher) |
| **Goal in Context** | A Publisher adds a new publication to the system and keeps their own publications' metadata correct. |
| **Scope** | PMS (web interface) |
| **Level** | User goal |
| **Primary Actor** | Publisher (also available to Moderator, Administrator, who inherit Publisher functions) |
| **Secondary Actors** | Bibliographic‑extraction subsystem |
| **Stakeholders and Interests** | **Publisher:** wants their own publications listed accurately with minimal manual data entry. **PMS:** wants correct, non‑duplicated bibliographic metadata and correctly scoped edit rights (own publications only). |
| **Preconditions** | The actor is logged in with at least Publisher privileges. For Edit/Access: the actor has previously uploaded at least one publication. |
| **Success Guarantee (Postconditions)** | Upload: a new publication record exists, owned by the actor, with metadata extracted and confirmed. Edit: the stored metadata reflects the actor's changes. Access: the actor has viewed the current list of their own publications. |
| **Trigger** | The actor selects "Upload Publication", "My Publications", or "Edit" on one of their own publications. |

**Main Success Scenario (Upload)**
1. The Publisher selects "Upload Publication".
2. The PMS prompts for a document in a supported format (pdf, ps, following BibTeX or RIS metadata).
3. The Publisher selects the file and confirms.
4. The PMS automatically extracts bibliographic information (author, title, etc.) from the document.
5. The PMS displays the extracted metadata for review, including any author/institute alias suggestions (e.g. "D. Vermeir" = "Dirk Vermeir").
6. The Publisher accepts or corrects the metadata and confirms.
7. The PMS stores the new publication, owned by the Publisher.

**Main Success Scenario (Access own publications)**
1. The Publisher selects "My Publications".
2. The PMS displays the title, authors, publication date, abstract and cited references for every publication the Publisher owns.

**Main Success Scenario (Edit own publication)**
1. From the "My Publications" list or a search result, the Publisher selects "Edit" on a publication they own.
2. The PMS displays an editable metadata form pre‑filled with current values.
3. The Publisher changes one or more fields and confirms.
4. The PMS validates and applies the changes.

**Extensions**
- **3a (Upload). Unsupported file format:** The PMS rejects the file with a format‑error message; resumes at step 2.
- **4a (Upload). Bibliographic data cannot be extracted:** The PMS presents a blank/partial metadata form for fully manual entry; resumes at step 5.
- **1a (Edit). Actor attempts to edit a publication they do not own:** The PMS refuses the action with an authorisation error (per R05 defence in Part 1 — this boundary is deliberately not delegated to Publishers).
- **4a (Edit). Submitted metadata fails validation:** The PMS redisplays the form with errors highlighted; resumes at step 3.

**Special Requirements**
- A Publisher must not be offered a "Delete own publication" control (design decision documented in Part 1, R05); deletion authority begins at Moderator level.
- Bulk upload (multiple publications via a single BibTeX file, SRS §2.3.4) is a variant of the Upload flow, out of individual‑file scope for this use case but sharing steps 4–7.

**Technology and Data Variations List**
- Metadata extraction accuracy depends on document quality; manual correction path is always available.
- Publication forms are implemented as Django `ModelForm`s; file upload handling uses Django's `FileField`/`request.FILES`; ownership is enforced via a `ForeignKey` to the uploading Publisher plus a view‑level permission check.

**Frequency of Occurrence** Moderate (upload: per new publication; edit/access: recurring).

**Open Issues**
- The exact rule for automatically merging author/institute aliases (e.g. "VUB" = "Vrije Universiteit Brussel") is listed as a future/optional function in the SRS (§2.3.7), not a current requirement.

---

## UC‑06: Manage User Accounts

| Field | Detail |
|---|---|
| **Use Case ID** | UC‑06 |
| **Related Requirement** | R06 (FR — CRUD‑style, entity: User account) |
| **Goal in Context** | A Moderator or Administrator finds and maintains other users' accounts; an Administrator additionally creates and deletes accounts. |
| **Scope** | PMS (web interface) |
| **Level** | User goal |
| **Primary Actor** | Moderator (search/edit within own department), Administrator (search/edit/create/delete, any user) |
| **Secondary Actors** | none |
| **Stakeholders and Interests** | **Moderator/Administrator:** wants an efficient way to keep user records and privilege levels correct. **Affected user:** wants their account only changed by someone properly authorised. |
| **Preconditions** | The actor is logged in as Moderator or Administrator. For Edit/Delete/Create: the relevant target account exists (except Create). |
| **Success Guarantee (Postconditions)** | Search: a list of matching users is shown. Edit: the target user's settings (including role level, within the actor's authority) reflect the change. Create: a new user account exists. Delete: the target account no longer exists. |
| **Trigger** | The actor selects "Search Users", "Create User", or "Delete User". |

**Main Success Scenario (Search users)**
1. The actor selects "Search Users".
2. The actor enters search criteria (e.g. name, department, role).
3. The PMS returns a list of matching users.

**Main Success Scenario (Edit user settings, incl. role level)**
1. The actor selects a user from a search result.
2. The PMS displays that user's editable settings, including role/level where the actor is authorised to change it (a Moderator may upgrade/downgrade Member ↔ Publisher within their own department; an Administrator may set any level — merged behaviour per R06 design decision, Part 1).
3. The actor changes settings and confirms.
4. The PMS validates and applies the changes.

**Main Success Scenario (Create user — Administrator only)**
1. The Administrator selects "Create User".
2. The Administrator enters username, password, email and group.
3. The PMS checks the username is unique.
4. The PMS creates the account.

**Main Success Scenario (Delete user — Administrator only)**
1. The Administrator selects "Delete User" and enters a username.
2. The PMS displays the matching user's details for confirmation.
3. The Administrator confirms.
4. The PMS deletes the account.

**Extensions**
- **2a (Edit). Moderator attempts to change a user outside their own department, or to Administrator level:** The PMS refuses with an authorisation error.
- **3a (Create). Username already exists:** The PMS rejects with an error; resumes at step 2.
- **1a (Delete). Username does not exist:** The PMS reports the error; use case ends without effect.

**Special Requirements**
- Role changes must never let an actor grant a privilege level higher than their own (SRS §2.3 inheritance model, §3.6.3 security).

**Technology and Data Variations List**
- User CRUD and role changes are implemented via Django's admin‑style views/forms over `django.contrib.auth`'s `User` model (extended with a role field), with authorisation enforced through Django's `permission_required`/custom decorators rather than the built‑in Django admin site directly.

**Frequency of Occurrence** Low–moderate (administrative task).

**Open Issues**
- The exact department‑boundary rule for Moderators is described only at a summary level in the SRS (§2.3.5) and will need a concrete definition for testing.

---

## UC‑07: Manage Groups

| Field | Detail |
|---|---|
| **Use Case ID** | UC‑07 |
| **Related Requirement** | R07 (FR — CRUD‑style, entity: Group) |
| **Goal in Context** | An Administrator creates, finds, edits, or removes a group used to organise users and permissions. |
| **Scope** | PMS (web interface) |
| **Level** | User goal |
| **Primary Actor** | Administrator |
| **Secondary Actors** | none |
| **Stakeholders and Interests** | **Administrator:** wants groups to accurately reflect departmental structure and permissions. **PMS:** must not allow deletion of a group that still has members, to avoid orphaned user records. |
| **Preconditions** | The actor is logged in as Administrator. For Edit/Delete: the target group exists. For Delete: additionally, the group is empty. |
| **Success Guarantee (Postconditions)** | Create: a new group exists. Search: matching groups are listed. Edit: the group's settings reflect the change. Delete: the group no longer exists. |
| **Trigger** | The Administrator selects "Create Group", "Search Group", "Edit" on a group, or "Delete Group". |

**Main Success Scenario (Create group)**
1. The Administrator selects "Create Group".
2. The Administrator enters group name and initial users.
3. The PMS checks the group name is unique.
4. The PMS creates the group.

**Main Success Scenario (Search group)**
1. The Administrator selects "Search Group".
2. The Administrator enters search criteria.
3. The PMS displays matching groups.

**Main Success Scenario (Edit group settings)**
1. The Administrator selects a group from a search result.
2. The PMS displays the group's editable settings (e.g. permissions, membership).
3. The Administrator changes settings and confirms.
4. The PMS validates and applies the changes.

**Main Success Scenario (Delete group)**
1. The Administrator selects "Delete Group" and enters a group name.
2. The PMS displays the matching group's details, including current member count.
3. The PMS verifies the group has no members.
4. The Administrator confirms.
5. The PMS deletes the group.

**Extensions**
- **3a (Create). Group name already exists:** The PMS rejects with an error; resumes at step 2.
- **1a (Delete). Group name does not exist:** The PMS reports the error; use case ends without effect.
- **3a (Delete). Group is not empty:** The PMS refuses deletion and states that members must be removed or reassigned first (SRS §3.2.29 exception); use case ends without effect.

**Special Requirements**
- The "group must be empty" rule (step 3 of Delete) must be enforced with a live check against current membership at the moment of deletion (per R07 AI assumption, Part 1), not a cached flag.

**Technology and Data Variations List**
- Groups map to a dedicated Django model (distinct from `django.contrib.auth.models.Group`, since PMS groups represent departments with membership counts, not just permission bundles); the "empty group" check (step 3 of Delete) is a live `queryset.count()`/`exists()` check against related users at deletion time.

**Frequency of Occurrence** Low (administrative task, infrequent).

**Open Issues**
- The SRS does not specify what should happen to a group's stored permission settings if it is later recreated with the same name; treated as out of scope.

---

## Traceability Summary

| Use Case | Requirement (Part 1) | Primary Actor(s) | CRUD? |
|---|---|---|---|
| UC‑01 | R01 | Guest | No |
| UC‑02 | R02 | All roles | No |
| UC‑03 | R03 | VUB‑Network User and above | No |
| UC‑04 | R04 | VUB‑Network User and above | No |
| UC‑05 | R05 | Publisher and above | Yes |
| UC‑06 | R06 | Moderator, Administrator | Yes |
| UC‑07 | R07 | Administrator | Yes |

*(NFR N01–N03 from Part 1 are cross‑cutting and are not modelled as separate use cases; they constrain the "Special Requirements" of the use cases above — see the Security note in UC‑01/UC‑02/UC‑06 and the file/error‑handling notes in UC‑04.)*
