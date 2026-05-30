# Quotation-Only MVP Boundary

## Status

Accepted

## Context

The dashboard is modeled after an exchange screen, including market lists, charts, orderbook, trades, alerts, and a disabled order form UI. Upbit trading APIs require authentication and introduce account, order, and secret-management concerns that are outside the initial monitoring goal.

## Decision

The MVP uses only public Upbit quotation data. It does not use Upbit API key authentication, user login, real order execution, simulated order execution, persisted portfolios, personalized watchlists, or personalized alert settings.

An order form may appear in the UI only as a disabled or "coming soon" surface. Any feature that uses authenticated Upbit Exchange APIs or user-specific trading state must revisit this boundary before implementation.

## Consequences

The MVP can run without secrets, account management, or trading-risk controls. The product remains a market observation dashboard rather than a trading system. UI elements that resemble trading controls must make their disabled state clear so the application does not imply that order execution is available.
