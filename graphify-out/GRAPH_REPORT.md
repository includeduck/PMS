# Graph Report - PMS  (2026-09-07)

## Corpus Check
- Corpus is ~7,861 words - fits in a single context window. You may not need a graph.

## Summary
- 145 nodes · 198 edges · 29 communities (6 shown, 15 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- UI Templates and Use Cases
- Orgs and Publications Views
- User and Publication Models
- Accounts Authentication Views
- Project Dependencies and Test Plan
- Department Group Models
- Network Mode Middleware
- Publication Services and Search
- Account Confirmation Services
- Accounts App Configuration
- Django Management Utility
- Orgs App Configuration
- Publications App Configuration
- Accounts Initial Migration
- System Specification Documents
- Role Hierarchy Specifications
- Orgs Initial Migration
- ASGI Server Configuration
- Django Settings Configuration
- WSGI Server Configuration
- Publications Initial Migration

## God Nodes (most connected - your core abstractions)
1. `require_role()` - 19 edges
2. `Base Navigation Bar` - 10 edges
3. `PMS Architecture` - 7 edges
4. `UC-07: Manage Groups` - 7 edges
5. `register()` - 6 edges
6. `UC-06: Manage User Accounts` - 6 edges
7. `UC-02: Authenticate and Control Access` - 5 edges
8. `DepartmentGroup` - 4 edges
9. `UC-01: Register for an Account` - 4 edges
10. `UC-05: Manage Own Publications` - 4 edges

## Surprising Connections (you probably didn't know these)
- `DepartmentGroupAdmin` --references--> `register()`  [EXTRACTED]
  orgs/admin.py → accounts/views.py
- `PublicationAdmin` --references--> `register()`  [EXTRACTED]
  publications/admin.py → accounts/views.py
- `PMS Architecture` --references--> `UC-03: Search for Publications and View Results`  [EXTRACTED]
  ImplementationPlan.md → UseCase.md
- `VUB Network Mode Design` --rationale_for--> `UC-02: Authenticate and Control Access`  [EXTRACTED]
  ImplementationPlan.md → UseCase.md
- `Live Group Membership Deletion Check` --rationale_for--> `UC-07: Manage Groups`  [EXTRACTED]
  ImplementationPlan.md → UseCase.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Accounts Management Workflow** — templates_accounts_user_search, templates_accounts_user_create, templates_accounts_user_edit, templates_accounts_user_delete [EXTRACTED 1.00]
- **Group Management Workflow** — templates_orgs_group_search, templates_orgs_group_create, templates_orgs_group_edit, templates_orgs_group_delete [EXTRACTED 1.00]
- **Publications Discovery and Management** — templates_publications_search, templates_publications_upload, templates_publications_mine, templates_publications_edit, templates_publications_download [EXTRACTED 1.00]

## Communities (29 total, 15 thin omitted)

### Community 0 - "UI Templates and Use Cases"
Cohesion: 0.15
Nodes (12): PMS Architecture, Live Group Membership Deletion Check, VUB Network Mode Design, Base Navigation Bar, Security and Password Hashing NFR, UC-01: Register for an Account, UC-02: Authenticate and Control Access, UC-03: Search for Publications and View Results (+4 more)

### Community 1 - "Orgs and Publications Views"
Cohesion: 0.18
Nodes (15): Role hierarchy checks (SRS §2.3). Currently a no-op; real checks come later., Placeholder decorator. Allows every request until authorization is implemented., require_role(), group_create(), group_delete(), group_edit(), group_search(), require_http_methods (+7 more)

### Community 2 - "User and Publication Models"
Cohesion: 0.17
Nodes (9): AbstractUser, ConfirmationTokenAdmin, UserAdmin, ConfirmationToken, Role, User, register(), PublicationAdmin (+1 more)

### Community 3 - "Accounts Authentication Views"
Cohesion: 0.20
Nodes (11): confirm(), network_mode(), require_http_methods, StubLoginView, StubLogoutView, user_create(), user_delete(), user_edit() (+3 more)

### Community 4 - "Project Dependencies and Test Plan"
Cohesion: 0.38
Nodes (6): Phased Implementation Plan, Test Strategy (pytest-django), Django Dependency, pytest Dependency, pytest-django Dependency, python-dotenv Dependency

### Community 5 - "Department Group Models"
Cohesion: 0.40
Nodes (3): DepartmentGroupAdmin, DepartmentGroup, PMS group/department (UC-07). Distinct from django.contrib.auth.Group.

## Knowledge Gaps
- **10 isolated node(s):** `Migration`, `Role`, `Migration`, `Migration`, `Implementation Plan` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 57 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `register()` connect `User and Publication Models` to `Accounts Authentication Views`, `Department Group Models`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `require_role()` connect `Orgs and Publications Views` to `Accounts Authentication Views`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `DepartmentGroupAdmin` connect `Department Group Models` to `User and Publication Models`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **What connects `Migration`, `Role`, `Migration` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._