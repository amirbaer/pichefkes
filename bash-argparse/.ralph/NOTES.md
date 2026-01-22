# Notes & User Directives

**For Claude: This file contains important context from conversations that doesn't fit in the PRD. Read this every iteration.**

Last Updated: 2026-01-22

---

## User Preferences

### Simplicity is Paramount
- Importing and defining flags MUST be as simple and straightforward as possible
- User explicitly emphasized this: "it's very important that importing it and defining the flags in scripts that want to use the library be as simple and straightforward as possible"
- Prioritize ease of use over feature completeness

### Feature Priority
- Aim for feature parity with Python's argparse if possible
- If full parity isn't achievable, focus on 80/20 core features
- Document any gaps between bash implementation and Python's argparse

### Deliverables
- A bashargparse library
- A sample script demonstrating capabilities
- Documentation of limitations and gaps vs Python argparse

---

## Constraints (Don't Do These)

- Don't make the API complex or verbose
- Don't require lots of boilerplate to define simple flags
- Don't sacrifice usability for edge case features

---

## Technical Decisions

### 2026-01-22: Project Setup
- **Decision:** Set up Ralph iteration system and Claude coordination
- **Reason:** Structured development with fresh context per iteration

---

## Python argparse Core Features (Reference)

Key features to consider for 80/20:
1. **Positional arguments** - `parser.add_argument('filename')`
2. **Optional arguments** - `parser.add_argument('-v', '--verbose')`
3. **Short and long flags** - `-v` / `--verbose`
4. **Default values** - `default=...`
5. **Required flags** - `required=True`
6. **Help text** - `help='...'`
7. **Auto-generated help** - `--help` / `-h`
8. **Type conversion** - `type=int`
9. **Choices** - `choices=['a', 'b', 'c']`
10. **Count actions** - `action='count'` (e.g., `-vvv`)
11. **Store true/false** - `action='store_true'`
12. **nargs** - multiple values for one argument
13. **Subcommands** - `subparsers`
14. **Argument groups** - for organized help output
15. **Mutually exclusive groups**

### Priority for bash implementation
- High: 1-8, 10-11 (core functionality)
- Medium: 9, 12 (useful but less common)
- Low: 13-15 (advanced, can be deferred)

---

## Context for Future Iterations

### Project Goal
bashargparse - A bash implementation of Python's argparse library, focusing on simplicity and the 80/20 of core features.

### Current State
- Initial setup complete
- Ralph system ready
- Ready to design PRD

---

**Remember:** Update this file whenever the user gives important directives that future iterations need to know!
