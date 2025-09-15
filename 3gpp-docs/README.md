# 3GPP Documentation for SMF-UPF Lawful Interception

This directory contains comprehensive 3GPP documentation and code generation templates for implementing lawful interception interfaces between SMF (Session Management Function) and UPF (User Plane Function) in 5G networks.

## Overview

Lawful interception in 5G networks involves monitoring and intercepting user communications for legal purposes. The SMF-UPF interface plays a crucial role in this process by managing session contexts and enabling the UPF to perform packet inspection and forwarding to Law Enforcement Agencies (LEAs).

## Key 3GPP Specifications

- **TS 29.244**: Interface between the Control Plane and the User Plane of EPC Nodes
- **TS 33.126**: Lawful Interception (LI) architecture and stage 2
- **TS 29.244**: PFCP (Packet Forwarding Control Protocol) specification
- **TS 33.501**: Security architecture and procedures for 5G System
- **TS 23.501**: System architecture for the 5G System

## Directory Structure

```
3gpp-docs/
├── specifications/          # 3GPP specification documents
├── interfaces/             # Interface definitions and schemas
├── code-templates/         # Code generation templates
├── examples/              # Implementation examples
├── cursor-rules/          # Cursor AI configuration
└── tools/                 # Code generation tools
```

## Quick Start

1. Review the relevant 3GPP specifications in `specifications/`
2. Use the code templates in `code-templates/` to generate implementation code
3. Follow the examples in `examples/` for practical implementation
4. Configure Cursor AI using rules in `cursor-rules/`

## Lawful Interception Flow

1. **Interception Request**: LEA requests interception through LI-ADMF
2. **Session Context**: SMF creates session context with LI parameters
3. **PFCP Session**: SMF establishes PFCP session with UPF
4. **Traffic Steering**: UPF steers traffic to LI-X1 and LI-X2 interfaces
5. **Data Collection**: UPF collects and forwards intercepted data
6. **Reporting**: UPF reports interception status to SMF

## Code Generation

Use the provided templates and Cursor AI rules to generate:
- PFCP message structures
- Session management code
- Traffic steering rules
- LI interface implementations
- Error handling and logging