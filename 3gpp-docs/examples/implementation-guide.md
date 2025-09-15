# 3GPP Lawful Interception Implementation Guide

## Overview
This guide provides step-by-step instructions for implementing lawful interception interfaces between SMF and UPF using the provided 3GPP templates and documentation.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- asyncio support
- aiohttp library for HTTP communication
- SSL/TLS support for secure communication

### Dependencies
```bash
pip install aiohttp
pip install cryptography
```

## Implementation Steps

### 1. Environment Setup

#### 1.1 Create Project Structure
```
project/
├── 3gpp-docs/              # 3GPP documentation
├── src/                    # Source code
│   ├── smf/               # SMF implementation
│   ├── upf/               # UPF implementation
│   └── li/                # LI system integration
├── config/                 # Configuration files
├── tests/                  # Test files
└── docs/                   # Additional documentation
```

#### 1.2 Configuration Files
Create `config/li_config.json`:
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

### 2. SMF Implementation

#### 2.1 SMF LI Handler
Create `src/smf/li_handler.py`:
```python
import asyncio
import json
from typing import Dict, Optional
from smf_upf_li_handler import SMFUPFLIHandler

class SMFLIHandler:
    def __init__(self, config: Dict):
        self.config = config
        self.li_handler = SMFUPFLIHandler(
            config["smf"]["id"],
            config["upf"]["id"]
        )
    
    async def initialize(self):
        await self.li_handler.initialize()
    
    async def handle_li_request(self, request: Dict) -> Dict:
        """Handle LI request from LI-ADMF"""
        li_session_id = request.get("li_session_id")
        target_identity = request.get("target_identity")
        
        # Create LI session
        li_request = {
            "li_session_id": li_session_id,
            "target_imsi": target_identity.get("imsi"),
            "target_msisdn": target_identity.get("msisdn"),
            "target_ip": target_identity.get("ip_address"),
            "li_x2_endpoint": self.config["li_system"]["li_x2_endpoint"],
            "li_x3_endpoint": self.config["li_system"]["li_x3_endpoint"],
            "encryption_key_id": self.config["li_system"]["encryption_key_id"]
        }
        
        return await self.li_handler.create_li_session(li_request)
```

#### 2.2 SMF Session Management
Create `src/smf/session_manager.py`:
```python
import asyncio
from typing import Dict, Optional
from pfcp_message_template import PFCPMessageBuilder

class SMFSessionManager:
    def __init__(self, config: Dict):
        self.config = config
        self.sessions = {}
        self.pfcp_builder = PFCPMessageBuilder("0x1234567890abcdef", 12345)
    
    async def create_session_with_li(self, session_data: Dict, li_session_id: Optional[str] = None):
        """Create PDU session with LI support"""
        session_id = session_data.get("session_id")
        
        # Create standard session
        # ... standard session creation logic ...
        
        # Add LI support if requested
        if li_session_id:
            await self._add_li_support(session_id, li_session_id)
        
        return {"status": "success", "session_id": session_id}
    
    async def _add_li_support(self, session_id: str, li_session_id: str):
        """Add LI support to existing session"""
        # Create PFCP message for LI
        pfcp_message = self.pfcp_builder.create_li_session_establishment(
            li_session_id=li_session_id,
            target_imsi=session_id,  # Use session ID as target
            li_x2_endpoint=self.config["li_system"]["li_x2_endpoint"],
            li_x3_endpoint=self.config["li_system"]["li_x3_endpoint"]
        )
        
        # Send to UPF
        await self._send_pfcp_message(pfcp_message)
```

### 3. UPF Implementation

#### 3.1 UPF LI Handler
Create `src/upf/li_handler.py`:
```python
import asyncio
import json
from typing import Dict, List
from li_message_template import LIMessageBuilder, TargetIdentity, ContentType, Protocol

class UPFLIHandler:
    def __init__(self, config: Dict):
        self.config = config
        self.li_sessions = {}
        self.li_builder = LIMessageBuilder("li-session-12345")
    
    async def handle_pfcp_li_request(self, pfcp_message: Dict):
        """Handle PFCP LI request from SMF"""
        # Parse PFCP message
        # Extract LI parameters
        # Configure traffic steering for LI
        
        li_session_id = pfcp_message.get("li_session_id")
        if li_session_id:
            self.li_sessions[li_session_id] = {
                "status": "active",
                "target_identity": pfcp_message.get("target_identity"),
                "li_x2_endpoint": pfcp_message.get("li_x2_endpoint"),
                "li_x3_endpoint": pfcp_message.get("li_x3_endpoint")
            }
    
    async def intercept_traffic(self, packet_data: Dict):
        """Intercept and forward traffic for LI"""
        for li_session_id, session_info in self.li_sessions.items():
            if session_info["status"] == "active":
                # Check if packet matches LI criteria
                if self._matches_li_criteria(packet_data, session_info):
                    await self._forward_to_li(packet_data, session_info)
    
    def _matches_li_criteria(self, packet_data: Dict, session_info: Dict) -> bool:
        """Check if packet matches LI criteria"""
        # Implement packet matching logic
        # Check target IP, protocol, etc.
        return True
    
    async def _forward_to_li(self, packet_data: Dict, session_info: Dict):
        """Forward intercepted data to LI system"""
        # Create LI content message
        target_identity = TargetIdentity(
            ip_address=packet_data.get("source_ip")
        )
        
        content_message = self.li_builder.create_content_message(
            target_identity=target_identity,
            content_data=packet_data.get("payload", ""),
            content_type=ContentType.TEXT,
            protocol=Protocol.HTTP,
            direction=packet_data.get("direction", "uplink")
        )
        
        # Send to LI-X2 endpoint
        await self._send_li_message(session_info["li_x2_endpoint"], content_message)
```

### 4. LI System Integration

#### 4.1 LI Message Handler
Create `src/li/message_handler.py`:
```python
import asyncio
import json
from typing import Dict
from aiohttp import web

class LIMessageHandler:
    def __init__(self, config: Dict):
        self.config = config
    
    async def handle_li_x2_message(self, request):
        """Handle LI-X2 content messages"""
        data = await request.json()
        
        # Process content message
        li_session_id = data.get("li_session_id")
        content = data.get("content", {})
        
        # Store or process content
        await self._process_content(li_session_id, content)
        
        return web.json_response({"status": "success"})
    
    async def handle_li_x3_message(self, request):
        """Handle LI-X3 IRI messages"""
        data = await request.json()
        
        # Process IRI message
        li_session_id = data.get("li_session_id")
        event_data = data.get("event_data", {})
        
        # Store or process IRI
        await self._process_iri(li_session_id, event_data)
        
        return web.json_response({"status": "success"})
    
    async def _process_content(self, li_session_id: str, content: Dict):
        """Process intercepted content"""
        # Implement content processing logic
        print(f"Processing content for LI session {li_session_id}")
    
    async def _process_iri(self, li_session_id: str, event_data: Dict):
        """Process intercept related information"""
        # Implement IRI processing logic
        print(f"Processing IRI for LI session {li_session_id}")
```

### 5. Testing Implementation

#### 5.1 Unit Tests
Create `tests/test_li_handler.py`:
```python
import pytest
import asyncio
from src.smf.li_handler import SMFLIHandler

@pytest.fixture
def config():
    return {
        "smf": {"id": "smf-test"},
        "upf": {"id": "upf-test"},
        "li_system": {
            "li_x2_endpoint": "https://test-li-x2.com:8080",
            "li_x3_endpoint": "https://test-li-x3.com:8081"
        }
    }

@pytest.mark.asyncio
async def test_create_li_session(config):
    handler = SMFLIHandler(config)
    await handler.initialize()
    
    request = {
        "li_session_id": "li-session-test",
        "target_identity": {
            "imsi": "123456789012345",
            "ip_address": "192.168.1.100"
        }
    }
    
    result = await handler.handle_li_request(request)
    assert result["status"] == "success"
    assert result["li_session_id"] == "li-session-test"
```

#### 5.2 Integration Tests
Create `tests/test_integration.py`:
```python
import pytest
import asyncio
from src.smf.li_handler import SMFLIHandler
from src.upf.li_handler import UPFLIHandler

@pytest.mark.asyncio
async def test_smf_upf_li_integration():
    # Test SMF-UPF LI communication
    smf_handler = SMFLIHandler(config)
    upf_handler = UPFLIHandler(config)
    
    await smf_handler.initialize()
    await upf_handler.initialize()
    
    # Create LI session
    li_request = {
        "li_session_id": "li-session-integration-test",
        "target_identity": {
            "imsi": "123456789012345",
            "ip_address": "192.168.1.100"
        }
    }
    
    result = await smf_handler.handle_li_request(li_request)
    assert result["status"] == "success"
    
    # Verify UPF received LI configuration
    assert "li-session-integration-test" in upf_handler.li_sessions
```

### 6. Deployment

#### 6.1 Docker Configuration
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

CMD ["python", "-m", "src.main"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  smf:
    build: .
    ports:
      - "8080:8080"
    environment:
      - CONFIG_PATH=/app/config/li_config.json
    volumes:
      - ./config:/app/config
  
  upf:
    build: .
    ports:
      - "8081:8081"
    environment:
      - CONFIG_PATH=/app/config/li_config.json
    volumes:
      - ./config:/app/config
  
  li-system:
    build: .
    ports:
      - "8082:8082"
    environment:
      - CONFIG_PATH=/app/config/li_config.json
    volumes:
      - ./config:/app/config
```

#### 6.2 Kubernetes Configuration
Create `k8s/smf-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smf-li
spec:
  replicas: 3
  selector:
    matchLabels:
      app: smf-li
  template:
    metadata:
      labels:
        app: smf-li
    spec:
      containers:
      - name: smf-li
        image: smf-li:latest
        ports:
        - containerPort: 8080
        env:
        - name: CONFIG_PATH
          value: "/app/config/li_config.json"
        volumeMounts:
        - name: config
          mountPath: /app/config
      volumes:
      - name: config
        configMap:
          name: li-config
```

### 7. Monitoring and Logging

#### 7.1 Logging Configuration
Create `config/logging.yaml`:
```yaml
version: 1
formatters:
  standard:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
  file:
    class: logging.FileHandler
    filename: /var/log/li-system.log
    level: DEBUG
    formatter: detailed

loggers:
  li_system:
    level: DEBUG
    handlers: [console, file]
    propagate: no
  smf_li:
    level: INFO
    handlers: [console, file]
    propagate: no
  upf_li:
    level: INFO
    handlers: [console, file]
    propagate: no
```

#### 7.2 Metrics Collection
Create `src/monitoring/metrics.py`:
```python
import time
from typing import Dict

class LIMetrics:
    def __init__(self):
        self.metrics = {
            "li_sessions_created": 0,
            "li_sessions_terminated": 0,
            "messages_sent": 0,
            "messages_failed": 0,
            "bytes_intercepted": 0
        }
    
    def increment_metric(self, metric_name: str, value: int = 1):
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
    
    def get_metrics(self) -> Dict:
        return self.metrics.copy()
```

### 8. Security Implementation

#### 8.1 Encryption Implementation
Create `src/security/encryption.py`:
```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class LIEncryption:
    def __init__(self, password: str, salt: bytes = None):
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.cipher = Fernet(key)
        self.salt = salt
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

### 9. Performance Optimization

#### 9.1 Connection Pooling
Create `src/network/connection_pool.py`:
```python
import aiohttp
import asyncio
from typing import Dict

class ConnectionPool:
    def __init__(self, max_connections: int = 100):
        self.max_connections = max_connections
        self.connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=10
        )
        self.session = None
    
    async def initialize(self):
        self.session = aiohttp.ClientSession(connector=self.connector)
    
    async def cleanup(self):
        if self.session:
            await self.session.close()
    
    async def post(self, url: str, data: Dict) -> Dict:
        if not self.session:
            await self.initialize()
        
        async with self.session.post(url, json=data) as response:
            return await response.json()
```

### 10. Troubleshooting

#### 10.1 Common Issues
1. **PFCP Message Format Errors**: Check message structure against TS 29.244
2. **LI Message Validation Failures**: Verify target identity format
3. **Encryption/Decryption Errors**: Check key management
4. **Network Connectivity Issues**: Verify endpoint URLs and certificates
5. **Session State Inconsistencies**: Implement proper state management

#### 10.2 Debug Tools
Create `tools/debug_li.py`:
```python
#!/usr/bin/env python3
"""
LI System Debug Tool
"""

import json
import asyncio
from src.smf.li_handler import SMFLIHandler

async def debug_li_session(li_session_id: str):
    """Debug specific LI session"""
    handler = SMFLIHandler(config)
    await handler.initialize()
    
    status = handler.li_handler.get_li_session_status(li_session_id)
    print(f"LI Session Status: {json.dumps(status, indent=2)}")
    
    sessions = handler.li_handler.list_li_sessions()
    print(f"All Sessions: {json.dumps(sessions, indent=2)}")

if __name__ == "__main__":
    import sys
    li_session_id = sys.argv[1] if len(sys.argv) > 1 else "li-session-001"
    asyncio.run(debug_li_session(li_session_id))
```

## Conclusion

This implementation guide provides a comprehensive approach to implementing 3GPP lawful interception interfaces. The modular design allows for easy testing, deployment, and maintenance while ensuring compliance with 3GPP standards and security requirements.

For additional support and examples, refer to the documentation in the `3gpp-docs/` directory and the provided code templates.