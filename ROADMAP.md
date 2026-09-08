Router-PI-Assistant Roadmap

Current baseline: 111 tests passing.

The project has evolved from a router-provisioning utility into something broader: a LAN-based router management appliance running on the Raspberry Pi.

The Pi is intended to become the trusted management plane for the router while also hosting services that the router cannot efficiently provide, such as Pi-hole and Unbound.
Phase 1 — Application Foundation ✅
1. Project structure and packaging — Complete

The project has a proper installable src/ layout with:

    application configuration
    logging
    Flask application infrastructure
    package metadata
    systemd support
    upgrade support
    application entry point

The project is structured as a system application rather than depending on development-directory execution.
2. Automated testing — Complete

The project now has a broad automated test suite covering application and router communication functionality.

Current baseline: 111 tests passing.
Phase 2 — Router Discovery & Identity ✅
3. Router discovery — Complete

The controller can discover router candidates and represent their network information.
4. Router identity — Complete

Router identity is based on stable information including:

    MAC address
    SSH host-key fingerprint

This allows the controller to distinguish a known router from a newly discovered device.
5. Persistent router state — Complete

Router state can be represented and persisted independently of transient discovery information.

This establishes the foundation for recognizing routers across application restarts.
Phase 3 — Secure Router Access ✅
6. Controller SSH key management — Complete

The controller can load or generate its SSH key pair.
7. Bootstrap provisioning — Complete

The provisioning workflow can:

    establish initial router access
    install the controller's public key
    close the bootstrap connection
    establish the permanent controller connection

8. Persistent SSH connections — Complete

The project has a dedicated SSH connection abstraction handling:

    controller-key authentication
    connection lifecycle
    command execution
    connection state
    cleanup
    communication failures

9. SSH host identity verification — Complete

The permanent SSH connection verifies the router's expected host-key fingerprint.

This establishes the core trust relationship:

Pi
 │
 │ trusted SSH identity
 ▼
Router

10. Connection manager — Complete

RouterConnectionManager provides the higher-level connection lifecycle and incorporates persisted router state when creating SSH connections.
11. Router/connection integration — Complete

Router now retains:

    identity
    discovery candidate
    persistent state
    connection manager

The router object is therefore becoming the central representation of a managed router.
Phase 4 — Management Plane 🔄

Current development phase

The focus now shifts from "Can the Pi connect to the router?" to:

    "Can the Pi manage the router and provide the administrator with a useful management interface?"

The Raspberry Pi becomes the authoritative management plane.

LAN Administrator
        │
        ▼
Router-PI-Assistant
        │
        ▼
RouterConnectionManager
        │
        ▼
OpenWrt Router

12. Establish the Router management API

Next priority

Make Router the central object used by application services.

The architecture should develop toward:

Web/UI
  │
  ▼
Application Services
  │
  ▼
Router
  │
  ▼
RouterConnectionManager
  │
  ▼
RouterConnection
  │
  ▼
Paramiko

Higher-level application code should not directly manipulate Paramiko.

This provides one consistent management path for:

    status
    configuration
    networking
    services
    terminal
    future automation

Phase 5 — Router Status Interface
13. Build Router Status service

Create a read-oriented service responsible for obtaining structured information from the router.

Initial information should include:
System

    hostname
    OpenWrt release
    kernel
    architecture
    target/platform
    uptime

Network

    interfaces
    addresses
    routes
    WAN status
    LAN status
    DNS configuration

Management

    SSH connection state
    router identity
    host-key fingerprint
    current IP
    last-seen information

The service should return structured application data rather than raw command output.
14. Build the Router Status page

Add a new web page displaying the information collected by the status service.

The first version should be intentionally read-only.

This becomes the first real end-to-end management feature:

Browser
   ↓
Flask
   ↓
Router Status Service
   ↓
Router
   ↓
SSH
   ↓
OpenWrt

This page will also become an important real-router testing interface.
15. Add Router Status to the Welcome page

The Welcome page should expose a:

Router Status

button.

The button should reflect the router's actual management connection state.
Connected

[ Router Status ]

enabled.
Not connected

The button should either be disabled or clearly indicate that the router is unavailable.

The UI should derive this state from the application rather than independently determining SSH connectivity.
Phase 6 — Integrated Router Terminal
16. Add a web terminal

A terminal should become a first-class management feature.

Conceptually:

Administrator
     │
     │ Browser
     ▼
Router-PI-Assistant
     │
     │ SSH
     ▼
OpenWrt root shell

The terminal gives administrators complete router access even when a particular management function has not yet been implemented in the GUI.

This is especially useful during development.
17. Implement interactive SSH sessions

The existing execute() API is suitable for individual commands but not a true terminal.

The terminal should eventually use an interactive SSH channel/PTY supporting:

    persistent shell session
    stdin
    stdout
    stderr
    streaming output
    Ctrl-C
    terminal resize
    long-running commands
    clean session termination

The architecture should become:

Web Terminal
     │
     ▼
Terminal Service
     │
     ▼
RouterConnectionManager
     │
     ▼
Interactive SSH channel
     │
     ▼
OpenWrt shell

The terminal should reuse the same trusted router connection infrastructure rather than creating an independent SSH implementation.
Phase 7 — Router Network Management
18. Implement structured network management

Once status is working, build services around the router's network configuration.

Initial areas:

    interfaces
    IP addresses
    DHCP
    DNS
    routes
    WAN
    LAN
    wireless
    firewall

The GUI should progressively expose common operations while the terminal remains available for advanced administration.
19. Router configuration management

Introduce controlled configuration operations.

Potential areas:

    hostname
    LAN configuration
    WAN configuration
    DHCP
    DNS
    wireless
    firewall
    services

The preferred architecture is:

GUI operation
      ↓
Router service
      ↓
validated operation
      ↓
SSH
      ↓
OpenWrt

rather than generating arbitrary shell commands in Flask routes.
Phase 8 — Pi as Network Services Platform

The project should now expand beyond router management.

The Raspberry Pi becomes the host for services that complement OpenWrt.
20. Pi-hole integration

Provide management and status information for Pi-hole.

Potential GUI areas:

    service status
    DNS status
    blocked queries
    query statistics
    configuration
    start/stop/restart

21. Unbound integration

Provide management of the local recursive DNS resolver.

Potential functionality:

    service status
    configuration
    DNS health
    resolver statistics
    start/stop/restart
    integration with Pi-hole

22. Unified DNS architecture

Eventually the application should understand the intended DNS path:

LAN Clients
     │
     ▼
    Pi-hole
     │
     ▼
   Unbound
     │
     ▼
   Internet

while Router-PI-Assistant manages the router-side DHCP/DNS configuration needed to make that architecture work.
Phase 9 — Router as a Managed Appliance
23. Router configuration profiles

Introduce higher-level configuration concepts.

For example:

Home Network
Small Office
Secure DNS
Guest Network
IoT Network

The controller could eventually translate these into router configuration.

This is where Router-PI-Assistant begins moving from a collection of management commands toward an actual configuration-management system.
24. Configuration backup and restore

Implement router configuration lifecycle management:

Router
  │
  ├── Backup
  │
  ├── Restore
  │
  └── Compare

Backups should be associated with the known router identity and managed carefully so that configurations cannot accidentally be restored to the wrong device.
25. Firmware management

Eventually support:

    firmware information
    available firmware
    upgrade preparation
    firmware installation
    reboot monitoring
    post-upgrade verification

Firmware operations should be treated as high-risk operations with additional validation and recovery handling.
Phase 10 — Management Access Control
26. Router SSH exposure management

The Pi should be the router's default SSH management path:

Pi → Router SSH       ENABLED
LAN → Router SSH      DISABLED
WAN → Router SSH      DISABLED

The application should provide an explicit mechanism to allow secondary LAN SSH access when the administrator wants it.

For example:

Router SSH Access

Pi management       ON
LAN SSH access      OFF

[ Enable LAN SSH ]

This allows the Pi to remain the router's primary management authority without permanently preventing advanced users from connecting directly.
27. Define the LAN management boundary

The intended deployment model is:

                    WAN / WWAN
                        │
                        X
                        │
                     Router
                        │
                       LAN
                        │
                ┌───────┴───────┐
                │               │
               Pi            LAN users
                │
        Router-PI-Assistant

The management application should be designed so that the administrative interface is intended for LAN access and is not accidentally exposed through WAN/WWAN interfaces.
Phase 11 — Reliability & Monitoring
28. Connection recovery

Handle:

    router reboot
    SSH disconnects
    network interruptions
    stale connections
    temporary router unavailability

The controller should distinguish between connection failures and identity/security failures.
29. Router state refresh

Introduce regular or on-demand state refresh.

For example:

Router
 ├── Refresh status
 ├── Refresh network
 └── Refresh identity

The controller should maintain accurate last_seen and connectivity information.
30. Health monitoring

Eventually monitor both the router and Pi-hosted services.

System Health
├── Router
│   ├── SSH
│   ├── WAN
│   ├── LAN
│   └── DNS
│
└── Pi
    ├── Pi-hole
    ├── Unbound
    └── Router-PI-Assistant

Phase 12 — Persistence Architecture
31. Complete the router repository

The remaining repository architecture should be finalized so the application has one clear persistent model for known routers.

It should support:

    locating a router by MAC
    loading persistent state
    updating state
    tracking router identity
    handling changed IP addresses
    recording timestamps

The database should store persistent information; live SSH connections should remain transient application objects.
Phase 13 — Testing & Validation
32. Expand mocked integration tests

Test complete workflows such as:

Discovery
   ↓
Provisioning
   ↓
Persistence
   ↓
Connection
   ↓
Status collection
   ↓
Web presentation

33. Add real-router integration tests

Eventually maintain a separate hardware test category for a physical OpenWrt router.

Normal development remains:

pytest

while hardware-specific tests can be run separately.

This prevents a physical router from becoming a prerequisite for normal application development.
Phase 14 — Long-Term Platform

Once the above pieces are mature, Router-PI-Assistant can become a unified network-management platform:

                         LAN Administrator
                                │
                                ▼
                 ┌──────────────────────────┐
                 │   Router-PI-Assistant    │
                 │                          │
                 │ Dashboard                │
                 │ Router Status             │
                 │ Network Management        │
                 │ Configuration             │
                 │ Terminal                  │
                 │ Service Management        │
                 └────────────┬─────────────┘
                              │
              ┌───────────────┴────────────────┐
              │                                │
              ▼                                ▼
        ┌───────────┐                    ┌─────────────┐
        │  OpenWrt  │                    │ Raspberry Pi│
        │  Router   │                    │  Services   │
        └───────────┘                    └─────────────┘
              │                                │
       ┌──────┼───────┐                 ┌──────┼──────┐
       │      │       │                 │      │      │
      WAN    LAN    WiFi              Pi-hole Unbound ...

The long-term goal is therefore not simply "a GUI for SSH."

It is:

    A Raspberry Pi-based management plane that securely controls an OpenWrt router, provides advanced network services, and gives the LAN administrator a unified interface for the entire network appliance.

Immediate Development Queue

Given the current 111/111 test baseline, I recommend we proceed in this exact order:

    Define RouterStatus and the router status service.
    Implement read-only OpenWrt system information collection.
    Implement network information collection.
    Add tests for command parsing and status generation.
    Create the /router/status Flask route.
    Build the Router Status page.
    Add the connection-aware Router Status button to the Welcome page.
    Test the complete status workflow against the physical router.
    Design the interactive SSH/PTY abstraction.
    Add the web terminal using the existing router connection architecture.
    Begin structured router network/configuration management.
    Begin Pi service integration with Pi-hole and Unbound.

The immediate milestone is now:

    A LAN user can open Router-PI-Assistant, see whether the Pi has a trusted SSH connection to the router, open Router Status, and inspect real read-only information collected directly from OpenWrt.

Once that works against the actual router, the terminal becomes the natural next feature and gives us a powerful administrative fallback while the structured management APIs continue to grow.