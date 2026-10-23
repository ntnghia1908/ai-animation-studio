# Adapter ChatGPT — PRODUCT / REQUIREMENT AGENT

This adapter binds the provider-neutral `product` role to a connected ChatGPT repository session.

It is an **interactive repository adapter**, not a local CLI or OpenAI API runner.

## Role

- PRODUCT / REQUIREMENT AGENT.
- Interviews HUMAN LEAD.
- Creates and updates the canonical REQ artifact.
- Uses repository/GitHub integration for the Product Layer handoff.
- Never authorizes implementation.

## Installation

Copy this adapter into the project and enable `chatgpt` in `framework.config.json`.

The Product Agent contract remains in `docs/product/PRODUCT_AGENT.md`; this adapter only describes how the connected tool occupies that role.

## Boundary

ChatGPT as an adapter does not become part of Framework Core. Provider-specific invocation and account capabilities remain here.
