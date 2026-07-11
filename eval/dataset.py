"""Hand-written QA pairs grounded in data/knowledge_base/, covering every
source document and the main insurance intent categories.

Used by run_eval.py to measure retrieval quality, answer quality,
and end-to-end assistant quality.
"""

EVAL_DATASET = [
    {
        "id": "claim-status-tracking",
        "category": "claim_status",
        "question": "How can I track the status of my insurance claim?",
        "ground_truth": (
            "Customers can track their claims using the claim number and "
            "registered mobile number through the customer portal, "
            "mobile application, or customer support center."
        ),
        "expected_source": "insurance_general_faq.html",
    },
    {
        "id": "claim-settlement-timeline",
        "category": "reimbursement_query",
        "question": "How long does claim settlement usually take?",
        "ground_truth": (
            "Claims are generally processed within 7 to 15 working days "
            "after receipt of complete documentation."
        ),
        "expected_source": "insurance_general_faq.html",
    },
    {
        "id": "health-coverage",
        "category": "policy_coverage",
        "question": "What expenses are covered under health insurance?",
        "ground_truth": (
            "Coverage typically includes hospitalization expenses, "
            "intensive care, day-care procedures, ambulance charges, "
            "and pre/post hospitalization expenses."
        ),
        "expected_source": "policy_coverage_faq.html",
    },
    {
        "id": "motor-coverage",
        "category": "policy_coverage",
        "question": "What does a motor insurance policy cover?",
        "ground_truth": (
            "Coverage includes accidental damage, theft, fire, "
            "natural calamities, and third-party liability."
        ),
        "expected_source": "policy_coverage_faq.html",
    },
    {
        "id": "policy-exclusions",
        "category": "policy_coverage",
        "question": "What are common exclusions in insurance policies?",
        "ground_truth": (
            "Common exclusions include cosmetic procedures, experimental "
            "treatments, intentional self-harm, and damages caused while "
            "driving under the influence."
        ),
        "expected_source": "policy_coverage_faq.html",
    },
    {
        "id": "health-claim-documents",
        "category": "document_request",
        "question": "What documents are required for a health insurance claim?",
        "ground_truth": (
            "Claim form, hospital bills, discharge summary, prescriptions, "
            "diagnostic reports, and identity proof."
        ),
        "expected_source": "claim_submission_guide.docx",
    },
    {
        "id": "motor-claim-documents",
        "category": "document_request",
        "question": "What documents are needed for a motor insurance claim?",
        "ground_truth": (
            "Photographs, vehicle registration certificate, driving license, "
            "repair estimates, and FIR when applicable."
        ),
        "expected_source": "claim_submission_guide.docx",
    },
    {
        "id": "life-claim-documents",
        "category": "document_request",
        "question": "What documents are required for a life insurance claim?",
        "ground_truth": (
            "Claim form, policy document, death certificate, nominee identity proof, "
            "and bank account details."
        ),
        "expected_source": "claim_submission_guide.docx",
    },
    {
        "id": "claim-rejection-reasons",
        "category": "claim_rejection",
        "question": "Why can an insurance claim be rejected?",
        "ground_truth": (
            "Claims may be rejected due to policy exclusions, "
            "non-disclosure of material facts, policy lapse, fraudulent "
            "information, incomplete documentation, or incidents occurring "
            "during waiting periods."
        ),
        "expected_source": "claim_rejection_policy.pdf",
    },
    {
        "id": "claim-appeal-process",
        "category": "claim_rejection",
        "question": "Can I appeal a rejected insurance claim?",
        "ground_truth": (
            "Customers may appeal rejected claims by providing additional "
            "documentation or clarification within 30 calendar days of "
            "receiving the rejection notice."
        ),
        "expected_source": "claim_rejection_policy.pdf",
    },
    {
        "id": "reimbursement-definition",
        "category": "reimbursement_query",
        "question": "What is a reimbursement claim?",
        "ground_truth": (
            "Customers who receive treatment at a non-network facility may "
            "submit reimbursement claims after paying expenses directly."
        ),
        "expected_source": "reimbursement_policy.pdf",
    },
    {
        "id": "reimbursement-payment",
        "category": "reimbursement_query",
        "question": "How is an approved reimbursement claim paid?",
        "ground_truth": (
            "Approved claim amounts are transferred directly to the "
            "customer's registered bank account."
        ),
        "expected_source": "reimbursement_policy.pdf",
    },
    {
        "id": "health-processing-time",
        "category": "document_request",
        "question": "How long does a health insurance claim take to process?",
        "ground_truth": "7-15 Working Days",
        "expected_source": "claim_documents_checklist.csv",
    },
    {
        "id": "property-processing-time",
        "category": "document_request",
        "question": "How long does a property insurance claim take to process?",
        "ground_truth": "10-30 Working Days",
        "expected_source": "claim_documents_checklist.csv",
    },
]