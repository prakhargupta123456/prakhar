# Cursor AI Rules for 3GPP Lawful Interception Code Generation

## Overview
These rules configure Cursor AI to generate code for 3GPP lawful interception interfaces between SMF and UPF based on the specifications in TS 29.244 and TS 33.126.

## Code Generation Rules

### 1. PFCP Message Generation
When generating PFCP messages for lawful interception:

- **Always use the PFCP message template** from `code-templates/pfcp-message-template.py`
- **Include proper error handling** for all PFCP operations
- **Validate input parameters** before creating messages
- **Use appropriate message types**: Session Establishment, Modification, Deletion
- **Include LI-specific IEs**: PDR, FAR, URR with LI forwarding information
- **Set proper precedence values** for LI PDRs (typically 50-100)
- **Include encryption information** for LI data forwarding

### 2. LI Message Generation
When generating lawful interception messages:

- **Use the LI message template** from `code-templates/li-message-template.py`
- **Distinguish between LI-X2 (content) and LI-X3 (IRI) messages**
- **Include proper target identity information** (IMSI, MSISDN, IP address)
- **Add encryption information** for all LI messages
- **Include timestamps** in ISO 8601 format
- **Validate message sequence numbers**
- **Handle different content types** (text, binary, audio, video)

### 3. Session Management
When implementing session management:

- **Use the SMF-UPF LI handler** from `code-templates/smf-upf-li-handler.py`
- **Implement proper session lifecycle**: Create, Modify, Terminate
- **Handle session state transitions** correctly
- **Include session validation** before operations
- **Log all session operations** for audit purposes
- **Handle concurrent session modifications**

### 4. Error Handling
When implementing error handling:

- **Use standard PFCP error codes** (100-110)
- **Use standard LI error codes** (LI-001 to LI-008)
- **Include retry mechanisms** for transient failures
- **Log errors with appropriate levels** (ERROR, WARNING, INFO)
- **Provide meaningful error messages** to users
- **Handle network timeouts** gracefully

### 5. Security Implementation
When implementing security features:

- **Encrypt all LI data** using AES-256-GCM or equivalent
- **Implement proper key management** for encryption keys
- **Use secure communication channels** (TLS 1.3)
- **Validate certificates** for all LI endpoints
- **Implement access control** for LI operations
- **Audit all LI activities** for compliance

## Code Generation Patterns

### PFCP Session Establishment for LI
```python
# Pattern for creating LI PFCP sessions
builder = PFCPMessageBuilder(f_seid, session_id)
message = builder.create_li_session_establishment(
    li_session_id=li_session_id,
    target_imsi=target_imsi,
    li_x2_endpoint=li_x2_endpoint,
    li_x3_endpoint=li_x3_endpoint
)
```

### LI Content Message Creation
```python
# Pattern for creating LI content messages
builder = LIMessageBuilder(li_session_id)
message = builder.create_content_message(
    target_identity=target_identity,
    content_data=content_data,
    content_type=ContentType.TEXT,
    protocol=Protocol.HTTP,
    direction="uplink"
)
```

### LI IRI Message Creation
```python
# Pattern for creating LI IRI messages
builder = LIMessageBuilder(li_session_id)
message = builder.create_iri_message(
    target_identity=target_identity,
    event_type=EventType.SESSION_ESTABLISHMENT,
    event_data=event_data
)
```

## Validation Rules

### Input Validation
- **Validate IMSI format**: 15 digits
- **Validate MSISDN format**: + followed by 1-15 digits
- **Validate IP addresses**: IPv4 or IPv6 format
- **Validate LI session IDs**: Must match pattern `li-session-[0-9]+`
- **Validate endpoint URLs**: Must be valid HTTP/HTTPS URLs

### Message Validation
- **Check required fields** are present
- **Validate enum values** against allowed options
- **Check message length** limits
- **Validate timestamp formats** (ISO 8601)
- **Check encryption parameters** are valid

## Performance Considerations

### Memory Management
- **Use generators** for large data processing
- **Implement proper cleanup** for resources
- **Limit message queue sizes** to prevent memory issues
- **Use connection pooling** for HTTP clients

### Network Optimization
- **Implement message batching** for multiple LI messages
- **Use compression** for large content messages
- **Implement retry logic** with exponential backoff
- **Monitor network latency** and adjust timeouts

## Testing Guidelines

### Unit Testing
- **Test all message creation functions**
- **Validate error handling paths**
- **Test encryption/decryption functions**
- **Verify input validation**

### Integration Testing
- **Test SMF-UPF communication**
- **Verify LI endpoint connectivity**
- **Test session lifecycle operations**
- **Validate error recovery**

### Performance Testing
- **Test with high message volumes**
- **Verify memory usage under load**
- **Test concurrent session handling**
- **Validate response times**

## Compliance Requirements

### 3GPP Standards
- **Follow TS 29.244** for PFCP implementation
- **Follow TS 33.126** for LI architecture
- **Implement required LI interfaces** (LI-X1, LI-X2, LI-X3)
- **Use standard message formats** and encodings

### Security Standards
- **Implement encryption** as per 3GPP requirements
- **Follow key management** best practices
- **Implement audit logging** for compliance
- **Ensure data privacy** protection

### Legal Requirements
- **Implement data retention** policies
- **Provide audit trails** for all operations
- **Support data deletion** after retention period
- **Implement access controls** for LI data

## Code Quality Standards

### Documentation
- **Document all public functions** with docstrings
- **Include type hints** for all parameters
- **Add inline comments** for complex logic
- **Provide usage examples** in docstrings

### Code Style
- **Follow PEP 8** style guidelines
- **Use meaningful variable names**
- **Keep functions focused** and small
- **Implement proper error handling**

### Testing
- **Achieve high test coverage** (>90%)
- **Include edge case testing**
- **Test error conditions**
- **Validate performance requirements**

## Common Patterns to Avoid

### Anti-patterns
- **Don't hardcode** LI endpoints or keys
- **Don't skip input validation**
- **Don't ignore error conditions**
- **Don't use weak encryption** algorithms
- **Don't log sensitive data** in plain text

### Best Practices
- **Use configuration files** for LI parameters
- **Implement proper logging** with appropriate levels
- **Use async/await** for I/O operations
- **Implement circuit breakers** for external calls
- **Use structured logging** for better analysis

## Integration Guidelines

### SMF Integration
- **Use standard SMF APIs** for session management
- **Implement proper event handling** for session changes
- **Support session context** updates
- **Handle SMF failures** gracefully

### UPF Integration
- **Use PFCP protocol** for UPF communication
- **Implement proper message handling**
- **Support UPF capabilities** negotiation
- **Handle UPF failures** and recovery

### LI System Integration
- **Use standard LI message formats**
- **Implement proper authentication** for LI endpoints
- **Support LI system** requirements
- **Handle LI system failures** gracefully