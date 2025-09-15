# Quick Start Guide - 3GPP Lawful Interception

## Overview
This guide helps you quickly get started with generating 3GPP-compliant code for lawful interception between SMF and UPF using Cursor AI.

## Prerequisites
- Python 3.8 or higher
- Cursor AI editor
- Basic understanding of 5G network architecture

## Quick Setup

### 1. Install Dependencies
```bash
pip install aiohttp cryptography pytest
```

### 2. Generate Code Using Cursor AI

#### Option A: Use the Code Generator Tool
```bash
cd 3gpp-docs/tools
python code-generator.py --smf-id smf-001 --upf-id upf-001 --target-imsi 123456789012345
```

#### Option B: Use Cursor AI with Templates

1. **Open Cursor AI** in this workspace
2. **Ask Cursor AI** to generate PFCP messages:
   ```
   Generate a PFCP session establishment request for lawful interception with target IMSI 123456789012345
   ```

3. **Ask Cursor AI** to generate LI messages:
   ```
   Create a lawful interception content message for HTTP traffic from IMSI 123456789012345
   ```

4. **Ask Cursor AI** to create session management:
   ```
   Implement a complete SMF-UPF lawful interception handler with session lifecycle management
   ```

### 3. Run Generated Code

```bash
cd generated_code
python generated_li_handler.py
```

## Example Prompts for Cursor AI

### Generate PFCP Messages
```
Using the 3GPP templates, create a PFCP session establishment request for lawful interception with:
- Target IMSI: 123456789012345
- LI-X2 endpoint: https://li-x2.example.com:8080
- LI-X3 endpoint: https://li-x3.example.com:8081
- Encryption key: li-key-001
```

### Generate LI Content Messages
```
Create a lawful interception content message for intercepted HTTP traffic with:
- Target IMSI: 123456789012345
- Content: "GET /api/data HTTP/1.1"
- Protocol: HTTP
- Direction: uplink
```

### Generate LI IRI Messages
```
Create an intercept related information message for session establishment with:
- Target IMSI: 123456789012345
- Event: Session Establishment
- PDU session type: IPv4
- DNN: internet
```

### Generate Complete Implementation
```
Implement a complete lawful interception system with:
- SMF-UPF communication using PFCP
- LI message handling (LI-X2 and LI-X3)
- Session lifecycle management
- Error handling and logging
- Security and encryption
```

## Configuration

### Basic Configuration
Create `config.json`:
```json
{
  "smf_id": "smf-001",
  "upf_id": "upf-001",
  "li_x2_endpoint": "https://li-x2.example.com:8080",
  "li_x3_endpoint": "https://li-x3.example.com:8081",
  "encryption_key_id": "li-key-001"
}
```

### Advanced Configuration
```json
{
  "smf": {
    "id": "smf-001",
    "n4_interface": {
      "ip": "10.0.0.10",
      "port": 8805
    }
  },
  "upf": {
    "id": "upf-001",
    "n4_interface": {
      "ip": "10.0.0.20",
      "port": 8805
    }
  },
  "li_system": {
    "li_x2_endpoint": "https://li-x2.example.com:8080",
    "li_x3_endpoint": "https://li-x3.example.com:8081",
    "encryption_key_id": "li-key-001",
    "certificate_path": "/path/to/li-cert.pem",
    "private_key_path": "/path/to/li-key.pem"
  },
  "security": {
    "encryption_algorithm": "AES-256-GCM",
    "tls_version": "1.3",
    "certificate_validation": true
  }
}
```

## Testing

### Run Unit Tests
```bash
pytest test_generated_li_handler.py -v
```

### Run Integration Tests
```bash
pytest tests/test_integration.py -v
```

### Manual Testing
```python
import asyncio
from generated_li_handler import GeneratedLIHandler

async def test_li_session():
    handler = GeneratedLIHandler()
    await handler.initialize()
    
    # Create LI session
    result = await handler.create_li_session(
        target_imsi="123456789012345",
        target_msisdn="+1234567890",
        target_ip="192.168.1.100"
    )
    
    print(f"LI Session Created: {result}")
    await handler.cleanup()

asyncio.run(test_li_session())
```

## Common Use Cases

### 1. Basic LI Session Creation
```python
# Ask Cursor AI: "Create a basic LI session with target IMSI 123456789012345"
```

### 2. Traffic Interception
```python
# Ask Cursor AI: "Implement traffic interception for HTTP and SMS protocols"
```

### 3. Session Modification
```python
# Ask Cursor AI: "Add session modification capabilities for changing LI targets"
```

### 4. Error Handling
```python
# Ask Cursor AI: "Implement comprehensive error handling for LI operations"
```

### 5. Security Implementation
```python
# Ask Cursor AI: "Add encryption and security features for LI data"
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path includes code templates

2. **Configuration Errors**
   - Verify JSON configuration format
   - Check endpoint URLs are accessible

3. **Network Errors**
   - Verify LI endpoints are reachable
   - Check firewall settings

4. **Authentication Errors**
   - Verify certificates are valid
   - Check encryption keys

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

1. **Customize Templates**: Modify the code templates for your specific requirements
2. **Add Features**: Extend the implementation with additional LI capabilities
3. **Integration**: Integrate with your existing 5G network infrastructure
4. **Testing**: Implement comprehensive testing for production deployment
5. **Monitoring**: Add monitoring and logging for operational visibility

## Support

- **Documentation**: Check `3gpp-docs/specifications/` for detailed 3GPP specifications
- **Examples**: See `3gpp-docs/examples/` for implementation examples
- **Templates**: Use `3gpp-docs/code-templates/` for code generation
- **Tools**: Use `3gpp-docs/tools/` for automated code generation

## Cursor AI Tips

1. **Be Specific**: Provide detailed requirements when asking Cursor AI to generate code
2. **Use Context**: Reference the 3GPP documentation when asking for compliance
3. **Iterate**: Start with basic functionality and ask for enhancements
4. **Test**: Always test generated code before production use
5. **Customize**: Modify generated code to fit your specific needs