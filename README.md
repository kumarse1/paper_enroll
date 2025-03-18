# paper_enroll

 install tessaract from the it hub
 add the path in code as 

Paper Enrollment Processing - Architecture & Security Plan

1. Project Overview

Objective

The Paper Enrollment Processing project aims to leverage OCR, Vision AI, LLM, and Human-in-the-Loop (HITL) workflows for document processing. As part of the Proof of Concept (POC), we require a PostgreSQL (PG) Test Database, which will store only mock data (no sensitive data, PII, or PHI). The future production deployment will be integrated with Active Directory (AD) groups for authentication and access control.

Key Components

OCR Processing: Extracts text from scanned paper documents.

Vision AI: Enhances OCR extraction by identifying key structured fields.

LLM Processing:

LLM 1: Summarization and correction of extracted data.

LLM 2: Data validation, recommendations, and classification.

Human-in-the-Loop (HITL): Manual validation and approval process.

PG Test Database: Stores extracted and processed mock data.

Entitlement-based Data Access: Restricts data based on user roles.

Future Integration: The system will be integrated into an existing SSO-enabled application.

2. Workflow & Data Creation

2.1 Steps Involved in Document Processing

Document Ingestion: User uploads a scanned paper enrollment form.

OCR Processing: Extracts raw text from the document.

Vision AI Processing: Detects structured fields (e.g., Name, DOB, Address).

LLM Summarization & Corrections:

Standardizes and corrects extracted text.

Identifies missing fields.

HITL Review Process:

Reviewer verifies and edits extracted data.

Reviewer approves or rejects document processing.

Data Storage & Classification:

Mock data is stored in PG Test DB.

Classified based on GEN (General), FEBP (Federal Benefits), STATE (State Benefits), EMPLOYEE categories.

Access Control & Logging:

Users can only access permitted data.

All read/write/update operations are logged.

Final Submission & Integration:

The processed data is made available to external systems for validation.

2.2 Mock Data Creation Plan

Documents: Sample enrollment forms (non-sensitive, randomly generated text).

Users & Roles: Mock users for different AD groups.

Data Fields: Simulated structured data (e.g., Name, DOB, Employee ID).

Validation Scenarios: Various test cases for OCR/AI processing.

3. Workflow Control: Data Classification & Entitlements

3.1 Data Classification

All stored data is classified into categories to enforce role-based access control (RBAC):

GEN (General): Generic enrollment data (e.g., form types, status tracking).

FEBP (Federal Benefits): Enrollment forms related to federal benefit programs.

STATE (State Benefits): Enrollment forms under state-funded benefit programs.

EMPLOYEE (Employee-specific): Employee-related enrollment information.

3.2 Entitlement-Based Access Control

User Role

GEN Access

FEBP Access

STATE Access

EMPLOYEE Access

Admin

✅ Full

✅ Full

✅ Full

✅ Full

Supervisor

✅ Full

✅ Full

✅ Full

❌ No Access

Reviewer

✅ Partial

✅ Partial

✅ Partial

❌ No Access

Employee

❌ No Access

❌ No Access

❌ No Access

✅ Limited Access

Admins have full access to all categories.

Supervisors & Reviewers can access assigned categories.

Employees can access only their own processed forms.

Unauthorized users cannot access data.

4. Data Access & Security Controls

4.1 Access Restrictions During Data Processing

Operation

Who Can Perform?

Restrictions Applied?

Uploading Documents

Authorized users

File type validation (JPG, PNG, PDF)

Reading Data

Admin, Supervisors, Reviewers

Restricted by category & AD group

Updating Extracted Data

HITL Reviewers, Admins

Only approved users can modify fields

Approving Documents

HITL Reviewers, Admins

Must log decisions and timestamps

Downloading Processed Data

Authorized users

Limited access based on AD permissions

4.2 Security Measures

✅ Data Encryption: All stored data is encrypted.
✅ Logging & Monitoring: Every access request is logged.
✅ Access Revocation: If an AD user loses permissions, access is revoked.
✅ Row-Level Security (RLS): Users see only permitted data.

5. Future Enhancements & Controls

Current Limitation

Future Enhancement

Manual HITL verification

AI-assisted validation & auto-approval for high-confidence cases

Limited data access controls

Full SSO & AD-based entitlement integration

Processing speed constraints

Asynchronous processing for batch documents

No real-time anomaly detection

AI-based fraud detection & compliance checks

5.1 Roadmap for Full-Scale Deployment

Phase 1: POC using PG Test DB with mock data (Current Scope).

Phase 2: AD integration for authentication & role-based access.

Phase 3: Enhanced AI validation for reducing manual HITL efforts.

Phase 4: Full production deployment with security compliance.

6. Conclusion

The Paper Enrollment Processing System ensures a secure, structured, and role-based approach for document processing. By leveraging OCR, Vision AI, LLMs, and HITL, we create an efficient pipeline while ensuring data security and entitlement-based access control. This POC will establish a strong foundation for a scalable, production-ready solution in the future.

✅ No sensitive data (PHI/PII) is stored in PG Test DB.✅ AD groups and entitlements control user access.✅ Future enhancements ensure scalability and security compliance.
 
