#!/usr/bin/env python3
"""
3GPP Lawful Interception Code Generator
Generates code based on 3GPP specifications and user requirements
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional
from pathlib import Path

# Add code templates to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'code-templates'))

from pfcp_message_template import PFCPMessageBuilder, generate_li_pfcp_code
from li_message_template import LIMessageBuilder, generate_li_content_message, generate_li_iri_message

class LICodeGenerator:
    """Code generator for 3GPP Lawful Interception"""
    
    def __init__(self, output_dir: str = "generated_code"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_pfcp_session_establishment(self, config: Dict) -> str:
        """Generate PFCP session establishment code"""
        li_session_id = config.get("li_session_id", "li-session-001")
        target_imsi = config.get("target_imsi", "123456789012345")
        li_x2_endpoint = config.get("li_x2_endpoint", "https://li-x2.example.com:8080")
        li_x3_endpoint = config.get("li_x3_endpoint", "https://li-x3.example.com:8081")
        
        code = generate_li_pfcp_code(li_session_id, target_imsi, li_x2_endpoint, li_x3_endpoint)
        
        # Save to file
        output_file = self.output_dir / "pfcp_session_establishment.py"
        with open(output_file, 'w') as f:
            f.write(code)
        
        return str(output_file)
    
    def generate_li_content_message(self, config: Dict) -> str:
        """Generate LI content message code"""
        li_session_id = config.get("li_session_id", "li-session-001")
        target_imsi = config.get("target_imsi", "123456789012345")
        content_data = config.get("content_data", "Sample intercepted content")
        protocol = config.get("protocol", "HTTP")
        
        code = generate_li_content_message(li_session_id, target_imsi, content_data, protocol)
        
        # Save to file
        output_file = self.output_dir / "li_content_message.py"
        with open(output_file, 'w') as f:
            f.write(code)
        
        return str(output_file)
    
    def generate_li_iri_message(self, config: Dict) -> str:
        """Generate LI IRI message code"""
        li_session_id = config.get("li_session_id", "li-session-001")
        target_imsi = config.get("target_imsi", "123456789012345")
        event_type = config.get("event_type", "SESSION_ESTABLISHMENT")
        event_data = config.get("event_data", {
            "session_id": "session-001",
            "pdu_session_type": "IPv4",
            "dnn": "internet"
        })
        
        code = generate_li_iri_message(li_session_id, target_imsi, event_type, event_data)
        
        # Save to file
        output_file = self.output_dir / "li_iri_message.py"
        with open(output_file, 'w') as f:
            f.write(code)
        
        return str(output_file)
    
    def generate_complete_li_handler(self, config: Dict) -> str:
        """Generate complete LI handler implementation"""
        smf_id = config.get("smf_id", "smf-001")
        upf_id = config.get("upf_id", "upf-001")
        li_x2_endpoint = config.get("li_x2_endpoint", "https://li-x2.example.com:8080")
        li_x3_endpoint = config.get("li_x3_endpoint", "https://li-x3.example.com:8081")
        
        code = f'''#!/usr/bin/env python3
"""
Generated LI Handler Implementation
Generated from 3GPP specifications
"""

import asyncio
import json
import logging
from typing import Dict, Optional
from smf_upf_li_handler import SMFUPFLIHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeneratedLIHandler:
    """Generated LI Handler for {smf_id} and {upf_id}"""
    
    def __init__(self):
        self.li_handler = SMFUPFLIHandler("{smf_id}", "{upf_id}")
        self.li_x2_endpoint = "{li_x2_endpoint}"
        self.li_x3_endpoint = "{li_x3_endpoint}"
    
    async def initialize(self):
        """Initialize the LI handler"""
        await self.li_handler.initialize()
        logger.info("Generated LI Handler initialized")
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.li_handler.cleanup()
    
    async def create_li_session(self, target_imsi: str, target_msisdn: str = None, 
                               target_ip: str = None) -> Dict:
        """Create a new LI session"""
        li_session_id = f"li-session-{{int(time.time())}}"
        
        li_request = {{
            "li_session_id": li_session_id,
            "target_imsi": target_imsi,
            "target_msisdn": target_msisdn,
            "target_ip": target_ip,
            "li_x2_endpoint": self.li_x2_endpoint,
            "li_x3_endpoint": self.li_x3_endpoint,
            "encryption_key_id": "li-key-001"
        }}
        
        return await self.li_handler.create_li_session(li_request)
    
    async def handle_intercepted_content(self, li_session_id: str, content: str, 
                                       protocol: str = "HTTP", direction: str = "uplink"):
        """Handle intercepted content"""
        content_data = {{
            "li_session_id": li_session_id,
            "content": content,
            "content_type": "text",
            "protocol": protocol,
            "direction": direction
        }}
        
        await self.li_handler.handle_intercepted_content(content_data)
    
    def get_session_status(self, li_session_id: str) -> Optional[Dict]:
        """Get LI session status"""
        return self.li_handler.get_li_session_status(li_session_id)
    
    def list_sessions(self) -> List[Dict]:
        """List all LI sessions"""
        return self.li_handler.list_li_sessions()

async def main():
    """Example usage"""
    handler = GeneratedLIHandler()
    await handler.initialize()
    
    try:
        # Create LI session
        result = await handler.create_li_session(
            target_imsi="123456789012345",
            target_msisdn="+1234567890",
            target_ip="192.168.1.100"
        )
        
        print(f"LI Session Created: {{result}}")
        
        # Handle intercepted content
        if result.get("status") == "success":
            li_session_id = result.get("li_session_id")
            await handler.handle_intercepted_content(
                li_session_id=li_session_id,
                content="Sample intercepted HTTP request",
                protocol="HTTP",
                direction="uplink"
            )
        
        # Get session status
        status = handler.get_session_status(li_session_id)
        print(f"Session Status: {{status}}")
        
    finally:
        await handler.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        # Save to file
        output_file = self.output_dir / "generated_li_handler.py"
        with open(output_file, 'w') as f:
            f.write(code)
        
        return str(output_file)
    
    def generate_config_file(self, config: Dict) -> str:
        """Generate configuration file"""
        default_config = {
            "smf": {
                "id": config.get("smf_id", "smf-001"),
                "n4_interface": {
                    "ip": config.get("smf_ip", "10.0.0.10"),
                    "port": config.get("smf_port", 8805)
                }
            },
            "upf": {
                "id": config.get("upf_id", "upf-001"),
                "n4_interface": {
                    "ip": config.get("upf_ip", "10.0.0.20"),
                    "port": config.get("upf_port", 8805)
                }
            },
            "li_system": {
                "li_x2_endpoint": config.get("li_x2_endpoint", "https://li-x2.example.com:8080"),
                "li_x3_endpoint": config.get("li_x3_endpoint", "https://li-x3.example.com:8081"),
                "encryption_key_id": config.get("encryption_key_id", "li-key-001"),
                "certificate_path": config.get("certificate_path", "/path/to/li-cert.pem"),
                "private_key_path": config.get("private_key_path", "/path/to/li-key.pem")
            },
            "security": {
                "encryption_algorithm": config.get("encryption_algorithm", "AES-256-GCM"),
                "tls_version": config.get("tls_version", "1.3"),
                "certificate_validation": config.get("certificate_validation", True)
            }
        }
        
        # Save to file
        output_file = self.output_dir / "li_config.json"
        with open(output_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return str(output_file)
    
    def generate_test_file(self, config: Dict) -> str:
        """Generate test file"""
        code = f'''#!/usr/bin/env python3
"""
Generated Test File for LI Implementation
"""

import pytest
import asyncio
from generated_li_handler import GeneratedLIHandler

@pytest.fixture
def li_handler():
    return GeneratedLIHandler()

@pytest.mark.asyncio
async def test_create_li_session(li_handler):
    """Test LI session creation"""
    await li_handler.initialize()
    
    result = await li_handler.create_li_session(
        target_imsi="123456789012345",
        target_msisdn="+1234567890",
        target_ip="192.168.1.100"
    )
    
    assert result["status"] == "success"
    assert "li_session_id" in result
    
    await li_handler.cleanup()

@pytest.mark.asyncio
async def test_handle_intercepted_content(li_handler):
    """Test handling intercepted content"""
    await li_handler.initialize()
    
    # Create session first
    result = await li_handler.create_li_session(
        target_imsi="123456789012345"
    )
    
    if result["status"] == "success":
        li_session_id = result["li_session_id"]
        
        # Handle intercepted content
        await li_handler.handle_intercepted_content(
            li_session_id=li_session_id,
            content="Test intercepted content",
            protocol="HTTP",
            direction="uplink"
        )
        
        # Verify session status
        status = li_handler.get_session_status(li_session_id)
        assert status is not None
    
    await li_handler.cleanup()

@pytest.mark.asyncio
async def test_list_sessions(li_handler):
    """Test listing LI sessions"""
    await li_handler.initialize()
    
    # Create multiple sessions
    await li_handler.create_li_session(
        target_imsi="123456789012345"
    )
    await li_handler.create_li_session(
        target_imsi="123456789012346"
    )
    
    # List sessions
    sessions = li_handler.list_sessions()
    assert len(sessions) >= 2
    
    await li_handler.cleanup()

if __name__ == "__main__":
    pytest.main([__file__])
'''
        
        # Save to file
        output_file = self.output_dir / "test_generated_li_handler.py"
        with open(output_file, 'w') as f:
            f.write(code)
        
        return str(output_file)
    
    def generate_readme(self, config: Dict) -> str:
        """Generate README file"""
        readme_content = f'''# Generated 3GPP Lawful Interception Implementation

This directory contains generated code for 3GPP lawful interception based on the provided configuration.

## Generated Files

- `generated_li_handler.py` - Main LI handler implementation
- `pfcp_session_establishment.py` - PFCP session establishment code
- `li_content_message.py` - LI content message handling
- `li_iri_message.py` - LI IRI message handling
- `li_config.json` - Configuration file
- `test_generated_li_handler.py` - Test file

## Configuration

The generated code uses the following configuration:
- SMF ID: {config.get("smf_id", "smf-001")}
- UPF ID: {config.get("upf_id", "upf-001")}
- LI-X2 Endpoint: {config.get("li_x2_endpoint", "https://li-x2.example.com:8080")}
- LI-X3 Endpoint: {config.get("li_x3_endpoint", "https://li-x3.example.com:8081")}

## Usage

### Running the Generated Code

```bash
python generated_li_handler.py
```

### Running Tests

```bash
pytest test_generated_li_handler.py
```

### Using the LI Handler

```python
from generated_li_handler import GeneratedLIHandler

async def main():
    handler = GeneratedLIHandler()
    await handler.initialize()
    
    # Create LI session
    result = await handler.create_li_session(
        target_imsi="123456789012345",
        target_msisdn="+1234567890",
        target_ip="192.168.1.100"
    )
    
    print(f"LI Session Created: {{result}}")
    
    await handler.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## Dependencies

- Python 3.8+
- asyncio
- aiohttp
- pytest (for testing)

## Installation

```bash
pip install aiohttp pytest
```

## 3GPP Compliance

This generated code follows 3GPP specifications:
- TS 29.244: PFCP (Packet Forwarding Control Protocol)
- TS 33.126: Lawful Interception architecture

## Security

The generated code includes:
- Encryption support for LI data
- Secure communication channels
- Input validation
- Error handling

## Support

For questions or issues, refer to the 3GPP documentation in the parent directory.
'''
        
        # Save to file
        output_file = self.output_dir / "README.md"
        with open(output_file, 'w') as f:
            f.write(readme_content)
        
        return str(output_file)
    
    def generate_all(self, config: Dict) -> List[str]:
        """Generate all code files"""
        generated_files = []
        
        # Generate individual components
        generated_files.append(self.generate_pfcp_session_establishment(config))
        generated_files.append(self.generate_li_content_message(config))
        generated_files.append(self.generate_li_iri_message(config))
        
        # Generate complete implementation
        generated_files.append(self.generate_complete_li_handler(config))
        generated_files.append(self.generate_config_file(config))
        generated_files.append(self.generate_test_file(config))
        generated_files.append(self.generate_readme(config))
        
        return generated_files

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="3GPP Lawful Interception Code Generator")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--output", "-o", default="generated_code", help="Output directory")
    parser.add_argument("--smf-id", default="smf-001", help="SMF ID")
    parser.add_argument("--upf-id", default="upf-001", help="UPF ID")
    parser.add_argument("--li-x2-endpoint", default="https://li-x2.example.com:8080", help="LI-X2 endpoint")
    parser.add_argument("--li-x3-endpoint", default="https://li-x3.example.com:8081", help="LI-X3 endpoint")
    parser.add_argument("--target-imsi", default="123456789012345", help="Target IMSI")
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Override with command line arguments
    config.update({
        "smf_id": args.smf_id,
        "upf_id": args.upf_id,
        "li_x2_endpoint": args.li_x2_endpoint,
        "li_x3_endpoint": args.li_x3_endpoint,
        "target_imsi": args.target_imsi
    })
    
    # Generate code
    generator = LICodeGenerator(args.output)
    generated_files = generator.generate_all(config)
    
    print(f"Generated {len(generated_files)} files in {args.output}:")
    for file_path in generated_files:
        print(f"  - {file_path}")
    
    print(f"\nTo run the generated code:")
    print(f"  cd {args.output}")
    print(f"  python generated_li_handler.py")
    
    print(f"\nTo run tests:")
    print(f"  cd {args.output}")
    print(f"  pytest test_generated_li_handler.py")

if __name__ == "__main__":
    main()