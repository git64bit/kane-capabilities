# Deployment Acceptance Protocol

## Status

**MANDATORY FOR KANE PRODUCTION DEPLOYMENTS**

This procedure is the operational counterpart to the Civic capability and trust-boundary design. It exists to prevent a correct architecture from being undermined by an unsafe deployment procedure.

The first Kane publication deployment is the reference deployment. Later service deployments must follow the same discipline unless a stricter service-specific procedure is documented.

## Core rule: one host per execution step

Every executable production step is scoped to exactly one physical host.

A command response or runbook step must not contain executable command blocks for two different production hosts. A transition to another host occurs only after:

1. the current host identity has been proved;
2. the requested read or write has completed;
3. its output has been reviewed;
4. the current host has no unexplained state relevant to the next action.

Container commands such as `pct exec <id>` are permitted only when the physical Proxmox host running that CT has already been asserted.

## Host and container identity gate

Before a production write, the command itself must fail closed if it is run on the wrong physical host.

For Proxmox/LXC work the acceptance record must identify:

- physical hostname;
- CT ID;
- CT hostname;
- CT address;
- service name;
- intended role.

Do not rely on shell prompt appearance alone.

## Read-only discovery before writes

Read-only discovery commands must be safe to run interactively on a production root shell.

Rules for discovery blocks:

- keep them short enough that their output and failure point are obvious;
- do not use `set -e` or `set -o pipefail` across a multi-probe audit block;
- an optional probe that may legitimately return nonzero must be isolated and explicitly tolerated;
- a failed discovery probe must not terminate the operator shell;
- prefer one subsystem at a time rather than a long omnibus audit;
- do not use a probe merely to discover an executable path when a safer direct file/read-only query exists;
- host assertions remain mandatory, but discovery aborts should return control to the operator shell rather than closing it.

Before modifying a service, capture the state that controls both current operation and restart behavior:

- effective systemd unit, including drop-ins;
- service state, PID, restart count, and actual command line;
- actual listeners;
- deployed source/package revision;
- relevant credential/policy metadata without exposing secrets;
- host/container network path required by the service;
- reboot-persistent network configuration where network reachability is part of the deployment;
- backend side-effect state where disabling side effects is an acceptance requirement.

A working request is not proof that restart state is correct.

## Persistence must be proved

For any required network or service state, distinguish:

- current kernel/runtime state;
- persistent configuration;
- boot-time mechanism that restores the persistent configuration.

Examples include:

- `net.ipv4.ip_forward` and its sysctl source;
- live iptables rules, saved rules, and the service/plugin that restores them;
- live WireGuard state, its protected configuration file, and enabled `wg-quick` service;
- current systemd process arguments and the unit/drop-ins that produce those arguments after restart.

The existence of a configuration file is not sufficient evidence that it is applied at boot.

## Repository/live-state comparison

The repository defines the intended restart-safe target state. Production acceptance compares that target against the live node.

Drift is classified before correction:

- **runtime drift** — the current process differs from intended behavior;
- **restart drift** — current process works, but files/unit state would produce different behavior after restart;
- **repository drift** — checked-in deployment assets do not describe the intended production state;
- **policy drift** — deployed authorization/quota/policy values differ from accepted deployment policy;
- **documentation drift** — actual node identity, route, dependency, or acceptance state is not recorded accurately.

Repository corrections should be made before production changes when the repository itself is wrong.

## Write discipline

A production step performs one state-changing action.

After that action:

1. verify exactly what changed;
2. compare it with the expected result;
3. stop on any discrepancy;
4. do not advance to the next write until the evidence is reviewed.

Do not combine credential transfer, unit creation, daemon reload, restart, health test, and rollback into one script.

Deletion and cleanup are also writes and are verified separately.

## Cross-host transfers

Network reachability does not imply an administrative authentication path.

Before transferring a credential or deployment artifact between hosts:

1. independently verify destination host identity;
2. verify the intended administrative authentication method;
3. do not introduce password/root automation merely to complete the deployment;
4. avoid nested `ssh | pct exec | shell` pipelines;
5. stage one bounded copy at a time;
6. verify owner, mode, size, and cryptographic digest without printing secret content.

## Restart gate

Restart is a separate explicit production action.

Before restart:

- deployed code/package is the intended revision;
- service unit/drop-ins are the intended restart-safe form;
- credentials/policy files exist with correct ownership/mode;
- `systemd-analyze verify` or equivalent static validation has passed where applicable;
- listener/bind arguments are explicit when defaults would be unsafe;
- any backend explicitly required to remain disabled is still disabled.

Only then may the service be restarted.

After restart, re-check PID, restart count, effective command, listener, health, authentication behavior, and required end-to-end route.

## Network-change separation

Application deployment does not modify forwarding, bridges, NAT, firewall, WireGuard, or relay topology unless a separate network defect has first been diagnosed.

A network change has its own:

- host assertion;
- before-state;
- one-write change;
- immediate verification;
- persistence verification;
- post-change reachability test.

## Acceptance evidence

A deployment is not marked accepted from memory or narrative alone. Record at least:

- repository commit;
- physical host and CT identity;
- deployed source/package revision;
- effective unit/drop-ins;
- required credentials/policies by metadata only;
- listener/bind state;
- network path and persistence evidence where required;
- authentication-negative tests;
- successful bounded positive/validation-only test;
- side-effect state;
- remaining deferred gates.

Repository implementation, production deployment, and production acceptance are separate states.

## Reference deployment

The first use of this protocol is the Kane publication path:

```text
srv-b / CT105 / civic-orchestrator
        ->
srv-b wg0 / 10.110.0.12
        ->
proxmox1 / 10.110.0.21:8046 relay
        ->
proxmox1 / CT106 / publication1 / 192.168.1.106:8046
```

`proxmox1 / CT102 / ipfs1.diagnostics.kane-il.us` is not part of this stack.

See `KANE_PUBLICATION_DEPLOYMENT_ACCEPTANCE.md` for the evolving evidence record.
