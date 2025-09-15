#!/usr/bin/env python3
"""
Lawful Interception Session Example
Demonstrates how to create and manage LI sessions using the 3GPP templates
"""

import asyncio
import json
import time
from typing import Dict, List

# Import our templates
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'code-templates'))

from pfcp_message_template import PFCPMessageBuilder, PFCPMessageType
from li_message_template import LIMessageBuilder, LIMessageType, TargetIdentity, ContentType, Protocol, EventType
from smf_upf_li_handler import SMFUPFLIHandler

class LISessionExample:
    """Example implementation of lawful interception session management"""
    
    def __init__(self):
        self.li_handler = None
        self.pfcp_builder = PFCPMessageBuilder("0x1234567890abcdef", 12345)
        self.li_builder = LIMessageBuilder("li-session-12345")
        
    async def initialize(self):
        """Initialize the example"""
        self.li_handler = SMFUPFLIHandler("smf-example", "upf-example")
        await self.li_handler.initialize()
        print("LI Session Example initialized")

    async def cleanup(self):
        """Cleanup resources"""
        if self.li_handler:
            await self.li_handler.cleanup()

    async def example_create_li_session(self):
        """Example: Create a new lawful interception session"""
        print("\n=== Creating LI Session ===")
        
        # LI session request
        li_request = {
            "li_session_id": "li-session-001",
            "target_imsi": "123456789012345",
            "target_msisdn": "+1234567890",
            "target_ip": "192.168.1.100",
            "li_x2_endpoint": "https://li-x2.example.com:8080",
            "li_x3_endpoint": "https://li-x3.example.com:8081",
            "encryption_key_id": "li-key-001",
            "interception_scope": {
                "content_of_communications": True,
                "intercept_related_information": True,
                "location_information": True
            }
        }
        
        # Create LI session
        result = await self.li_handler.create_li_session(li_request)
        print(f"LI Session Creation Result: {json.dumps(result, indent=2)}")
        
        return result.get("li_session_id")

    async def example_modify_li_session(self, li_session_id: str):
        """Example: Modify an existing LI session"""
        print(f"\n=== Modifying LI Session: {li_session_id} ===")
        
        # Modification request
        modifications = {
            "new_target_imsi": "123456789012346",  # Change target
            "update_li_endpoints": True
        }
        
        result = await self.li_handler.modify_li_session(li_session_id, modifications)
        print(f"LI Session Modification Result: {json.dumps(result, indent=2)}")

    async def example_handle_intercepted_content(self, li_session_id: str):
        """Example: Handle intercepted content"""
        print(f"\n=== Handling Intercepted Content for: {li_session_id} ===")
        
        # Simulate intercepted content from UPF
        content_data = {
            "li_session_id": li_session_id,
            "content": "This is intercepted HTTP request data",
            "content_type": "text",
            "protocol": "HTTP",
            "direction": "uplink",
            "timestamp": time.time()
        }
        
        await self.li_handler.handle_intercepted_content(content_data)
        print("Intercepted content processed")

    async def example_create_pfcp_messages(self):
        """Example: Create PFCP messages for LI"""
        print("\n=== Creating PFCP Messages ===")
        
        # Create session establishment request
        pfcp_message = self.pfcp_builder.create_li_session_establishment(
            li_session_id="li-session-002",
            target_imsi="123456789012347",
            li_x2_endpoint="https://li-x2.example.com:8080",
            li_x3_endpoint="https://li-x3.example.com:8081"
        )
        
        print("PFCP Session Establishment Request:")
        print(pfcp_message.to_json())
        
        # Create session modification request
        mod_message = self.pfcp_builder.create_li_session_modification(
            li_session_id="li-session-002",
            new_target_imsi="123456789012348"
        )
        
        print("\nPFCP Session Modification Request:")
        print(mod_message.to_json())

    async def example_create_li_messages(self):
        """Example: Create LI messages"""
        print("\n=== Creating LI Messages ===")
        
        # Create target identity
        target_identity = TargetIdentity(
            imsi="123456789012349",
            msisdn="+1234567891",
            ip_address="192.168.1.101"
        )
        
        # Create content message
        content_message = self.li_builder.create_content_message(
            target_identity=target_identity,
            content_data="This is intercepted SMS message content",
            content_type=ContentType.TEXT,
            protocol=Protocol.SMS,
            direction="uplink"
        )
        
        print("LI Content Message (LI-X2):")
        print(self.li_builder.to_json(content_message))
        
        # Create IRI message
        iri_message = self.li_builder.create_iri_message(
            target_identity=target_identity,
            event_type=EventType.SESSION_ESTABLISHMENT,
            event_data={
                "session_id": "session-001",
                "pdu_session_type": "IPv4",
                "dnn": "internet",
                "sst": 1,
                "sd": "000001"
            }
        )
        
        print("\nLI IRI Message (LI-X3):")
        print(self.li_builder.to_json(iri_message))

    async def example_session_status_management(self, li_session_id: str):
        """Example: Session status management"""
        print(f"\n=== Session Status Management for: {li_session_id} ===")
        
        # Get session status
        status = self.li_handler.get_li_session_status(li_session_id)
        print(f"Session Status: {json.dumps(status, indent=2)}")
        
        # List all sessions
        sessions = self.li_handler.list_li_sessions()
        print(f"\nAll LI Sessions: {json.dumps(sessions, indent=2)}")

    async def example_error_handling(self):
        """Example: Error handling scenarios"""
        print("\n=== Error Handling Examples ===")
        
        # Try to create session with invalid data
        invalid_request = {
            "li_session_id": "invalid-session-id",  # Invalid format
            "target_imsi": "123",  # Invalid IMSI
            "li_x2_endpoint": "invalid-url"  # Invalid URL
        }
        
        result = await self.li_handler.create_li_session(invalid_request)
        print(f"Invalid Request Result: {json.dumps(result, indent=2)}")
        
        # Try to modify non-existent session
        result = await self.li_handler.modify_li_session("non-existent-session", {})
        print(f"Non-existent Session Result: {json.dumps(result, indent=2)}")

    async def example_terminate_li_session(self, li_session_id: str):
        """Example: Terminate LI session"""
        print(f"\n=== Terminating LI Session: {li_session_id} ===")
        
        result = await self.li_handler.terminate_li_session(li_session_id)
        print(f"LI Session Termination Result: {json.dumps(result, indent=2)}")

    async def run_all_examples(self):
        """Run all examples"""
        try:
            await self.initialize()
            
            # Create LI session
            li_session_id = await self.example_create_li_session()
            
            if li_session_id:
                # Modify session
                await self.example_modify_li_session(li_session_id)
                
                # Handle intercepted content
                await self.example_handle_intercepted_content(li_session_id)
                
                # Session status management
                await self.example_session_status_management(li_session_id)
                
                # Terminate session
                await self.example_terminate_li_session(li_session_id)
            
            # Create PFCP messages
            await self.example_create_pfcp_messages()
            
            # Create LI messages
            await self.example_create_li_messages()
            
            # Error handling
            await self.example_error_handling()
            
        except Exception as e:
            print(f"Error running examples: {e}")
        finally:
            await self.cleanup()

def generate_li_code_example():
    """Generate a complete LI implementation example"""
    return """
# Complete LI Implementation Example
import asyncio
from smf_upf_li_handler import SMFUPFLIHandler

async def main():
    # Initialize LI handler
    li_handler = SMFUPFLIHandler("smf-001", "upf-001")
    await li_handler.initialize()
    
    # Create LI session
    li_request = {
        "li_session_id": "li-session-001",
        "target_imsi": "123456789012345",
        "target_msisdn": "+1234567890",
        "target_ip": "192.168.1.100",
        "li_x2_endpoint": "https://li-x2.example.com:8080",
        "li_x3_endpoint": "https://li-x3.example.com:8081",
        "encryption_key_id": "li-key-001"
    }
    
    result = await li_handler.create_li_session(li_request)
    print(f"LI Session Created: {result}")
    
    # Handle intercepted content
    content_data = {
        "li_session_id": "li-session-001",
        "content": "Intercepted HTTP request",
        "content_type": "text",
        "protocol": "HTTP",
        "direction": "uplink"
    }
    
    await li_handler.handle_intercepted_content(content_data)
    
    # Terminate session
    await li_handler.terminate_li_session("li-session-001")
    await li_handler.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
"""

if __name__ == "__main__":
    example = LISessionExample()
    asyncio.run(example.run_all_examples())
    
    print("\n=== Generated Code Example ===")
    print(generate_li_code_example())