from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

from database import get_db
import models
from routers.auth import get_current_active_user
from services.thai_tax import generate_wht_certificate, calculate_wht, calculate_vat

router = APIRouter(
    prefix="/api/thai-tax",
    tags=["Thai Tax"],
    responses={404: {"description": "Not found"}},
)

# Schemas
class WHTCodeResponse(BaseModel):
    id: int
    code: str
    rate: Decimal
    income_type_code: str
    description_th: str
    description_en: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True

class WHTCertificateCreate(BaseModel):
    payment_id: Optional[int] = None
    wht_code_id: int
    base_amount: Decimal
    payer_tax_id: str
    payer_name: str
    payer_branch: str = "00000"
    payee_tax_id: str
    payee_name: str
    payee_branch: str = "00000"

class WHTCertificateResponse(BaseModel):
    id: int
    book_number: str
    certificate_date: date
    payment_id: Optional[int]
    payer_tax_id: str
    payer_name: str
    payer_branch: str
    payee_tax_id: str
    payee_name: str
    payee_branch: str
    wht_code_id: int
    base_amount: Decimal
    tax_amount: Decimal
    status: str
    
    class Config:
        from_attributes = True

class TaxGroupResponse(BaseModel):
    id: int
    code: str
    name: str
    rate: Decimal
    tax_type: str
    is_active: bool
    
    class Config:
        from_attributes = True

class VATReportLine(BaseModel):
    document_no: str
    document_date: date
    partner_name: str
    partner_tax_id: str
    base_amount: Decimal
    vat_amount: Decimal
    total_amount: Decimal

class VATReport(BaseModel):
    period_from: date
    period_to: date
    output_vat_lines: List[VATReportLine]
    input_vat_lines: List[VATReportLine]
    total_output_vat: Decimal
    total_input_vat: Decimal
    net_vat_payable: Decimal

# Endpoints

@router.get("/wht-codes", response_model=List[WHTCodeResponse])
def get_wht_codes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all WHT tax codes"""
    return db.query(models.WHTTaxCode).filter(models.WHTTaxCode.is_active == True).all()


@router.post("/wht-certificates", response_model=WHTCertificateResponse, status_code=status.HTTP_201_CREATED)
def create_wht_certificate(
    cert_data: WHTCertificateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Generate a WHT Certificate (50 Bis)"""
    try:
        certificate = generate_wht_certificate(
            db=db,
            payment_id=cert_data.payment_id,
            wht_code_id=cert_data.wht_code_id,
            base_amount=cert_data.base_amount,
            payer_tax_id=cert_data.payer_tax_id,
            payer_name=cert_data.payer_name,
            payee_tax_id=cert_data.payee_tax_id,
            payee_name=cert_data.payee_name,
            payer_branch=cert_data.payer_branch,
            payee_branch=cert_data.payee_branch
        )
        return certificate
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/wht-certificates/{cert_id}", response_model=WHTCertificateResponse)
def get_wht_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a specific WHT certificate"""
    cert = db.query(models.WHTCertificate).filter(models.WHTCertificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="WHT Certificate not found")
    return cert


@router.get("/tax-groups", response_model=List[TaxGroupResponse])
def get_tax_groups(
    tax_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all VAT tax groups"""
    query = db.query(models.TaxGroup).filter(models.TaxGroup.is_active == True)
    
    if tax_type:
        query = query.filter(models.TaxGroup.tax_type == tax_type)
    
    return query.all()


@router.get("/vat-report", response_model=VATReport)
def get_vat_report(
    period_from: date,
    period_to: date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Generate VAT Report (PP.30 style)
    Shows Input VAT and Output VAT for the period
    """
    # TODO: This will be fully implemented when Tax Invoice table is integrated
    # For now, return a placeholder structure
    
    return VATReport(
        period_from=period_from,
        period_to=period_to,
        output_vat_lines=[],
        input_vat_lines=[],
        total_output_vat=Decimal('0.00'),
        total_input_vat=Decimal('0.00'),
        net_vat_payable=Decimal('0.00')
    )
