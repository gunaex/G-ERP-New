"""
GL Account Determination Engine
SAP B1-style logic to determine GL accounts without hardcoding
"""
from sqlalchemy.orm import Session
from typing import Optional
import models


def get_gl_account(
    db: Session,
    process_key: str,
    profile_name: str = "Default",
    product_category: Optional[models.MasterItem] = None
) -> int:
    """
    Determine the GL Account ID for a business process.
    
    Priority:
    1. Product Category Override (if applicable)
    2. System Default Configuration (GLDetermination table)
    3. Raise error if not configured
    
    Args:
        db: Database session
        process_key: Business process (e.g., 'SALES_REVENUE', 'AR_DOMESTIC')
        profile_name: Configuration profile (default: 'Default')
        product_category: Optional product category for override logic
        
    Returns:
        int: GL Account ID
        
    Raises:
        ValueError: If no configuration found
    """
    
    # TODO: Future enhancement - check product category overrides
    # if product_category:
    #     if process_key == "INVENTORY_ASSET" and product_category.inventory_account_id:
    #         return product_category.inventory_account_id
    #     if process_key == "COST_OF_GOODS" and product_category.cogs_account_id:
    #         return product_category.cogs_account_id
    #     if process_key == "SALES_REVENUE" and product_category.revenue_account_id:
    #         return product_category.revenue_account_id
    
    # Get default configuration
    config = db.query(models.GLDetermination).filter_by(
        process_key=process_key,
        profile_name=profile_name
    ).first()
    
    if not config:
        raise ValueError(
            f"CRITICAL: GL Account not configured for process '{process_key}' "
            f"in profile '{profile_name}'. Please configure in gl_determinations table."
        )
    
    return config.account_id


def get_account_by_code(db: Session, code: str) -> Optional[models.MasterAccount]:
    """
    Get GL Account by code.
    
    Args:
        db: Database session
        code: Account code (e.g., '11300')
        
    Returns:
        MasterAccount object or None
    """
    return db.query(models.MasterAccount).filter_by(code=code, is_active=True).first()


def validate_account_postable(db: Session, account_id: int) -> bool:
    """
    Check if an account is postable (not a title/header account).
    
    Args:
        db: Database session
        account_id: Account ID
        
    Returns:
        bool: True if postable, False otherwise
    """
    account = db.query(models.MasterAccount).filter_by(id=account_id).first()
    if not account:
        return False
    return account.is_postable
