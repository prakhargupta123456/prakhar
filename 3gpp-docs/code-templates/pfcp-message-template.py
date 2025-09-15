#!/usr/bin/env python3
"""
PFCP Message Template for Lawful Interception
Generated from 3GPP TS 29.244 specification
"""

import json
import struct
import time
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

class PFCPMessageType(Enum):
    """PFCP Message Types for Lawful Interception"""
    SESSION_ESTABLISHMENT_REQUEST = 50
    SESSION_ESTABLISHMENT_RESPONSE = 51
    SESSION_MODIFICATION_REQUEST = 52
    SESSION_MODIFICATION_RESPONSE = 53
    SESSION_DELETION_REQUEST = 54
    SESSION_DELETION_RESPONSE = 55
    SESSION_REPORT_REQUEST = 56
    SESSION_REPORT_RESPONSE = 57

class SourceInterface(Enum):
    """Source Interface Types"""
    ACCESS = 0
    CORE = 1
    SGI_LAN = 2
    CP_FUNCTION = 3
    VN_INTERNAL = 4

class DestinationInterface(Enum):
    """Destination Interface Types"""
    ACCESS = 0
    CORE = 1
    SGI_LAN = 2
    CP_FUNCTION = 3
    VN_INTERNAL = 4
    LI_X2 = 5  # For lawful interception content
    LI_X3 = 6  # For lawful interception IRI

@dataclass
class LIForwardingInfo:
    """Lawful Interception Forwarding Information"""
    li_session_id: str
    li_x2_endpoint: Optional[str] = None
    li_x3_endpoint: Optional[str] = None
    encryption_key_id: Optional[str] = None
    interception_scope: Optional[Dict[str, bool]] = None

@dataclass
class PDI:
    """Packet Detection Information"""
    source_interface: SourceInterface
    ue_ip_address: Optional[str] = None
    ue_ipv6_address: Optional[str] = None
    application_id: Optional[str] = None
    network_instance: Optional[str] = None

@dataclass
class OuterHeaderCreation:
    """Outer Header Creation Information"""
    outer_header_creation_description: str
    teid: Optional[str] = None
    ipv4_address: Optional[str] = None
    ipv6_address: Optional[str] = None
    port_number: Optional[int] = None

@dataclass
class ForwardingParameters:
    """Forwarding Action Rule Parameters"""
    destination_interface: DestinationInterface
    network_instance: Optional[str] = None
    outer_header_creation: Optional[OuterHeaderCreation] = None
    li_forwarding_info: Optional[LIForwardingInfo] = None

@dataclass
class FAR:
    """Forwarding Action Rule"""
    far_id: int
    apply_action: str  # DROP, FORW, BUFF, etc.
    forwarding_parameters: Optional[ForwardingParameters] = None

@dataclass
class PDR:
    """Packet Detection Rule"""
    pdr_id: int
    precedence: int
    pdi: PDI
    outer_header_removal: Optional[str] = None
    far_id: int
    urr_id: Optional[int] = None
    qer_id: Optional[int] = None

@dataclass
class VolumeThreshold:
    """Volume Threshold for Usage Reporting"""
    total_volume: Optional[int] = None
    uplink_volume: Optional[int] = None
    downlink_volume: Optional[int] = None

@dataclass
class LIUsageReporting:
    """Lawful Interception Usage Reporting Configuration"""
    li_session_id: str
    reporting_interval: int = 60
    include_packet_count: bool = True
    include_byte_count: bool = True
    include_timestamp: bool = True

@dataclass
class URR:
    """Usage Reporting Rule"""
    urr_id: int
    measurement_method: str  # DURAT, VOLUME, EVENT
    reporting_triggers: List[str]
    measurement_period: Optional[int] = None
    volume_threshold: Optional[VolumeThreshold] = None
    time_threshold: Optional[int] = None
    li_usage_reporting: Optional[LIUsageReporting] = None

@dataclass
class PFCPMessage:
    """PFCP Message Structure"""
    version: int = 1
    message_type: PFCPMessageType
    message_length: int = 0
    f_seid: str
    pfcp_session_id: int
    sequence_number: int
    ie_list: List[Dict] = None

    def __post_init__(self):
        if self.ie_list is None:
            self.ie_list = []

    def add_pdr(self, pdr: PDR) -> None:
        """Add a Packet Detection Rule to the message"""
        pdr_dict = asdict(pdr)
        pdr_dict['ie_type'] = 'Create PDR'
        self.ie_list.append(pdr_dict)

    def add_far(self, far: FAR) -> None:
        """Add a Forwarding Action Rule to the message"""
        far_dict = asdict(far)
        far_dict['ie_type'] = 'Create FAR'
        self.ie_list.append(far_dict)

    def add_urr(self, urr: URR) -> None:
        """Add a Usage Reporting Rule to the message"""
        urr_dict = asdict(urr)
        urr_dict['ie_type'] = 'Create URR'
        self.ie_list.append(urr_dict)

    def to_json(self) -> str:
        """Convert PFCP message to JSON"""
        message_dict = {
            'version': self.version,
            'message_type': self.message_type.name,
            'f_seid': self.f_seid,
            'pfcp_session_id': self.pfcp_session_id,
            'sequence_number': self.sequence_number,
            'ie_list': self.ie_list
        }
        return json.dumps(message_dict, indent=2)

class PFCPMessageBuilder:
    """Builder class for creating PFCP messages for lawful interception"""
    
    def __init__(self, f_seid: str, pfcp_session_id: int):
        self.f_seid = f_seid
        self.pfcp_session_id = pfcp_session_id
        self.sequence_number = int(time.time() * 1000) % 2**32

    def create_li_session_establishment(self, li_session_id: str, 
                                      target_imsi: str,
                                      li_x2_endpoint: str,
                                      li_x3_endpoint: str) -> PFCPMessage:
        """Create a PFCP Session Establishment Request for lawful interception"""
        
        message = PFCPMessage(
            message_type=PFCPMessageType.SESSION_ESTABLISHMENT_REQUEST,
            f_seid=self.f_seid,
            pfcp_session_id=self.pfcp_session_id,
            sequence_number=self.sequence_number
        )

        # Create PDR for LI traffic detection
        pdi = PDI(
            source_interface=SourceInterface.ACCESS,
            ue_ip_address="192.168.1.100",  # Target UE IP
            application_id=f"li-target-{target_imsi}",
            network_instance="internet"
        )

        pdr = PDR(
            pdr_id=1001,
            precedence=50,
            pdi=pdi,
            outer_header_removal="GTP-U/UDP/IPv4",
            far_id=2001,
            urr_id=3001
        )

        # Create FAR for LI traffic forwarding
        li_forwarding_info = LIForwardingInfo(
            li_session_id=li_session_id,
            li_x2_endpoint=li_x2_endpoint,
            li_x3_endpoint=li_x3_endpoint,
            encryption_key_id="li-key-001",
            interception_scope={
                "content_of_communications": True,
                "intercept_related_information": True,
                "location_information": True
            }
        )

        outer_header_creation = OuterHeaderCreation(
            outer_header_creation_description="UDP/IPv4",
            ipv4_address="10.0.0.100",
            port_number=8080
        )

        forwarding_params = ForwardingParameters(
            destination_interface=DestinationInterface.LI_X2,
            network_instance="li-network",
            outer_header_creation=outer_header_creation,
            li_forwarding_info=li_forwarding_info
        )

        far = FAR(
            far_id=2001,
            apply_action="FORW",
            forwarding_parameters=forwarding_params
        )

        # Create URR for LI usage reporting
        volume_threshold = VolumeThreshold(
            total_volume=1000000,  # 1MB threshold
            uplink_volume=500000,
            downlink_volume=500000
        )

        li_usage_reporting = LIUsageReporting(
            li_session_id=li_session_id,
            reporting_interval=60,
            include_packet_count=True,
            include_byte_count=True,
            include_timestamp=True
        )

        urr = URR(
            urr_id=3001,
            measurement_method="VOLUME",
            reporting_triggers=["IMMER", "PERIO", "VOLTH"],
            measurement_period=60,
            volume_threshold=volume_threshold,
            li_usage_reporting=li_usage_reporting
        )

        # Add IEs to message
        message.add_pdr(pdr)
        message.add_far(far)
        message.add_urr(urr)

        return message

    def create_li_session_modification(self, li_session_id: str,
                                     new_target_imsi: Optional[str] = None,
                                     update_li_endpoints: bool = False) -> PFCPMessage:
        """Create a PFCP Session Modification Request for LI updates"""
        
        message = PFCPMessage(
            message_type=PFCPMessageType.SESSION_MODIFICATION_REQUEST,
            f_seid=self.f_seid,
            pfcp_session_id=self.pfcp_session_id,
            sequence_number=self.sequence_number
        )

        # Update PDR if new target specified
        if new_target_imsi:
            pdi = PDI(
                source_interface=SourceInterface.ACCESS,
                ue_ip_address="192.168.1.101",  # New target UE IP
                application_id=f"li-target-{new_target_imsi}",
                network_instance="internet"
            )

            pdr = PDR(
                pdr_id=1001,
                precedence=50,
                pdi=pdi,
                outer_header_removal="GTP-U/UDP/IPv4",
                far_id=2001,
                urr_id=3001
            )

            pdr_dict = asdict(pdr)
            pdr_dict['ie_type'] = 'Update PDR'
            message.ie_list.append(pdr_dict)

        return message

    def create_li_session_deletion(self) -> PFCPMessage:
        """Create a PFCP Session Deletion Request for LI termination"""
        
        message = PFCPMessage(
            message_type=PFCPMessageType.SESSION_DELETION_REQUEST,
            f_seid=self.f_seid,
            pfcp_session_id=self.pfcp_session_id,
            sequence_number=self.sequence_number
        )

        return message

# Example usage and code generation functions
def generate_li_pfcp_code(li_session_id: str, target_imsi: str, 
                         li_x2_endpoint: str, li_x3_endpoint: str) -> str:
    """Generate Python code for LI PFCP message creation"""
    
    builder = PFCPMessageBuilder("0x1234567890abcdef", 12345)
    message = builder.create_li_session_establishment(
        li_session_id, target_imsi, li_x2_endpoint, li_x3_endpoint
    )
    
    return f"""
# Generated PFCP code for Lawful Interception
# LI Session ID: {li_session_id}
# Target IMSI: {target_imsi}

from pfcp_message_template import PFCPMessageBuilder

# Initialize PFCP message builder
builder = PFCPMessageBuilder("0x1234567890abcdef", 12345)

# Create LI session establishment message
message = builder.create_li_session_establishment(
    li_session_id="{li_session_id}",
    target_imsi="{target_imsi}",
    li_x2_endpoint="{li_x2_endpoint}",
    li_x3_endpoint="{li_x3_endpoint}"
)

# Convert to JSON for transmission
pfcp_json = message.to_json()
print(pfcp_json)
"""

if __name__ == "__main__":
    # Example usage
    builder = PFCPMessageBuilder("0x1234567890abcdef", 12345)
    
    # Create LI session establishment
    message = builder.create_li_session_establishment(
        li_session_id="li-session-12345",
        target_imsi="123456789012345",
        li_x2_endpoint="https://li-x2.example.com:8080",
        li_x3_endpoint="https://li-x3.example.com:8081"
    )
    
    print("PFCP Session Establishment Request for LI:")
    print(message.to_json())