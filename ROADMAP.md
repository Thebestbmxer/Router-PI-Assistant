Router Pi Assistant — Canonical Development Roadmap
GitHub Repository: https://github.com/Thebestbmxer/Router-PI-Assistant

Project: Router-PI-Assistant
Package: router-pi-controller
Python package: router_controller
Target platform: Raspberry Pi / Debian Linux
Router platform: OpenWrt, with special consideration for legacy/resource-constrained devices
Current release: 0.4.4
Roadmap status: Active
Last updated: 2026-09-07
1. Purpose

Router Pi Assistant is a Raspberry Pi-based controller for discovering, provisioning, managing, and monitoring OpenWrt routers.

The long-term objective is to provide a reliable management layer between a Raspberry Pi and OpenWrt routers, particularly older devices with severe hardware and firmware constraints.

The controller should:

    Discover routers on the local network.
    Identify routers independently of their current IP address.
    Establish secure SSH communication.
    Bootstrap routers that do not yet have the controller's SSH key.
    Persist router identity and state.
    Recover from DHCP/IP changes.
    Collect normalized router information.
    Provide a web-based management interface.
    Keep OpenWrt-specific implementation details behind a clean integration layer.
    Be installable and upgradeable as a normal Debian system application.
    Remain testable without requiring a live router for most tests.

2. Roadmap Rules

This file is the canonical development roadmap.

The older files: (No longer included in GitHub Repository)

    Roadmap.txt
    current Roadmap.txt
    Previous Roadmap.txt
    Previous Roadmap 2.txt
    Previous Roadmap3.txt

are historical planning documents and should not be treated as competing sources of truth.

When implementation and roadmap disagree:

    Verify the actual source code.
    Run the test suite.
    Update this roadmap to reflect reality.
    Only then plan the next task.

Do not mark functionality complete merely because code exists. A milestone is complete when its behavior is implemented, tested, packaged where appropriate, and integrated into the actual application architecture.
3. Current Project State
3.1 Foundation

Status: COMPLETE

The original application foundation is operational.

Implemented:

    Python package structure.
    Flask application.
    Configuration system.
    Persistent application data directory.
    Logging.
    Application entry point.
    Systemd service.
    Dedicated service user/group.
    Debian packaging.
    Package installation.
    Package upgrade handling.
    Package removal/purge handling.
    Persistent data preservation.
    Version/changelog handling.
    GitHub Actions testing/release infrastructure.
    SSH key storage infrastructure.

The project uses the src/router_controller/ package layout and builds a Debian package through the existing debian/rules / pybuild infrastructure.
4. Current Release Baseline — 0.4.4

Status: COMPLETE / VERIFIED

The current installed system package is:

router-pi-controller 0.4.4

The Debian package was built locally and installed successfully.

The installed Python package is located at:

/usr/lib/python3/dist-packages/router_controller/

The installed package was explicitly verified to contain the current router repository integration.

This is important because an earlier development problem exposed a distinction between:

src/router_controller/

and:

/usr/lib/python3/dist-packages/router_controller/

The source tree contained newer code while the installed Debian package still contained version 0.4.3.

The correct solution was not to permanently rely on:

PYTHONPATH=src pytest

Instead, the current source was packaged and installed as 0.4.4.

The final system-level verification is:

pytest
109 passed

This confirms that the installed application code and the source tests are now aligned.
5. Testing Baseline

Status: COMPLETE / VERIFIED

Current test count:

109 tests
109 passed
0 failed

The suite covers:

    application startup
    configuration
    database/application persistence
    logging
    package metadata
    systemd
    package upgrade behavior
    router bootstrap
    SSH connections
    connection management
    SSH key installation
    SSH key management
    router discovery
    router neighbors/MAC discovery
    router identity
    router network information
    router state
    router provisioning
    router model
    SSH behavior

Both development-source execution and system-installed execution have been verified.

Preferred system-level verification:

pytest

Development-source verification may still use:

PYTHONPATH=src pytest

but the application must not depend on PYTHONPATH at runtime.
6. Router Identity Architecture

Status: COMPLETE

The controller now distinguishes router identity from router location.
Identity

A router's stable identity is based on:

MAC address
SSH host-key fingerprint

Location

A router's current location is represented by:

IP address
SSH port
network interface

This separation is essential because a router may receive a different IP address through DHCP without becoming a different router.

The architectural model is:

Router
├── identity
│   ├── MAC address
│   └── SSH host-key fingerprint
│
└── location
    ├── IP address
    ├── SSH port
    └── interface

This provides the foundation for future rediscovery and DHCP recovery.
7. Router State Persistence

Status: IMPLEMENTED / VERIFIED

Router state has now been introduced as a persistent application concern.

Implemented:

RouterState
├── mac_address
├── ssh_host_key
├── ip_address
├── ssh_port
├── username
├── first_seen
└── last_seen

And:

RouterStateRepository
├── save()
└── load()

State is stored beneath the controller's persistent data directory.

Tests verify:

    state can be saved
    state can be loaded
    missing state is handled
    router identity survives IP changes
    provisioning saves router state

8. Provisioning and Persistent State Integration

Status: COMPLETE FOR INITIAL PROVISIONING

The provisioning flow now integrates router state persistence.

Current lifecycle:

Discover router
      │
      ▼
Load/generate controller SSH key
      │
      ▼
Bootstrap SSH connection
      │
      ▼
Install controller public key
      │
      ▼
Build RouterState
      │
      ▼
Save RouterState
      │
      ▼
Close bootstrap connection
      │
      ▼
Create permanent key-based connection
      │
      ▼
Verify connection
      │
      ▼
Return Router

The factory now constructs and injects:

RouterStateRepository

into:

RouterProvisioner

The provisioner therefore owns the orchestration while the repository owns persistence.

This separation should be preserved.
9. Router Discovery

Status: COMPLETE

Current discovery architecture:

Pi network interfaces
        │
        ▼
Local IPv4 networks
        │
        ▼
Candidate addresses
        │
        ▼
SSH port check
        │
        ▼
RouterCandidate
        │
        ▼
Neighbor/MAC discovery

Discovery should remain separate from authentication and provisioning.

Discovery identifies candidates.

Bootstrap authenticates and provisions them.

Permanent connection handles normal communication.
10. MAC / Neighbor Discovery

Status: COMPLETE

The controller can use local network neighbor information to associate an IP address with a MAC address.

This allows the system to distinguish:

current router location

from:

known router identity

The long-term recovery strategy depends on this capability.
11. SSH Key Management

Status: COMPLETE

Implemented:

    SSH key generation.
    Existing key loading.
    Key integrity handling.
    Persistent controller key storage.
    Public-key installation.
    Idempotent key installation.
    Bootstrap authentication.
    Permanent key-based authentication.

The controller key pair is stored in the configured persistent data directory.
12. Bootstrap SSH

Status: COMPLETE

The bootstrap process supports initial router access before the controller key has been installed.

Current authentication strategy:

root + blank password
        │
        ├── success ──► provision
        │
        ▼
root + configured/default password
        │
        ├── success ──► provision
        │
        ▼
authentication failure

Bootstrap connections explicitly disable:

allow_agent=False
look_for_keys=False

This prevents accidental use of unrelated SSH credentials from the Raspberry Pi.

Bootstrap credentials now also carry the SSH host-key fingerprint.

The host key fingerprint is calculated using the SSH server key itself rather than relying on an unrelated connection property.
13. Permanent SSH Connection

Status: COMPLETE, SECURITY HARDENING REMAINS

RouterConnection currently provides:

    SSH authentication using the controller key.
    connection state.
    command execution.
    connection reuse behavior.
    clean shutdown.
    host-key fingerprint retrieval.
    connection error handling.

RouterConnectionManager provides a lifecycle abstraction above the raw connection.

This keeps the Flask application from directly managing SSH sessions.
14. NEXT: Secure Host-Key Verification

Status: NEXT DEVELOPMENT TASK

This is the next major security task.

The current permanent connection must not ultimately rely on:

AutoAddPolicy()

as the final trust model.

The desired model is:

Known Router
    │
    ▼
Expected SSH host-key fingerprint
    │
    ▼
SSH connection
    │
    ▼
Host key received
    │
    ├── MATCH ───────► CONNECT
    │
    └── MISMATCH ────► REJECT

Required behavior:

    Unknown router handling.
    Known fingerprint accepted.
    Matching fingerprint accepted.
    Changed fingerprint rejected.
    Fingerprint retrieved correctly.
    Fingerprint persisted.
    Fingerprint survives application restart.
    Identity mismatch produces a clear connection failure.
    No silent acceptance of a changed host key.

Required tests:

    unknown host key
    matching host key
    changed host key
    fingerprint persistence
    identity mismatch
    connection rejection
    bootstrap fingerprint becoming permanent router identity

Security principle:

    A router's SSH host key is an identity credential, not merely informational metadata.

15. NEXT: Complete Persistent Router Lifecycle

Status: PLANNED / HIGH PRIORITY

After secure host-key verification, integrate the persistent state into normal startup and reconnection.

Desired lifecycle:

Pi boots
   │
   ▼
Controller starts
   │
   ▼
Load RouterState
   │
   ├── No state
   │      │
   │      ▼
   │   Initial discovery
   │
   ▼
Known router
   │
   ▼
Try last known IP
   │
   ├── Success
   │      │
   │      ▼
   │   Verify MAC/identity
   │      │
   │      ▼
   │   Verify SSH host key
   │      │
   │      ▼
   │   CONNECT
   │
   └── Failure
          │
          ▼
      Local discovery
          │
          ▼
      MAC verification
          │
          ▼
      SSH host-key verification
          │
          ▼
        CONNECT
          │
          ▼
    Update RouterState

This is the point where router persistence becomes operational rather than simply historical.
16. Router Reconnection and DHCP Recovery

Status: PLANNED

The controller should tolerate routers changing IP addresses.

Recovery should prioritize:

    Last known IP.
    Local network discovery.
    MAC matching.
    SSH host-key matching.
    State update.

The MAC and SSH fingerprint must prevent a newly discovered unrelated device from being mistaken for the known router.
17. Router Information API

Status: PLANNED

The UI should not directly know how OpenWrt commands work.

Introduce a normalized router information API.

Conceptually:

Router
│
└── RouterInformation
    ├── system()
    ├── network()
    ├── security()
    └── services()

Possible public operations:

router.get_system_info()
router.get_network_info()
router.get_security_status()
router.get_services()

The API should return application-friendly structures rather than raw SSH output.
18. OpenWrt Integration Layer

Status: PLANNED

OpenWrt-specific commands should live behind an integration boundary.

Target architecture:

Controller
    │
    ▼
Router API
    │
    ▼
OpenWrt Integration
    │
    ▼
SSH
    │
    ▼
OpenWrt

Potential structure:

integrations/
└── openwrt/
    ├── system.py
    ├── network.py
    ├── security.py
    ├── services.py
    └── capabilities.py

The core controller should not become tightly coupled to OpenWrt-specific files, commands, or implementation details.
19. System Information

Status: PLANNED

Collect and normalize:

    hostname
    OpenWrt release/version
    kernel version
    target
    architecture
    CPU information
    RAM
    storage/flash
    uptime
    system load
    installed packages
    detected capabilities

The information layer should be mock-testable without requiring a live router.
20. Network Information

Status: PLANNED

Collect:

    interfaces
    IPv4 addresses
    IPv6 addresses where supported
    routes
    link state
    interface statistics
    VLAN information
    bridge information
    wireless information

Wireless information should eventually include:

    radios
    bands
    channels
    SSIDs
    AP/client state

21. Router Profile

Status: PLANNED / ARCHITECTURAL DIRECTION

The persistent router profile should eventually describe the managed device comprehensively.

Potential profile:

RouterProfile
├── manufacturer
├── model
├── hardware revision
├── architecture
├── CPU
├── RAM
├── flash/storage
│
├── identity
│   ├── factory MAC
│   ├── operational MAC
│   └── SSH host key
│
├── firmware
│   ├── OpenWrt version
│   ├── target
│   └── kernel
│
├── packages
├── capabilities
│
├── interfaces
├── wireless
├── switch
├── LEDs
│
└── current state

The profile should evolve from the currently implemented RouterState rather than replacing stable identity concepts.
22. Dashboard / Home Page

Status: PLANNED

The first operational dashboard should expose normalized information rather than raw SSH commands.

Initial information:

    router connection status
    router name
    model
    architecture
    target
    firmware
    kernel
    uptime
    CPU/system load
    memory usage
    storage usage
    network/interface status
    last-seen information
    identity status

The UI should clearly distinguish:

Connected
Disconnected
Unknown
Authentication failure
Identity mismatch
Discovery required

23. Diagnostics

Status: FUTURE

Provide read-only diagnostics such as:

    SSH connectivity
    router reachability
    DNS status
    network interface state
    routing state
    wireless state
    system resource usage
    service status
    storage status
    log access

Diagnostics should initially be read-only.
24. Device History

Status: FUTURE

Build on persistent router state to retain meaningful historical information.

Potential history:

    IP address changes
    connection failures
    SSH identity changes
    firmware changes
    package changes
    configuration snapshots
    uptime
    resource statistics
    interface changes
    wireless changes

History must not undermine the stable identity model.
25. Controlled Configuration

Status: FUTURE

Only after reliable read-only management is established should the controller begin modifying router configuration.

Configuration changes should be:

    explicit
    validated
    reversible where possible
    logged
    testable
    limited to supported operations

Avoid building a generic "execute arbitrary command" web interface.
26. Raspberry Pi Network Services

Status: FUTURE

Potential services include:

    DHCP assistance
    DNS assistance
    network monitoring
    router recovery
    provisioning network support
    local service discovery

These capabilities must be designed carefully so the controller does not accidentally disrupt the network it is intended to manage.
27. Advanced Network Functions

Status: FUTURE

Possible future functionality:

    controlled routing changes
    firewall management
    VLAN configuration
    wireless configuration
    WAN/LAN management
    service management
    network diagnostics
    backup/restore

These features depend on the completion of the read-only information and safety layers.
28. Legacy 4 MB Router Support

Status: LONG-TERM OBJECTIVE

A major project goal is support for severely resource-constrained OpenWrt hardware such as the Netgear WNR1000v2 class of devices.

The controller should therefore favor:

    lightweight SSH operations
    minimal router-side dependencies
    small command payloads
    low memory usage
    low storage requirements
    external processing on the Raspberry Pi
    graceful degradation when router capabilities are unavailable

The Raspberry Pi should perform as much processing as possible rather than requiring a large software stack on the router.
29. Release and Packaging

Status: FUNCTIONAL / CONTINUING

Current packaging path:

Source
   │
   ▼
pybuild
   │
   ├── build wheel
   ├── run tests
   └── build Debian package
          │
          ▼
       .deb

Verified locally with version 0.4.4.

Release process should continue to guarantee:

Python package version
        =
Debian changelog version
        =
Debian package version
        =
Git release tag

Future releases should also verify the installed package, not merely the source tree.
30. Development Environment Integrity

Status: LESSON LEARNED / PROCESS REQUIREMENT

The project previously exposed a dangerous development condition:

source tree = newer code
system package = older code
pytest = older installed code

This occurred because Python imported:

/usr/lib/python3/dist-packages/router_controller/

instead of:

src/router_controller/

The correct resolution was to rebuild and install the Debian package.

Future development must explicitly distinguish:
Source-tree tests

PYTHONPATH=src pytest

Installed-system tests

pytest

Both should be kept functional.

The project should eventually configure the development tooling so contributors can run ordinary pytest from a checkout without accidentally testing a stale system installation.

This should be addressed as development infrastructure work, not by weakening the system packaging model.
31. Immediate Development Queue

The next work should be performed in this order.
Priority 1 — Secure SSH host-key verification

Implement:

    expected fingerprint handling
    matching fingerprint acceptance
    changed fingerprint rejection
    unknown-key policy
    clear identity mismatch errors
    tests for all cases

Do not move to large UI features before this security boundary is correct.
Priority 2 — Complete persistent router lifecycle

Implement:

    startup state loading
    last-known-IP connection
    fallback discovery
    MAC matching
    SSH fingerprint matching
    state updates
    reconnect behavior

Priority 3 — Improve development/package test isolation

Ensure:

pytest

from the repository cannot silently test an unrelated stale system installation.

Preserve the ability to test the actual installed Debian package separately.
Priority 4 — Router Information API

Introduce normalized system/network/security/service information.
Priority 5 — OpenWrt integration layer

Move OpenWrt-specific operations behind a clean integration boundary.
Priority 6 — Read-only dashboard

Expose router state and normalized information through the Flask application.
32. Milestone Sequence

The consolidated milestone sequence is:

M0.0 — Development Foundation                 ✅
   │
   ▼
M0.1 — Application Foundation                 ✅
   │
   ▼
M0.2 — Debian Packaging                       ✅
   │
   ▼
M0.3 — SSH Provisioning                       ✅
   │
   ▼
M0.4 — Router Identity                        ✅
   │
   ▼
M0.5 — Router State Persistence                ✅
   │
   ▼
M0.6 — Network/MAC Discovery                  ✅
   │
   ▼
M0.7 — Persistent SSH Connection              ✅
   │
   ▼
M0.8 — Connection Manager                     ✅
   │
   ▼
M0.9 — Secure Host-Key Verification           🔴 NEXT
   │
   ▼
M1.0 — Complete Persistent Router Lifecycle   🟡
   │
   ▼
M1.1 — Router Information API                 📋
   │
   ▼
M1.2 — OpenWrt Integration                    📋
   │
   ▼
M1.3 — Read-Only Dashboard                    📋
   │
   ▼
M2.0 — Live Diagnostics                       📋
   │
   ▼
M3.0 — Device History                         📋
   │
   ▼
M4.0 — Controlled Configuration               📋
   │
   ▼
M5.0 — Pi Network Services                    📋
   │
   ▼
M6.0 — Advanced Network Functions             📋
   │
   ▼
M7.0 — Legacy 4 MB Router Support             📋

33. Session Accomplishments — 2026-09-07

This section records the work completed during the development session so the next session does not need to reconstruct the context.
Router repository integration

Completed:

    RouterStateRepository dependency added to RouterProvisioner.
    Repository constructed by factory.py.
    Repository injected into RouterProvisioner.
    Provisioning saves router state.
    Router state is built from bootstrap credentials and discovery data.
    MAC address is required for persistent router state.

Bootstrap fingerprint handling

Completed:

    Bootstrap obtains the remote SSH host key.
    Host-key fingerprint is calculated from the Paramiko key bytes.
    BootstrapCredentials carries the SSH fingerprint.
    Tests were corrected to provide a real test host key rather than a mock/function.
    All bootstrap tests pass.

Provisioning tests

Completed:

    Provisioner tests updated for bootstrap credentials.
    Router state persistence tested.
    Bootstrap connection lifecycle tested.
    Permanent connection lifecycle tested.
    Repository save behavior tested.

Test result

Final system-wide test result:

109 passed in 8.74s

The important command was:

pytest

with no PYTHONPATH=src override.
Debian packaging

Completed:

router-pi-controller 0.4.4

Built:

router-pi-controller_0.4.4_all.deb

Installed successfully using:

sudo dpkg -i ../router-pi-controller_0.4.4_all.deb

The installed package was verified to contain the router repository integration.
Important development lesson

The earlier two application test failures were not caused by the current source tree.

The system was loading the previously installed:

router-pi-controller 0.4.3

while the repository contained newer source code.

Rebuilding and installing 0.4.4 resolved the discrepancy.

This confirms that Debian packaging is part of the application's actual integration environment and must be tested as such.
34. Next Session Starting Point

When development resumes, start here:

Current release: 0.4.4
Tests: 109 passed
Working tree: verify with git status
Next milestone: M0.9 Secure Host-Key Verification

Do not restart router discovery, SSH provisioning, router identity, or router state work unless a test demonstrates that those components are incomplete.

The immediate architectural question is:

    How does the permanent SSH connection prove that the router it is connecting to is the same router whose identity was previously established?

The answer should use the persisted:

MAC address
+
SSH host-key fingerprint

and should reject identity mismatches.

After that security boundary is complete, implement the startup/reconnect lifecycle using the persisted RouterState.
35. Definition of Done for the Current Architecture

The current router-management foundation will be considered complete when all of the following are true:

    Router can be discovered.
    Router MAC can be determined.
    Router identity can be represented independently of IP.
    Controller SSH keys can be generated.
    Existing controller keys can be loaded.
    Bootstrap SSH works.
    Bootstrap credentials include host-key identity.
    Controller public key can be installed.
    Permanent SSH connection works.
    Connection lifecycle is managed.
    Router state can be persisted.
    Router state can be loaded.
    Initial provisioning saves router state.
    Debian package builds.
    Debian package installs.
    System package contains current source.
    Normal pytest runs against the installed application.
    109 tests pass.
    Permanent SSH verifies the expected host key.
    Startup loads persisted router state.
    DHCP/IP changes trigger identity-based rediscovery.
    Router information is exposed through a normalized API.
    OpenWrt-specific operations are isolated.
    Read-only dashboard displays router information.

36. Guiding Architecture

The project should continue converging toward this architecture:

                         Browser
                            │
                            ▼
                     Flask Web UI
                            │
                            ▼
                  Application Services
                            │
                            ▼
                       Router API
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
       Router State              OpenWrt Integration
       Repository                       │
                │                       ▼
                │                Router Connection
                │                       │
                └───────────┐           ▼
                            └───────► SSH
                                      │
                                      ▼
                                   OpenWrt

Identity should remain separate from location.

Persistence should remain separate from communication.

Communication should remain separate from the web UI.

OpenWrt-specific behavior should remain separate from the core router model.

Security verification should happen before a known router is trusted.

The Raspberry Pi should perform heavyweight management work so the OpenWrt device can remain lightweight.
37. Final Principle

The project is no longer primarily an SSH provisioning script.

It is becoming a persistent router management controller.

The architectural progression should therefore remain:

Discover
   ↓
Identify
   ↓
Bootstrap
   ↓
Persist
   ↓
Verify
   ↓
Reconnect
   ↓
Observe
   ↓
Manage

Each layer should be independently testable and should build on the previous layer without collapsing responsibilities together.

One important correction from the old roadmap: I marked the Debian/release foundation as effectively complete, but kept automated release/distribution work as continuing infrastructure rather than claiming the entire release system is finished. The existing roadmap describes GitHub Actions release building, tag/version validation, .deb creation, and artifact publishing as the intended release path.

For the next session, the first line of attack should therefore be M0.9 Secure Host-Key Verification, not more database work. The database/state foundation is now good enough to support that security layer.