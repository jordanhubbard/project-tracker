# Models and generation

[Documentation](../README.md)

Two separate model connections exist:

| Connection | Purpose | Configuration |
| --- | --- | --- |
| Coding provider | Generates an application from the locked specification | Installed LitAI/operator configuration and lifecycle CLI |
| Product assistant gateway | Answers a user's repository/task question while the app runs | Backend Settings and `TRACKER_LLM_*` variables |

The lifecycle wrapper defaults `CODING_CLI` to `claude` and examples select
`claude-fable-5-1`. The frontend executable and requested model are observable; a router's
underlying resolved model should only be reported when separate evidence establishes it.
Selecting a coding provider does not configure the product assistant.

Generation inputs include the Component's specification set, selected Flavors, pinned
conversion skills and exact dependency authority. `lock` and `plan` resolve those inputs.
A matching accepted-source cache can supply source, but current admission and acceptance
are still required. Keep private credentials and operator endpoints out of authored inputs.

The wrapper defaults `LITERATE_AI_CODING_CLI_TIMEOUT_SECONDS` to 3600 unless already set.
Long full-stack runs may use an explicit larger budget. A generation timeout does not
justify editing an accepted cache or bypassing tests. Inspect the failure evidence and
change the narrowest owning specification when product intent needs correction.

Use [development](development.md) for commands and [configuration](configuration.md#assistant-gateway)
for the running product's assistant.
