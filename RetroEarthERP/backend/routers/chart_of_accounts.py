from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from decimal import Decimal

from database import get_db
import models
from routers.auth import get_current_active_user

router = APIRouter(
    prefix="/api/chart-of-accounts",
    tags=["Chart of Accounts"],
    responses={404: {"description": "Not found"}},
)

# Schemas
class AccountBase(BaseModel):
    code: str
    name_th: str
    name_en: Optional[str] = None
    account_type: str
    account_level: int = 1
    is_postable: bool = True
    normal_balance: str = "DEBIT"
    parent_id: Optional[int] = None
    description: Optional[str] = None

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class AccountTreeNode(BaseModel):
    id: int
    code: str
    name_th: str
    name_en: Optional[str]
    account_type: str
    account_level: int
    is_postable: bool
    normal_balance: str
    children: List['AccountTreeNode'] = []
    
    class Config:
        from_attributes = True

# Endpoints

@router.get("/", response_model=List[AccountResponse])
def get_all_accounts(
    category: Optional[str] = None,
    postable_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all GL accounts, optionally filtered by category"""
    query = db.query(models.MasterAccount).filter(models.MasterAccount.is_active == True)
    
    if category:
        query = query.filter(models.MasterAccount.account_type == category)
    
    if postable_only:
        query = query.filter(models.MasterAccount.is_postable == True)
    
    return query.order_by(models.MasterAccount.code).all()


@router.get("/tree", response_model=List[AccountTreeNode])
def get_account_tree(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get Chart of Accounts as hierarchical tree"""
    query = db.query(models.MasterAccount).filter(
        models.MasterAccount.is_active == True,
        models.MasterAccount.parent_id == None  # Root nodes only
    )
    
    if category:
        query = query.filter(models.MasterAccount.account_type == category)
    
    root_accounts = query.order_by(models.MasterAccount.code).all()
    
    def build_tree(account):
        children = db.query(models.MasterAccount).filter(
            models.MasterAccount.parent_id == account.id,
            models.MasterAccount.is_active == True
        ).order_by(models.MasterAccount.code).all()
        
        return AccountTreeNode(
            id=account.id,
            code=account.code,
            name_th=account.name_th,
            name_en=account.name_en,
            account_type=account.account_type.value,
            account_level=account.account_level,
            is_postable=account.is_postable,
            normal_balance=account.normal_balance,
            children=[build_tree(child) for child in children]
        )
    
    return [build_tree(acc) for acc in root_accounts]


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a specific GL account"""
    account = db.query(models.MasterAccount).filter(models.MasterAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new GL account"""
    # Check if code already exists
    existing = db.query(models.MasterAccount).filter(models.MasterAccount.code == account.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Account code '{account.code}' already exists")
    
    db_account = models.MasterAccount(
        code=account.code,
        name_th=account.name_th,
        name_en=account.name_en,
        account_type=account.account_type,
        account_level=account.account_level,
        is_postable=account.is_postable,
        normal_balance=account.normal_balance,
        parent_id=account.parent_id,
        description=account.description,
        is_active=True
    )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Update a GL account"""
    db_account = db.query(models.MasterAccount).filter(models.MasterAccount.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Update fields
    db_account.name_th = account.name_th
    db_account.name_en = account.name_en
    db_account.account_level = account.account_level
    db_account.is_postable = account.is_postable
    db_account.normal_balance = account.normal_balance
    db_account.parent_id = account.parent_id
    db_account.description = account.description
    
    db.commit()
    db.refresh(db_account)
    
    return db_account


@router.delete("/{account_id}")
def deactivate_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Deactivate a GL account (soft delete)"""
    db_account = db.query(models.MasterAccount).filter(models.MasterAccount.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Check if account has been used in journal entries
    has_entries = db.query(models.TrnJournalEntryLine).filter(
        models.TrnJournalEntryLine.account_id == account_id
    ).first()
    
    if has_entries:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate account that has been used in journal entries"
        )
    
    db_account.is_active = False
    db.commit()
    
    return {"message": "Account deactivated successfully"}
