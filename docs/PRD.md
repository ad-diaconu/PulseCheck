# Pulse Check - Prdocut Requirements Document

## Overview

An uptime monitoring platform offering **per-minute tracking** and **instant alerts** for client websites / APIs.

## User Stories

- Authentication: The user can create an account using an emain and password, or log in via OAuth2 (Google, GitHub, etc)
- Workspaces: The user can create a personal Workspace to group monitors (e.g. "Client X monitoring") and invite other members with specific roles can invite other members with specific roles ( Admin, Viewer).
- Monitor management: The user can add, edit, delete or pause a URL from being monitored.
- Data Cllection: The system will automatically make an HTTP request (ping) to every active URL at a defined interval (e.g., every 1 or 5 minutes), and log the HTTP status code along with the response time.
- Dashboard & pagination: The user can visualize ping history in a paginated table, with the ability to filter by status code (e.g., 500 errors only) andsort by date or latency.

### Out of Scope (Version 1)

* TCP, gRPC, database, or SSH monitoring (HTTP/HTTPS only).
* SMS or phone call alerts (limited to webhooks and emails).
* "Infinite scroll" pagination in the frontend (we will use classic or cursor-based pagination).
