#!/usr/bin/env python3
"""
SMF-UPF Lawful Interception Handler
Implements the interface between SMF and UPF for lawful interception
Based on 3GPP TS 29.244 and TS 33.126
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import aiohttp
from aiohttp import web
import ssl

# Import our templates
from pfcp_message_template import PFCPMessageBuilder, PFCPMessageType
from li_message_template import LIMessageBuilder, LIMessageType, TargetIdentity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LIStatus(Enum):
    """Lawful Interception Status"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ERROR = "error"
    TERMINATED = "terminated"

@dataclass
class LISession:
    """Lawful Interception Session"""
    li_session_id: str
    target_identity: TargetIdentity
    smf_session_id: str
    upf_session_id: str
    status: LIStatus
    created_at: float
    li_x2_endpoint: str
    li_x3_endpoint: str
    encryption_key_id: str
    interception_scope: Dict[str, bool]

class SMFUPFLIHandler:
    """SMF-UPF Lawful Interception Handler"""
    
    def __init__(self, smf_id: str, upf_id: str):
        self.smf_id = smf_id
        self.upf_id = upf_id
        self.li_sessions: Dict[str, LISession] = {}
        self.pfcp_builder = PFCPMessageBuilder("0x1234567890abcdef", 12345)
        self.li_builder = LIMessageBuilder("li-session-12345")
        self.http_session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize the handler"""
        self.http_session = aiohttp.ClientSession()
        logger.info(f"SMF-UPF LI Handler initialized: SMF={self.smf_id}, UPF={self.upf_id}")

    async def cleanup(self):
        """Cleanup resources"""
        if self.http_session:
            await self.http_session.close()

    async def create_li_session(self, li_request: Dict) -> Dict:
        """Create a new lawful interception session"""
        try:
            li_session_id = li_request.get("li_session_id")
            target_identity = TargetIdentity(
                imsi=li_request.get("target_imsi"),
                msisdn=li_request.get("target_msisdn"),
                ip_address=li_request.get("target_ip")
            )
            li_x2_endpoint = li_request.get("li_x2_endpoint")
            li_x3_endpoint = li_request.get("li_x3_endpoint")
            encryption_key_id = li_request.get("encryption_key_id", "default-key")
            
            # Create LI session
            li_session = LISession(
                li_session_id=li_session_id,
                target_identity=target_identity,
                smf_session_id=f"smf-session-{int(time.time())}",
                upf_session_id=f"upf-session-{int(time.time())}",
                status=LIStatus.ACTIVE,
                created_at=time.time(),
                li_x2_endpoint=li_x2_endpoint,
                li_x3_endpoint=li_x3_endpoint,
                encryption_key_id=encryption_key_id,
                interception_scope=li_request.get("interception_scope", {
                    "content_of_communications": True,
                    "intercept_related_information": True,
                    "location_information": True
                })
            )
            
            self.li_sessions[li_session_id] = li_session
            
            # Create PFCP session establishment request
            pfcp_message = self.pfcp_builder.create_li_session_establishment(
                li_session_id=li_session_id,
                target_imsi=target_identity.imsi,
                li_x2_endpoint=li_x2_endpoint,
                li_x3_endpoint=li_x3_endpoint
            )
            
            # Send PFCP message to UPF
            await self._send_pfcp_message(pfcp_message)
            
            # Send LI session establishment IRI
            await self._send_li_iri_message(
                li_session_id=li_session_id,
                target_identity=target_identity,
                event_type="LI Session Establishment",
                event_data={
                    "smf_session_id": li_session.smf_session_id,
                    "upf_session_id": li_session.upf_session_id,
                    "interception_scope": li_session.interception_scope
                }
            )
            
            logger.info(f"LI session created: {li_session_id}")
            
            return {
                "status": "success",
                "li_session_id": li_session_id,
                "smf_session_id": li_session.smf_session_id,
                "upf_session_id": li_session.upf_session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to create LI session: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def modify_li_session(self, li_session_id: str, modifications: Dict) -> Dict:
        """Modify an existing lawful interception session"""
        try:
            if li_session_id not in self.li_sessions:
                raise ValueError(f"LI session not found: {li_session_id}")
            
            li_session = self.li_sessions[li_session_id]
            
            # Create PFCP session modification request
            pfcp_message = self.pfcp_builder.create_li_session_modification(
                li_session_id=li_session_id,
                new_target_imsi=modifications.get("new_target_imsi"),
                update_li_endpoints=modifications.get("update_li_endpoints", False)
            )
            
            # Send PFCP message to UPF
            await self._send_pfcp_message(pfcp_message)
            
            # Update session if needed
            if modifications.get("new_target_imsi"):
                li_session.target_identity.imsi = modifications["new_target_imsi"]
            
            # Send LI session modification IRI
            await self._send_li_iri_message(
                li_session_id=li_session_id,
                target_identity=li_session.target_identity,
                event_type="LI Session Modification",
                event_data=modifications
            )
            
            logger.info(f"LI session modified: {li_session_id}")
            
            return {
                "status": "success",
                "li_session_id": li_session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to modify LI session: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def terminate_li_session(self, li_session_id: str) -> Dict:
        """Terminate a lawful interception session"""
        try:
            if li_session_id not in self.li_sessions:
                raise ValueError(f"LI session not found: {li_session_id}")
            
            li_session = self.li_sessions[li_session_id]
            
            # Create PFCP session deletion request
            pfcp_message = self.pfcp_builder.create_li_session_deletion()
            
            # Send PFCP message to UPF
            await self._send_pfcp_message(pfcp_message)
            
            # Send LI session termination IRI
            await self._send_li_iri_message(
                li_session_id=li_session_id,
                target_identity=li_session.target_identity,
                event_type="LI Session Termination",
                event_data={
                    "termination_reason": "Requested by LEA",
                    "session_duration": time.time() - li_session.created_at
                }
            )
            
            # Update session status
            li_session.status = LIStatus.TERMINATED
            
            logger.info(f"LI session terminated: {li_session_id}")
            
            return {
                "status": "success",
                "li_session_id": li_session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to terminate LI session: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def handle_intercepted_content(self, content_data: Dict) -> None:
        """Handle intercepted content from UPF"""
        try:
            li_session_id = content_data.get("li_session_id")
            
            if li_session_id not in self.li_sessions:
                logger.warning(f"Received content for unknown LI session: {li_session_id}")
                return
            
            li_session = self.li_sessions[li_session_id]
            
            # Create LI content message
            content_message = self.li_builder.create_content_message(
                target_identity=li_session.target_identity,
                content_data=content_data.get("content", ""),
                content_type=content_data.get("content_type", "text"),
                protocol=content_data.get("protocol", "HTTP"),
                direction=content_data.get("direction", "uplink")
            )
            
            # Send to LI-X2 endpoint
            await self._send_li_content_message(li_session, content_message)
            
            logger.info(f"Intercepted content forwarded: {li_session_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle intercepted content: {e}")

    async def _send_pfcp_message(self, pfcp_message) -> None:
        """Send PFCP message to UPF"""
        try:
            # In a real implementation, this would send the PFCP message
            # to the UPF via the N4 interface
            logger.info(f"Sending PFCP message: {pfcp_message.message_type.name}")
            # Simulate network delay
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Failed to send PFCP message: {e}")
            raise

    async def _send_li_iri_message(self, li_session_id: str, target_identity: TargetIdentity,
                                 event_type: str, event_data: Dict) -> None:
        """Send LI IRI message to LI-X3 endpoint"""
        try:
            if li_session_id not in self.li_sessions:
                return
            
            li_session = self.li_sessions[li_session_id]
            
            # Create IRI message
            iri_message = self.li_builder.create_iri_message(
                target_identity=target_identity,
                event_type=event_type,
                event_data=event_data
            )
            
            # Send to LI-X3 endpoint
            if self.http_session and li_session.li_x3_endpoint:
                async with self.http_session.post(
                    li_session.li_x3_endpoint,
                    json=json.loads(self.li_builder.to_json(iri_message)),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        logger.info(f"IRI message sent successfully: {li_session_id}")
                    else:
                        logger.error(f"Failed to send IRI message: {response.status}")
            
        except Exception as e:
            logger.error(f"Failed to send IRI message: {e}")

    async def _send_li_content_message(self, li_session: LISession, content_message) -> None:
        """Send LI content message to LI-X2 endpoint"""
        try:
            # Send to LI-X2 endpoint
            if self.http_session and li_session.li_x2_endpoint:
                async with self.http_session.post(
                    li_session.li_x2_endpoint,
                    json=json.loads(self.li_builder.to_json(content_message)),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        logger.info(f"Content message sent successfully: {li_session.li_session_id}")
                    else:
                        logger.error(f"Failed to send content message: {response.status}")
            
        except Exception as e:
            logger.error(f"Failed to send content message: {e}")

    def get_li_session_status(self, li_session_id: str) -> Optional[Dict]:
        """Get LI session status"""
        if li_session_id not in self.li_sessions:
            return None
        
        li_session = self.li_sessions[li_session_id]
        return {
            "li_session_id": li_session_id,
            "status": li_session.status.value,
            "target_identity": {
                "imsi": li_session.target_identity.imsi,
                "msisdn": li_session.target_identity.msisdn,
                "ip_address": li_session.target_identity.ip_address
            },
            "created_at": li_session.created_at,
            "interception_scope": li_session.interception_scope
        }

    def list_li_sessions(self) -> List[Dict]:
        """List all LI sessions"""
        return [
            self.get_li_session_status(session_id)
            for session_id in self.li_sessions.keys()
        ]

# HTTP API for SMF-UPF LI Handler
async def create_li_session_handler(request):
    """HTTP handler for creating LI sessions"""
    handler = request.app['li_handler']
    data = await request.json()
    result = await handler.create_li_session(data)
    return web.json_response(result)

async def modify_li_session_handler(request):
    """HTTP handler for modifying LI sessions"""
    handler = request.app['li_handler']
    li_session_id = request.match_info['session_id']
    data = await request.json()
    result = await handler.modify_li_session(li_session_id, data)
    return web.json_response(result)

async def terminate_li_session_handler(request):
    """HTTP handler for terminating LI sessions"""
    handler = request.app['li_handler']
    li_session_id = request.match_info['session_id']
    result = await handler.terminate_li_session(li_session_id)
    return web.json_response(result)

async def get_li_session_status_handler(request):
    """HTTP handler for getting LI session status"""
    handler = request.app['li_handler']
    li_session_id = request.match_info['session_id']
    result = handler.get_li_session_status(li_session_id)
    if result:
        return web.json_response(result)
    else:
        return web.json_response({"error": "Session not found"}, status=404)

async def list_li_sessions_handler(request):
    """HTTP handler for listing LI sessions"""
    handler = request.app['li_handler']
    result = handler.list_li_sessions()
    return web.json_response(result)

async def handle_intercepted_content_handler(request):
    """HTTP handler for intercepted content from UPF"""
    handler = request.app['li_handler']
    data = await request.json()
    await handler.handle_intercepted_content(data)
    return web.json_response({"status": "success"})

def create_app(li_handler: SMFUPFLIHandler):
    """Create the web application"""
    app = web.Application()
    app['li_handler'] = li_handler
    
    # Add routes
    app.router.add_post('/li/sessions', create_li_session_handler)
    app.router.add_put('/li/sessions/{session_id}', modify_li_session_handler)
    app.router.add_delete('/li/sessions/{session_id}', terminate_li_session_handler)
    app.router.add_get('/li/sessions/{session_id}', get_li_session_status_handler)
    app.router.add_get('/li/sessions', list_li_sessions_handler)
    app.router.add_post('/li/content', handle_intercepted_content_handler)
    
    return app

async def main():
    """Main function"""
    # Create LI handler
    li_handler = SMFUPFLIHandler("smf-001", "upf-001")
    await li_handler.initialize()
    
    # Create web application
    app = create_app(li_handler)
    
    # Start web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    logger.info("SMF-UPF LI Handler started on port 8080")
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await li_handler.cleanup()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())