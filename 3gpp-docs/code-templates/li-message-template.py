#!/usr/bin/env python3
"""
Lawful Interception Message Template
Generated from 3GPP TS 33.126 specification
"""

import json
import time
import hashlib
import base64
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone

class LIMessageType(Enum):
    """Lawful Interception Message Types"""
    CONTENT_OF_COMMUNICATIONS = "Content of Communications"
    INTERCEPT_RELATED_INFORMATION = "Intercept Related Information"
    LI_SESSION_ESTABLISHMENT = "LI Session Establishment"
    LI_SESSION_MODIFICATION = "LI Session Modification"
    LI_SESSION_TERMINATION = "LI Session Termination"
    LI_STATUS_REPORT = "LI Status Report"
    LI_ERROR_REPORT = "LI Error Report"

class ContentType(Enum):
    """Content Types for Communications"""
    TEXT = "text"
    BINARY = "binary"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    APPLICATION = "application"

class Protocol(Enum):
    """Communication Protocols"""
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    SIP = "SIP"
    RTP = "RTP"
    SMS = "SMS"
    MMS = "MMS"
    FTP = "FTP"
    SMTP = "SMTP"
    IMAP = "IMAP"
    POP3 = "POP3"
    DNS = "DNS"
    DHCP = "DHCP"
    ICMP = "ICMP"
    TCP = "TCP"
    UDP = "UDP"

class EventType(Enum):
    """Intercept Related Information Event Types"""
    SESSION_ESTABLISHMENT = "Session Establishment"
    SESSION_RELEASE = "Session Release"
    SESSION_MODIFICATION = "Session Modification"
    LOCATION_UPDATE = "Location Update"
    SERVICE_REQUEST = "Service Request"
    AUTHENTICATION = "Authentication"
    REGISTRATION = "Registration"
    DEREGISTRATION = "Deregistration"
    HANDOVER = "Handover"
    CHARGING_EVENT = "Charging Event"
    ERROR_EVENT = "Error Event"

@dataclass
class TargetIdentity:
    """Target Identity Information"""
    imsi: Optional[str] = None
    msisdn: Optional[str] = None
    ip_address: Optional[str] = None
    ipv6_address: Optional[str] = None
    imei: Optional[str] = None
    supi: Optional[str] = None

@dataclass
class EncryptionInfo:
    """Encryption Information"""
    encryption_algorithm: str = "AES-256-GCM"
    key_id: str = ""
    initialization_vector: Optional[str] = None
    authentication_tag: Optional[str] = None

@dataclass
class CommunicationContent:
    """Communication Content Structure"""
    content_type: ContentType
    content_encoding: str = "base64"
    content_data: str = ""
    content_size: int = 0
    content_hash: Optional[str] = None

    def __post_init__(self):
        if self.content_data and not self.content_hash:
            self.content_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate SHA-256 hash of content"""
        content_bytes = base64.b64decode(self.content_data) if self.content_encoding == "base64" else self.content_data.encode()
        return hashlib.sha256(content_bytes).hexdigest()

@dataclass
class SessionInfo:
    """Session Information"""
    session_id: str
    pdu_session_type: str = "IPv4"
    dnn: str = "internet"
    sst: int = 1
    sd: str = "000001"
    qfi: int = 1

@dataclass
class LocationInformation:
    """Location Information"""
    tai: Optional[str] = None
    ecgi: Optional[str] = None
    ncgi: Optional[str] = None
    location_timestamp: Optional[str] = None
    location_accuracy: Optional[float] = None
    location_source: Optional[str] = None

@dataclass
class ServiceInformation:
    """Service Information"""
    service_type: str = "Data"
    service_status: str = "Active"
    qos_parameters: Optional[Dict] = None
    charging_information: Optional[Dict] = None

@dataclass
class LIStatistics:
    """LI Statistics"""
    messages_sent: int = 0
    bytes_sent: int = 0
    messages_failed: int = 0
    last_activity: Optional[str] = None
    uptime: int = 0

@dataclass
class ErrorInfo:
    """Error Information"""
    error_code: str
    error_message: str
    error_timestamp: str
    retry_after: Optional[int] = None
    error_details: Optional[Dict] = None

@dataclass
class LIMessage:
    """Base Lawful Interception Message"""
    message_type: LIMessageType
    li_session_id: str
    timestamp: str
    target_identity: TargetIdentity
    message_sequence: int = 1
    encryption_info: Optional[EncryptionInfo] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

@dataclass
class ContentOfCommunications(LIMessage):
    """Content of Communications Message (LI-X2)"""
    content: CommunicationContent
    direction: str  # uplink, downlink, bidirectional
    protocol: Protocol
    session_info: Optional[SessionInfo] = None

@dataclass
class InterceptRelatedInformation(LIMessage):
    """Intercept Related Information Message (LI-X3)"""
    event_type: EventType
    event_data: Dict
    location_information: Optional[LocationInformation] = None
    service_information: Optional[ServiceInformation] = None

@dataclass
class LIStatusReport(LIMessage):
    """LI Status Report Message"""
    status: str  # Active, Inactive, Error, Suspended, Terminated
    status_reason: Optional[str] = None
    statistics: Optional[LIStatistics] = None
    error_info: Optional[ErrorInfo] = None

class LIMessageBuilder:
    """Builder class for creating LI messages"""
    
    def __init__(self, li_session_id: str):
        self.li_session_id = li_session_id
        self.message_sequence = 1

    def create_content_message(self, target_identity: TargetIdentity,
                             content_data: str, content_type: ContentType,
                             protocol: Protocol, direction: str,
                             session_info: Optional[SessionInfo] = None) -> ContentOfCommunications:
        """Create a Content of Communications message"""
        
        content = CommunicationContent(
            content_type=content_type,
            content_encoding="base64",
            content_data=base64.b64encode(content_data.encode()).decode(),
            content_size=len(content_data)
        )

        message = ContentOfCommunications(
            message_type=LIMessageType.CONTENT_OF_COMMUNICATIONS,
            li_session_id=self.li_session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            target_identity=target_identity,
            message_sequence=self.message_sequence,
            content=content,
            direction=direction,
            protocol=protocol,
            session_info=session_info
        )

        self.message_sequence += 1
        return message

    def create_iri_message(self, target_identity: TargetIdentity,
                          event_type: EventType, event_data: Dict,
                          location_information: Optional[LocationInformation] = None,
                          service_information: Optional[ServiceInformation] = None) -> InterceptRelatedInformation:
        """Create an Intercept Related Information message"""
        
        message = InterceptRelatedInformation(
            message_type=LIMessageType.INTERCEPT_RELATED_INFORMATION,
            li_session_id=self.li_session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            target_identity=target_identity,
            message_sequence=self.message_sequence,
            event_type=event_type,
            event_data=event_data,
            location_information=location_information,
            service_information=service_information
        )

        self.message_sequence += 1
        return message

    def create_status_report(self, target_identity: TargetIdentity,
                           status: str, status_reason: Optional[str] = None,
                           statistics: Optional[LIStatistics] = None,
                           error_info: Optional[ErrorInfo] = None) -> LIStatusReport:
        """Create a LI Status Report message"""
        
        message = LIStatusReport(
            message_type=LIMessageType.LI_STATUS_REPORT,
            li_session_id=self.li_session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            target_identity=target_identity,
            message_sequence=self.message_sequence,
            status=status,
            status_reason=status_reason,
            statistics=statistics,
            error_info=error_info
        )

        self.message_sequence += 1
        return message

    def to_json(self, message: LIMessage) -> str:
        """Convert LI message to JSON"""
        message_dict = asdict(message)
        
        # Convert enums to strings
        if 'message_type' in message_dict:
            message_dict['message_type'] = message_dict['message_type'].value
        if 'content' in message_dict and 'content_type' in message_dict['content']:
            message_dict['content']['content_type'] = message_dict['content']['content_type'].value
        if 'protocol' in message_dict:
            message_dict['protocol'] = message_dict['protocol'].value
        if 'event_type' in message_dict:
            message_dict['event_type'] = message_dict['event_type'].value
        
        return json.dumps(message_dict, indent=2)

# Example usage and code generation functions
def generate_li_content_message(li_session_id: str, target_imsi: str,
                              content_data: str, protocol: str) -> str:
    """Generate Python code for LI content message creation"""
    
    builder = LIMessageBuilder(li_session_id)
    target_identity = TargetIdentity(imsi=target_imsi)
    
    message = builder.create_content_message(
        target_identity=target_identity,
        content_data=content_data,
        content_type=ContentType.TEXT,
        protocol=Protocol(protocol),
        direction="uplink"
    )
    
    return f"""
# Generated LI Content Message
# LI Session ID: {li_session_id}
# Target IMSI: {target_imsi}

from li_message_template import LIMessageBuilder, TargetIdentity, ContentType, Protocol

# Initialize LI message builder
builder = LIMessageBuilder("{li_session_id}")

# Create target identity
target_identity = TargetIdentity(imsi="{target_imsi}")

# Create content message
message = builder.create_content_message(
    target_identity=target_identity,
    content_data="{content_data}",
    content_type=ContentType.TEXT,
    protocol=Protocol.{protocol},
    direction="uplink"
)

# Convert to JSON for transmission
li_json = builder.to_json(message)
print(li_json)
"""

def generate_li_iri_message(li_session_id: str, target_imsi: str,
                           event_type: str, event_data: Dict) -> str:
    """Generate Python code for LI IRI message creation"""
    
    builder = LIMessageBuilder(li_session_id)
    target_identity = TargetIdentity(imsi=target_imsi)
    
    message = builder.create_iri_message(
        target_identity=target_identity,
        event_type=EventType(event_type),
        event_data=event_data
    )
    
    return f"""
# Generated LI IRI Message
# LI Session ID: {li_session_id}
# Target IMSI: {target_imsi}

from li_message_template import LIMessageBuilder, TargetIdentity, EventType

# Initialize LI message builder
builder = LIMessageBuilder("{li_session_id}")

# Create target identity
target_identity = TargetIdentity(imsi="{target_imsi}")

# Create IRI message
message = builder.create_iri_message(
    target_identity=target_identity,
    event_type=EventType.{event_type},
    event_data={json.dumps(event_data, indent=4)}
)

# Convert to JSON for transmission
li_json = builder.to_json(message)
print(li_json)
"""

if __name__ == "__main__":
    # Example usage
    builder = LIMessageBuilder("li-session-12345")
    
    # Create target identity
    target_identity = TargetIdentity(
        imsi="123456789012345",
        msisdn="+1234567890",
        ip_address="192.168.1.100"
    )
    
    # Create content message
    content_message = builder.create_content_message(
        target_identity=target_identity,
        content_data="Hello, this is intercepted content",
        content_type=ContentType.TEXT,
        protocol=Protocol.HTTP,
        direction="uplink"
    )
    
    print("LI Content Message:")
    print(builder.to_json(content_message))
    
    # Create IRI message
    iri_message = builder.create_iri_message(
        target_identity=target_identity,
        event_type=EventType.SESSION_ESTABLISHMENT,
        event_data={
            "session_id": "session-67890",
            "pdu_session_type": "IPv4",
            "dnn": "internet"
        }
    )
    
    print("\nLI IRI Message:")
    print(builder.to_json(iri_message))