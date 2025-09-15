# TS 29.244 - PFCP (Packet Forwarding Control Protocol)

## Overview
PFCP is the protocol used between the Control Plane (SMF) and User Plane (UPF) functions in 5G networks for session management and traffic steering.

## Key PFCP Messages for Lawful Interception

### Session Establishment Request (SER)
```json
{
  "message_type": "Session Establishment Request",
  "node_id": "smf.example.com",
  "f_seid": "0x1234567890abcdef",
  "pfcp_session_id": 12345,
  "ie_list": [
    {
      "ie_type": "Create PDR",
      "pdr_id": 1,
      "precedence": 100,
      "pdi": {
        "source_interface": "access",
        "ue_ip_address": "192.168.1.100"
      },
      "far_id": 1,
      "urr_id": 1
    }
  ]
}
```

### Session Modification Request (SMR)
Used to modify existing sessions for LI purposes:
- Add/remove PDRs for traffic steering
- Update FARs for LI forwarding
- Configure URRs for usage reporting

### Session Deletion Request (SDR)
Terminates PFCP sessions when LI is no longer required.

## PDR (Packet Detection Rule) for LI

### LI Traffic Detection
```json
{
  "pdr_id": 1001,
  "precedence": 50,
  "pdi": {
    "source_interface": "access",
    "ue_ip_address": "192.168.1.100",
    "application_id": "li-target-app"
  },
  "outer_header_removal": "GTP-U/UDP/IPv4",
  "far_id": 2001,
  "urr_id": 3001
}
```

## FAR (Forwarding Action Rule) for LI

### LI Traffic Forwarding
```json
{
  "far_id": 2001,
  "apply_action": "FORW",
  "forwarding_parameters": {
    "destination_interface": "core",
    "network_instance": "li-network",
    "outer_header_creation": {
      "outer_header_creation_description": "GTP-U/UDP/IPv4",
      "teid": 0x12345678,
      "ipv4_address": "10.0.0.100"
    }
  }
}
```

## URR (Usage Reporting Rule) for LI

### LI Usage Reporting
```json
{
  "urr_id": 3001,
  "measurement_method": "VOLUME",
  "reporting_triggers": [
    "IMMER",
    "PERIO",
    "VOLTH"
  ],
  "measurement_period": 60,
  "volume_threshold": {
    "total_volume": 1000000,
    "uplink_volume": 500000,
    "downlink_volume": 500000
  }
}
```

## Error Handling

### Common PFCP Error Codes
- **100**: Invalid message format
- **101**: Invalid length
- **102**: Mandatory IE missing
- **103**: Conditional IE missing
- **104**: Invalid IE content
- **105**: Invalid IE length
- **106**: Invalid IE type
- **107**: Invalid IE value
- **108**: Invalid IE presence
- **109**: Invalid IE structure
- **110**: Invalid IE encoding

## Security Considerations

1. **Authentication**: PFCP messages must be authenticated
2. **Integrity**: Message integrity must be verified
3. **Confidentiality**: Sensitive LI data must be encrypted
4. **Authorization**: Only authorized entities can modify LI rules