"""
Thai Tax Calculation Services
WHT and VAT calculation logic for Thai Revenue Department compliance
"""
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from typing import Optional
import models


def calculate_wht(base_amount: Decimal, wht_code: models.WHTTaxCode) -> Decimal:
    """
    Calculate Withholding Tax amount.
    
    Args:
        base_amount: Base amount before WHT
        wht_code: WHT Tax Code object
        
    Returns:
        Decimal: WHT amount
    """
    return (base_amount * wht_code.rate / Decimal('100')).quantize(Decimal('0.01'))


def generate_wht_certificate(
    db: Session,
    payment_id: int,
    wht_code_id: int,
    base_amount: Decimal,
    payer_tax_id: str,
    payer_name: str,
    payee_tax_id: str,
    payee_name: str,
    payer_branch: str = "00000",
    payee_branch: str = "00000"
) -> models.WHTCertificate:
    """
    Generate a WHT Certificate (50 Bis).
    
    Args:
        db: Database session
        payment_id: Payment transaction ID
        wht_code_id: WHT Tax Code ID
        base_amount: Base amount
        payer_tax_id: Payer's 13-digit tax ID
        payer_name: Payer's name
        payee_tax_id: Payee's 13-digit tax ID
        payee_name: Payee's name
        payer_branch: Payer's branch code (default: 00000 = head office)
        payee_branch: Payee's branch code (default: 00000 = head office)
        
    Returns:
        WHTCertificate: Created certificate
    """
    # Get WHT Code
    wht_code = db.query(models.WHTTaxCode).filter_by(id=wht_code_id).first()
    if not wht_code:
        raise ValueError(f"WHT Code ID {wht_code_id} not found")
    
    # Calculate tax amount
    tax_amount = calculate_wht(base_amount, wht_code)
    
    # Generate running number (format: YYYY/NNNN)
    current_year = date.today().year
    last_cert = db.query(models.WHTCertificate).filter(
        models.WHTCertificate.book_number.like(f"{current_year}/%")
    ).order_by(models.WHTCertificate.id.desc()).first()
    
    if last_cert:
        last_number = int(last_cert.book_number.split('/')[1])
        new_number = last_number + 1
    else:
        new_number = 1
    
    book_number = f"{current_year}/{str(new_number).zfill(4)}"
    
    # Create certificate
    certificate = models.WHTCertificate(
        book_number=book_number,
        certificate_date=date.today(),
        payment_id=payment_id,
        payer_tax_id=payer_tax_id,
        payer_name=payer_name,
        payer_branch=payer_branch,
        payee_tax_id=payee_tax_id,
        payee_name=payee_name,
        payee_branch=payee_branch,
        wht_code_id=wht_code_id,
        base_amount=base_amount,
        tax_amount=tax_amount,
        status="ISSUED"
    )
    
    db.add(certificate)
    db.commit()
    db.refresh(certificate)
    
    return certificate


def calculate_vat(amount: Decimal, tax_group: models.TaxGroup) -> Decimal:
    """
    Calculate VAT amount.
    
    Args:
        amount: Base amount before VAT
        tax_group: Tax Group object
        
    Returns:
        Decimal: VAT amount
    """
    return (amount * tax_group.rate / Decimal('100')).quantize(Decimal('0.01'))


def get_default_vat_group(db: Session, vat_type: str = "OUTPUT") -> Optional[models.TaxGroup]:
    """
    Get default VAT group (7%).
    
    Args:
        db: Database session
        vat_type: 'INPUT' or 'OUTPUT'
        
    Returns:
        TaxGroup object or None
    """
    code = "V7I" if vat_type == "INPUT" else "V7"
    return db.query(models.TaxGroup).filter_by(code=code, is_active=True).first()
