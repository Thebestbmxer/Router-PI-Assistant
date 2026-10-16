Router-PI-Assistant Roadmap

Status: Active development
Primary target: Raspberry Pi running Linux, managing an OpenWrt router
Authoritative roadmap: This file
Last reviewed: 2026-10-16

1. Project vision

Router-PI-Assistant is a Raspberry Pi-based management appliance that provides a secure, centralized interface for administering an OpenWrt router and eventually managing additional network services hosted on the Pi.

The long-term goal is to make the Pi the trusted management point for the network appliance, providing router status, network configuration, an administrative terminal, service management, monitoring, and recovery capabilities.

Development prioritizes security, reliability, testability, and incremental delivery.

2. Development principles
Preserve working functionality. Extend the existing architecture instead of rebuilding completed components.
One management path. Application services use the Router abstraction, connection manager, and established SSH infrastructure rather than creating independent router connections.
Read before write. Implement and validate read-only status collection before introducing configuration changes.
Secure by default. Verify router identity, protect credentials, and restrict the management interface to the intended LAN boundary.
Test every change. Add automated tests for new behavior and run the existing suite before deployment.
Validate on hardware. Mocked tests are necessary but do not replace testing against the actual router.
Deliver in small increments. Each milestone must have clear acceptance criteria.
Keep this roadmap current. Completed work is removed from the active backlog only after its acceptance criteria are met.
3. Current baseline

The existing roadmap reports completion of the following foundations:

Python application structure and packaging.
Flask application infrastructure, configuration, and logging.
systemd integration and upgrade-related support.
Automated tests for application and router communication functionality.
Router discovery and stable identity.
Persistent router state.
SSH key management and bootstrap provisioning.
Authenticated SSH connections with host-key verification.
Router connection management and integration with persisted state.

The existing roadmap reports 111 passing tests. This is a documented baseline, not a guarantee that the suite has been rerun against the current checkout.

Before beginning new implementation work, verify the current code, test results, installed Raspberry Pi version, and physical-router behavior. Update this section when the baseline has been confirmed.

4. Milestone 1 — Complete the core management workflow

Priority: P0 — Immediate

Objective: Allow a LAN administrator to open Router-PI-Assistant and inspect trustworthy, live information from the connected router.

Work items
Finalize the application-facing Router management API.
Establish clear boundaries between Flask routes, application services, router state, the connection manager, and SSH transport.
Implement structured router system status collection.
Implement structured network status collection.
Integrate status models and parsing with the existing router communication architecture.
Add a read-only Router Status page.
Add a connection-aware Router Status entry point to the Welcome page.
Test the complete workflow using both mocked connections and the physical OpenWrt router.
Initial status information

System:

Hostname, model, and firmware release.
Kernel, architecture, and platform.
Uptime, load average, and local time.

Network:

Interfaces and IP addresses.
Routes and WAN/LAN state.
DHCP and DNS information where available.
Wireless status where supported.

Management:

Known router identity.
Current connection state.
SSH host-key identity.
Current address and last-seen information.
Clear error details when status cannot be retrieved.

Optional fields must be handled gracefully when a router does not expose them.

Acceptance criteria
The application uses the existing trusted router connection.
Status is returned as structured application data, not raw shell output.
The UI distinguishes connected, disconnected, stale, and failed status retrieval.
No router configuration is changed by status requests.
Automated tests cover parsing, missing data, and connection failures.
The complete workflow succeeds against the physical router.

Milestone complete when: A LAN user can open the application, see the router connection state, and inspect real read-only system and network status.

5. Milestone 2 — Reliable administration and terminal access

Priority: P1 — After Milestone 1

Objective: Make the Pi a dependable administrative entry point for the router.

Work items
Implement an interactive SSH session abstraction using the existing connection infrastructure.
Provide a web terminal with streaming input/output, clean session termination, and long-running command support.
Handle terminal resizing, interruption, and session timeouts.
Recover cleanly from router reboots, SSH disconnects, and network interruptions.
Distinguish connectivity failures from host-identity or authentication failures.
Add refreshable router health and last-seen information.
Add appropriate session access controls, request validation, and audit logging.
Acceptance criteria
The terminal does not create a competing SSH connection implementation.
Sessions terminate safely and do not persist unintentionally.
Disconnects and authentication failures are reported clearly.
The terminal cannot be accessed from unintended network interfaces.
Automated tests cover session lifecycle and failure handling.
Interactive terminal behavior is validated against the real router.
6. Milestone 3 — Structured router network management

Priority: P2 — After the management workflow is reliable

Objective: Provide common router administration operations through validated application services.

Work items
Introduce structured, validated configuration operations.
Add interface and IP-address management.
Add WAN/LAN configuration and connectivity status.
Add DHCP and DNS management.
Add wireless configuration.
Add firewall and service management.
Refresh displayed state after successful changes.
Provide clear validation errors and operation results.
Safety requirements
Validate requested changes before executing them.
Avoid building arbitrary shell commands directly from web input.
Require explicit confirmation for disruptive operations.
Detect changes that could disconnect the administrator.
Where feasible, support rollback or a recovery procedure.
Do not report success until the operation has been verified.
Acceptance criteria
Each operation has a defined input, validation process, and result.
Tests cover invalid input, command failures, and state refresh.
Critical operations have documented recovery procedures.
Real-router tests demonstrate successful changes and recovery from failures.
7. Milestone 4 — Raspberry Pi network services

Priority: P3 — After core router administration

Objective: Integrate services that complement OpenWrt and provide centralized network-service management.

Work items
Integrate Pi-hole status and service management.
Integrate Unbound status and service management.
Expose DNS health and resolver availability.
Present service state, relevant statistics, and configuration status.
Define the intended DHCP/DNS configuration between OpenWrt, Pi-hole, and Unbound.
Add service restart, failure reporting, and recovery workflows.
Verify the complete DNS path from a LAN client to the upstream resolver.
Acceptance criteria
The application distinguishes service failure from router connectivity failure.
DNS dependencies and configuration are documented.
Service operations are validated and recoverable.
DNS behavior is verified from an actual LAN client.
8. Milestone 5 — Managed appliance and release readiness

Priority: P4 — After the core platform is stable

Objective: Make the system safer to operate, maintain, update, and recover.

Work items
Implement router configuration backup, comparison, and controlled restore.
Associate backups with router identity and validate the target before restoration.
Add firmware information and upgrade preparation.
Implement firmware upgrades only after recovery and post-upgrade verification procedures are established.
Review management-interface binding, authentication, authorization, secrets, and logging.
Validate installation and upgrades using the project's packaging and systemd infrastructure.
Add hardware-specific integration testing alongside the normal automated test suite.
Document recovery, backup restoration, and troubleshooting.
Establish release and version-validation procedures.
Acceptance criteria
Installation and upgrades are reproducible on the target Raspberry Pi.
Existing application data survives supported upgrades.
Backup restoration validates the target router and configuration.
High-risk operations have explicit safeguards and documented recovery.
Release checks and automated tests pass before deployment.
9. Architecture and compatibility decisions
Router management architecture

Maintain the separation between:

Web interface and Flask routes.
Application services.
Router and persistent router state.
Router connection manager.
SSH connection and transport.
Structured status models and configuration operations.
Firmware providers

The existing firmware-provider proposal should be reconciled with the actual code before implementation.

OpenWrt remains the primary target. Additional firmware support should be introduced only when a concrete need exists and the provider boundary offers a practical benefit.

If implemented, firmware-specific providers should translate device-specific responses into common application models without replacing the trusted connection infrastructure.

Do not build multiple firmware adapters speculatively.

Persistence

Keep persistent router identity and state separate from transient SSH connections. Confirm that state updates, changed IP addresses, timestamps, and router lookup remain consistent across application restarts.

10. Testing and quality gates

For each change:

Add or update automated tests.
Run the complete existing test suite.
Check packaging, application startup, and relevant static or release checks.
Deploy the change to the Raspberry Pi.
Validate the feature against the physical router when the change affects real router behavior.
Record any limitations or known failures.

Maintain separate categories for:

Unit tests.
Mocked integration tests.
Packaging and installation tests.
Hardware-specific router tests.

Normal development must not require a physical router for every test run.

11. Development and deployment workflow

The standard development cycle is:

Develop in Visual Studio on the development machine.
Run the local test suite and relevant checks.
Commit and push changes to GitHub.
Pull the intended revision onto the Raspberry Pi.
Run required installation or upgrade steps.
Restart the application service if necessary.
Check service health and application logs.
Verify the change through the web interface and against the physical router when applicable.

Keep the deployed revision identifiable so that a failed deployment can be diagnosed and rolled back to a known-good revision.

Do not deploy untested changes directly into a workflow that could interrupt router administration.

12. Immediate development queue

Work in this order:

Verify the current code and actual test baseline.
Reconcile the Router API and application service boundaries.
Complete structured, read-only system status collection.
Complete structured network status collection.
Add and test the Router Status application endpoint.
Build the Router Status page and Welcome-page entry point.
Validate the complete status workflow against the physical router.
Begin interactive SSH terminal design and implementation.
Improve connection recovery and health reporting.
Begin structured network configuration operations.
Plan Pi-hole and Unbound integration.
Prepare appliance hardening and release readiness.
13. Scope control

The following are not immediate priorities:

Supporting multiple additional firmware platforms before OpenWrt management is proven.
Building a complex dashboard before the underlying status data is reliable.
Implementing broad configuration management before read-only collection is stable.
Adding advanced automation before safe, validated operations exist.
Implementing firmware upgrades before recovery procedures are established.

These features remain possible future work; they should not delay the current milestone.

Definition of success

The project succeeds when Router-PI-Assistant provides a secure and dependable LAN management interface for an OpenWrt router, uses a consistent and trusted management architecture, and can be installed, upgraded, tested, and recovered on the Raspberry Pi.

The first major delivery is a fully tested, read-only router status workflow against the real device. Subsequent milestones build on that verified foundation.