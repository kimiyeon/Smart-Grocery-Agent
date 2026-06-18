---
name: parse-intent
description: Parse grocery shopping intent from user profile and shopping goals.
---

# Parse Intent Skill

## Purpose
Analyze user grocery-shopping intent.

## Responsibilities
- Parse family composition
- Detect allergies
- Identify shopping purpose
- Parse budget constraints

## Output Schema
```json
{
  "family_size": 0,
  "allergies": [],
  "purpose": "",
  "budget": 0
}
```