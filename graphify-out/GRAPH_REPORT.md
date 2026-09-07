# Graph Report - PMS  (2026-09-07)

## Corpus Check
- 31 files · ~15,523 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 222 nodes · 296 edges · 29 communities (7 shown, 17 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- User Account & Role Models
- Role Hierarchy & Permissions Logic
- Publication Data Models & Tests
- UI Templates & System Documentation
- Publication Services & Metadata Extraction
- Department Group Models & Admin
- User Management Integration Tests
- Core Architecture & Use Case Specs
- VUB Campus Network Session Middleware
- Session Logout & Authentication Views
- Accounts Django App Configuration
- Django CLI Entrypoint
- Orgs Django App Configuration
- Publications Django App Configuration
- Accounts Initial Database Migrations
- System Requirements & Specifications
- Test Strategy & Implementation Roadmap
- Role Hierarchy Formal Specification
- Orgs Initial Database Migrations
- ASGI Server Configuration
- Django Project Core Settings
- WSGI Server Configuration
- Publications Database Migrations
- Django Auth Logout View

## God Nodes (most connected - your core abstractions)
1. `require_role()` - 19 edges
2. `PMS Base Template and Role-Aware Navbar` - 19 edges
3. `TestUC06UserAccountManagement` - 12 edges
4. `TestUC03SearchPublications` - 10 edges
5. `TestUC01RegistrationAndConfirmation` - 9 edges
6. `TestUC02AuthenticationAndNetworkMode` - 9 edges
7. `TestUC07GroupManagement` - 9 edges
8. `TestUC05ManageOwnPublications` - 9 edges
9. `PMS Architecture` - 7 edges
10. `confirm_account()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `DepartmentGroupAdmin` --references--> `register()`  [EXTRACTED]
  orgs/admin.py → accounts/views.py
- `6-Tier User Role Hierarchy` --references--> `PMS Base Template and Role-Aware Navbar`  [INFERRED]
  README.md → templates/base.html
- `PublicationAdmin` --references--> `register()`  [EXTRACTED]
  publications/admin.py → accounts/views.py
- `PMS Architecture` --references--> `UC-01: Register for an Account`  [EXTRACTED]
  ImplementationPlan.md → UseCase.md
- `PMS Architecture` --references--> `UC-03: Search for Publications and View Results`  [EXTRACTED]
  ImplementationPlan.md → UseCase.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **User Registration and Activation Workflow (UC-01)** — templates_accounts_register_html_form, templates_accounts_confirm_html_view, templates_accounts_login_html_loginform, readme_security_rules [INFERRED 0.95]
- **Publication Lifecycle and Distribution Workflow (UC-03 to UC-05)** — templates_publications_search_html_view, templates_publications_upload_html_form, templates_publications_mine_html_view, templates_publications_edit_html_form, templates_publications_download_html_view, templates_publications_download_all_html_view [INFERRED 0.95]
- **Departmental Hierarchy and Safe Group Management (UC-06, UC-07)** — templates_orgs_group_search_html_view, templates_orgs_group_create_html_form, templates_orgs_group_edit_html_form, templates_orgs_group_delete_html_form, templates_accounts_user_search_html_view, readme_security_rules [INFERRED 0.85]

## Communities (29 total, 17 thin omitted)

### Community 0 - "User Account & Role Models"
Cohesion: 0.08
Nodes (16): AbstractUser, ConfirmationTokenAdmin, UserAdmin, ConfirmationToken, Role, User, confirm_account(), issue_confirmation_token() (+8 more)

### Community 1 - "Role Hierarchy & Permissions Logic"
Cohesion: 0.12
Nodes (21): get_user_role(), has_role(), Role hierarchy checks (SRS §2.3)., Determine the effective role of the actor making the request. - If user is…, Check if the user's effective role satisfies the required roles under…, Decorator requiring the request to have at least the privileges of one of the…, require_role(), confirm() (+13 more)

### Community 2 - "Publication Data Models & Tests"
Cohesion: 0.08
Nodes (6): Publication, django_db, fixture, TestUC03SearchPublications, TestUC04DownloadPublications, TestUC05ManageOwnPublications

### Community 3 - "UI Templates & System Documentation"
Cohesion: 0.14
Nodes (26): PMS CI/CD Pipeline, CI Build & Test Matrix Job, Model-View-Template-Service Architecture, Publications Management System Overview, Security and Business Rules, 6-Tier User Role Hierarchy, PMS Python Dependencies, Account Confirmation Token Template (+18 more)

### Community 4 - "Publication Services & Metadata Extraction"
Cohesion: 0.19
Nodes (14): bundle_publications_zip(), extract_bibliographic_metadata(), Publication search, download, and metadata extraction (UC-03–UC-05)., Search publications matching the specified criteria. criteria keys: - keywords:…, Package an iterable of Publication instances into an in-memory zip archive.…, Extract title, authors, year, and abstract from an uploaded document (pdf, ps,…, search_publications(), download() (+6 more)

### Community 5 - "Department Group Models & Admin"
Cohesion: 0.12
Nodes (6): DepartmentGroupAdmin, DepartmentGroup, PMS group/department (UC-07). Distinct from django.contrib.auth.Group., django_db, fixture, TestUC07GroupManagement

### Community 7 - "Core Architecture & Use Case Specs"
Cohesion: 0.22
Nodes (11): PMS Architecture, Live Group Membership Deletion Check, VUB Network Mode Design, Security and Password Hashing NFR, UC-01: Register for an Account, UC-02: Authenticate and Control Access, UC-03: Search for Publications and View Results, UC-04: Download Publication(s) (+3 more)

## Knowledge Gaps
- **15 isolated node(s):** `Migration`, `Migration`, `Role`, `Migration`, `UC-03: Search for Publications and View Results` (+10 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 110 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TestUC06UserAccountManagement` connect `User Management Integration Tests` to `User Account & Role Models`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **What connects `Migration`, `Migration`, `Role` to the rest of the system?**
  _15 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `User Account & Role Models` be split into smaller, more focused modules?**
  _Cohesion score 0.07563025210084033 - nodes in this community are weakly interconnected._
- **Should `Role Hierarchy & Permissions Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.11576354679802955 - nodes in this community are weakly interconnected._
- **Should `Publication Data Models & Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.0812807881773399 - nodes in this community are weakly interconnected._
- **Should `UI Templates & System Documentation` be split into smaller, more focused modules?**
  _Cohesion score 0.14461538461538462 - nodes in this community are weakly interconnected._
- **Should `Department Group Models & Admin` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._