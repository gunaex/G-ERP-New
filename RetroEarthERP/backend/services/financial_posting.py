"""
Financial Posting Service
Integrates operational documents (Sales, Purchasing, Inventory) with General Ledger
SAP B1-style automatic journal entry generation
"""
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from typing import List, Dict, Optional
import models
from services.gl_determination import get_gl_account
from services.thai_tax import calculate_vat, get_default_vat_group


def generate_journal_number(db: Session) -> str:
    """
    Generate next journal entry number (format: JV-YYYY-MM-NNNN).
    
    Args:
        db: Database session
        
    Returns:
        str: Journal number
    """
    today = date.today()
    prefix = f"JV-{today.year}-{str(today.month).zfill(2)}"
    
    last_je = db.query(models.TrnJournalEntryHead).filter(
        models.TrnJournalEntryHead.journal_no.like(f"{prefix}-%")
    ).order_by(models.TrnJournalEntryHead.id.desc()).first()
    
    if last_je:
        last_number = int(last_je.journal_no.split('-')[-1])
        new_number = last_number + 1
    else:
        new_number = 1
    
    return f"{prefix}-{str(new_number).zfill(4)}"


def create_ar_invoice_posting(
    db: Session,
    invoice_id: int,
    user_id: int
) -> models.TrnJournalEntryHead:
    """
    Create Journal Entry for Sales Invoice (AR).
    
    Dr. Accounts Receivable (Total Amount)
    Cr. Sales Revenue (Net Amount)
    Cr. Output VAT (VAT Amount)
    
    If Perpetual Inventory:
    Dr. Cost of Goods Sold
    Cr. Inventory
    
    Args:
        db: Database session
        invoice_id: Tax Invoice ID
        user_id: User creating the entry
        
    Returns:
        TrnJournalEntryHead: Created journal entry
    """
    # Get invoice
    invoice = db.query(models.TrnTaxInvoiceHead).filter_by(id=invoice_id).first()
    if not invoice:
        raise ValueError(f"Invoice ID {invoice_id} not found")
    
    # Get GL accounts
    ar_account_id = get_gl_account(db, "AR_DOMESTIC")
    revenue_account_id = get_gl_account(db, "SALES_REVENUE")
    vat_account_id = get_gl_account(db, "SALES_VAT")
    
    # Create Journal Entry Header
    je = models.TrnJournalEntryHead(
        journal_no=generate_journal_number(db),
        date=invoice.invoice_date,
        description=f"Sales Invoice - {invoice.customer_name}",
        reference=invoice.invoice_no,
        status=models.DocumentStatus.POSTED,
        source_document_type="TAX_INVOICE",
        source_document_id=invoice_id,
        created_by=user_id,
        posted_by=user_id,
        posted_at=date.today()
    )
    db.add(je)
    db.flush()  # Get ID
    
    # Create Journal Lines
    lines = []
    
    # Dr. Accounts Receivable
    lines.append(models.TrnJournalEntryLine(
        journal_id=je.id,
        account_id=ar_account_id,
        partner_id=invoice.customer_id if hasattr(invoice, 'customer_id') else None,
        description=f"A/R - {invoice.customer_name}",
        debit=invoice.total_amount,
        credit=Decimal('0.00')
    ))
    
    # Cr. Sales Revenue
    net_amount = invoice.total_amount - invoice.tax_amount
    lines.append(models.TrnJournalEntryLine(
        journal_id=je.id,
        account_id=revenue_account_id,
        description="Sales Revenue",
        debit=Decimal('0.00'),
        credit=net_amount
    ))
    
    # Cr. Output VAT
    if invoice.tax_amount > 0:
        lines.append(models.TrnJournalEntryLine(
            journal_id=je.id,
            account_id=vat_account_id,
            description="Output VAT 7%",
            debit=Decimal('0.00'),
            credit=invoice.tax_amount
        ))
    
    db.add_all(lines)
    db.commit()
    db.refresh(je)
    
    return je


def create_ap_grpo_posting(
    db: Session,
    grpo_id: int,
    user_id: int
) -> models.TrnJournalEntryHead:
    """
    Create Journal Entry for Goods Receipt PO (AP).
    
    Dr. Inventory
    Dr. Input VAT
    Cr. Accounts Payable
    
    Args:
        db: Database session
        grpo_id: Goods Receipt PO ID
        user_id: User creating the entry
        
    Returns:
        TrnJournalEntryHead: Created journal entry
    """
    # TODO: Implement when GRPO table is available
    # This is a placeholder for future implementation
    raise NotImplementedError("GRPO posting will be implemented in Phase 3")


def create_payment_posting(
    db: Session,
    payment_id: int,
    user_id: int,
    wht_amount: Optional[Decimal] = None
) -> models.TrnJournalEntryHead:
    """
    Create Journal Entry for Payment.
    
    Dr. Accounts Payable
    Cr. Bank
    Cr. WHT Payable (if applicable)
    
    Args:
        db: Database session
        payment_id: Payment ID
        user_id: User creating the entry
        wht_amount: Optional WHT amount
        
    Returns:
        TrnJournalEntryHead: Created journal entry
    """
    # TODO: Implement when Payment table is available
    # This is a placeholder for future implementation
    raise NotImplementedError("Payment posting will be implemented in Phase 3")


def validate_journal_balance(lines: List[models.TrnJournalEntryLine]) -> bool:
    """
    Validate that total debits equal total credits.
    
    Args:
        lines: List of journal entry lines
        
    Returns:
        bool: True if balanced, False otherwise
    """
    total_debit = sum(line.debit for line in lines)
    total_credit = sum(line.credit for line in lines)
    
    return total_debit == total_credit
