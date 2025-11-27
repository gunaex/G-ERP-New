"""
Seed data script for RetroEarthERP
Creates initial users, packages, and sample data
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine as db_engine, Base
from models import (
    User, CompanySettings, LicensePackage, MasterWarehouse,
    MasterItem, MasterBusinessPartner, ItemType, PartnerType,
    UserRole, ThemePreference, MasterBOM, BOMStatus, LocationMaster,
    MasterMachine, MachineStatus, PartnerAddress, AddressType, ConditionType,
    MasterAccount, AccountType, GLDetermination, WHTTaxCode, TaxGroup
)
from decimal import Decimal


from auth import get_password_hash

def create_seed_data():
    """Create initial seed data"""
    Base.metadata.create_all(bind=db_engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("Seed data already exists. Skipping...")
            return
        
        print("Creating seed data...")
        
        # 1. Create Users (using dynamic hashing)
        # Password: admin123, manager123, user123
        users = [
            User(
                username="admin",
                email="admin@retroearperp.com",
                password_hash=get_password_hash("admin123"),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                theme_preference=ThemePreference.RETRO_EARTH,
                language="en",
                is_active=True
            ),
            User(
                username="manager",
                email="manager@retroearperp.com",
                password_hash=get_password_hash("manager123"),
                full_name="Production Manager",
                role=UserRole.MANAGER,
                theme_preference=ThemePreference.RETRO_EARTH,
                language="th",
                is_active=True
            ),
            User(
                username="user",
                email="user@retroearperp.com",
                password_hash=get_password_hash("user123"),
                full_name="Regular User",
                role=UserRole.USER,
                theme_preference=ThemePreference.MODERN_CLEAN,
                language="en",
                is_active=True
            )
        ]
        db.add_all(users)
        db.commit()
        print("[OK] Created 3 users (admin/manager/user)")
        
        # 2. Create Company Settings
        company = CompanySettings(
            id=1,
            company_name="Demo Manufacturing Co., Ltd.",
            tax_id="1234567890123",
            address="123 Industrial Road, Bangkok, Thailand",
            phone="+66-2-123-4567",
            email="info@demomfg.com",
            base_currency="THB"
        )
        db.add(company)
        db.commit()
        print("[OK] Created company settings")
        
        # 3. Create License Packages
        packages = [
            LicensePackage(
                package_code="SMALL",
                package_name="Small Package",
                description="Basic ERP features: Inventory, Purchase, Sales",
                price=9900.00,
                is_active=True
            ),
            LicensePackage(
                package_code="STANDARD",
                package_name="Standard Package",
                description="Includes Production, BOM, and MRP",
                price=19900.00,
                is_active=True
            ),
            LicensePackage(
                package_code="ADVANCED",
                package_name="Advanced Package",
                description="Full features with AI capabilities",
                price=39900.00,
                is_active=True
            )
        ]
        db.add_all(packages)
        db.commit()
        print("[OK] Created 3 license packages")
        
        # 4. Create Warehouses
        warehouses = [
            MasterWarehouse(
                warehouse_code="WH01",
                warehouse_name="Main Warehouse",
                location="Building A, Floor 1",
                is_active=True
            ),
            MasterWarehouse(
                warehouse_code="WH02",
                warehouse_name="Raw Material Storage",
                location="Building B, Floor 1",
                is_active=True
            )
        ]
        db.add_all(warehouses)
        db.commit()
        print("[OK] Created 2 warehouses")
        
        # 4.5 Create Locations (for BOM production/storage)
        locations = [
            LocationMaster(
                warehouse_id=1,
                location_code="PROD-01",
                # location_name removed
                zone_type="WIP",  # Was location_type="PRODUCTION"
                condition_type=ConditionType.GENERAL,  # Was zone_type="AMBIENT"
                # is_active removed
            ),
            LocationMaster(
                warehouse_id=1,
                location_code="STOR-01",
                zone_type="FG",  # Was location_type="STORAGE"
                condition_type=ConditionType.GENERAL,
            ),
            LocationMaster(
                warehouse_id=2,
                location_code="RAW-01",
                zone_type="RM",  # Was location_type="STORAGE"
                condition_type=ConditionType.GENERAL,
            )
        ]
        db.add_all(locations)
        db.commit()
        print("[OK] Created 3 locations")

        # 4.6 Create Machines
        machines = [
            MasterMachine(
                machine_code="CNC-01",
                machine_name="CNC Milling Machine #1",
                location_id=1,  # PROD-01
                status=MachineStatus.ACTIVE,
                maintenance_interval_days=90,
                is_active=True
            ),
            MasterMachine(
                machine_code="ASSY-LINE-01",
                machine_name="Assembly Line #1",
                location_id=1,  # PROD-01
                status=MachineStatus.ACTIVE,
                maintenance_interval_days=30,
                is_active=True
            )
        ]
        db.add_all(machines)
        db.commit()
        print("[OK] Created 2 machines")

        
        # 5. Create Sample Items (Multi-level BOM structure)
        # Level 0: Finished Good
        # Level 1: WIP (Sub-assembly), Components
        # Level 2: Raw Materials
        items = [
            # Finished Good (Level 0)
            MasterItem(
                item_code="ENGINE-001",
                item_name="V8 Engine Assembly",
                item_type=ItemType.FINISHED_GOOD,
                unit_of_measure="PCS",
                standard_cost=25000.00,
                selling_price=45000.00,
                reorder_point=5,
                lead_time_days=30
            ),
            # WIP / Sub-Assembly (Level 1)
            MasterItem(
                item_code="PISTON-ASSY",
                item_name="Piston Sub-Assembly",
                item_type=ItemType.WIP,
                unit_of_measure="SET",
                standard_cost=4500.00,
                selling_price=0.00,
                reorder_point=20,
                lead_time_days=5
            ),
            MasterItem(
                item_code="CYLINDER-ASSY",
                item_name="Cylinder Block Assembly",
                item_type=ItemType.WIP,
                unit_of_measure="PCS",
                standard_cost=8000.00,
                selling_price=0.00,
                reorder_point=10,
                lead_time_days=7
            ),
            # Components (Level 1)
            MasterItem(
                item_code="CRANK-01",
                item_name="Crankshaft",
                item_type=ItemType.COMPONENT,
                unit_of_measure="PCS",
                standard_cost=1200.00,
                selling_price=1800.00,
                reorder_point=10,
                lead_time_days=5
            ),
            MasterItem(
                item_code="GASKET-01",
                item_name="Head Gasket",
                item_type=ItemType.COMPONENT,
                unit_of_measure="PCS",
                standard_cost=150.00,
                selling_price=250.00,
                reorder_point=50,
                lead_time_days=3
            ),
            # Raw Materials (Level 2)
            MasterItem(
                item_code="STEEL-001",
                item_name="Steel Plate 10mm",
                item_type=ItemType.RAW_MATERIAL,
                unit_of_measure="KG",
                standard_cost=50.00,
                selling_price=0.00,
                reorder_point=500,
                lead_time_days=14,
                lot_control=True  # Enable lot control
            ),
            MasterItem(
                item_code="ALUM-001",
                item_name="Aluminum Alloy",
                item_type=ItemType.RAW_MATERIAL,
                unit_of_measure="KG",
                standard_cost=120.00,
                selling_price=0.00,
                reorder_point=200,
                lead_time_days=10
            ),
            MasterItem(
                item_code="CAST-001",
                item_name="Cast Iron",
                item_type=ItemType.RAW_MATERIAL,
                unit_of_measure="KG",
                standard_cost=35.00,
                selling_price=0.00,
                reorder_point=1000,
                lead_time_days=14
            ),
            MasterItem(
                item_code="RUBBER-001",
                item_name="Rubber Sheet",
                item_type=ItemType.RAW_MATERIAL,
                unit_of_measure="M2",
                standard_cost=80.00,
                selling_price=0.00,
                reorder_point=100,
                lead_time_days=7
            ),
            # Packaging
            MasterItem(
                item_code="BOX-001",
                item_name="Engine Packaging Box",
                item_type=ItemType.PACKAGE,
                unit_of_measure="PCS",
                standard_cost=200.00,
                selling_price=0.00,
                reorder_point=50,
                lead_time_days=5
            )
        ]
        db.add_all(items)
        db.commit()
        print("[OK] Created 10 sample items (multi-level BOM structure)")
        
        # 6. Create Business Partners
        partners = [
            MasterBusinessPartner(
                partner_code="V001",
                partner_name="ABC Supplier Co., Ltd.",
                partner_type=PartnerType.VENDOR,
                tax_id="1111111111111",
                address="456 Supplier Street",
                city="Bangkok",
                province="Bangkok",
                postal_code="10100",
                country="Thailand",
                phone="+66-2-111-1111",
                email="sales@abcsupplier.com",
                payment_terms="Net 30",
                credit_limit=1000000.00,
                currency="THB"
            ),
            MasterBusinessPartner(
                partner_code="C001",
                partner_name="XYZ Customer Co., Ltd.",
                partner_type=PartnerType.CUSTOMER,
                tax_id="2222222222222",
                address="789 Customer Avenue",
                city="Bangkok",
                province="Bangkok",
                postal_code="10200",
                country="Thailand",
                phone="+66-2-222-2222",
                email="purchase@xyzcustomer.com",
                payment_terms="Net 30",
                credit_limit=500000.00,
                currency="THB"
            )
        ]
        db.add_all(partners)
        db.commit()
        print("[OK] Created 2 business partners")

        # 6.5 Create Partner Addresses
        partner_addresses = [
            PartnerAddress(
                partner_id=1,  # V001
                address_type=AddressType.BILL_TO,
                address="456 Supplier Street (Head Office)",
                city="Bangkok",
                is_primary=True
            ),
            PartnerAddress(
                partner_id=2,  # C001
                address_type=AddressType.SHIP_TO,
                address="789 Customer Warehouse 2",
                city="Samut Prakan",
                is_primary=False
            )
        ]
        db.add_all(partner_addresses)
        db.commit()
        print("[OK] Created partner addresses")

        
        # 7. Create Multi-Level BOM Structure
        # Get item IDs
        engine_item = db.query(MasterItem).filter(MasterItem.item_code == "ENGINE-001").first()
        piston_assy = db.query(MasterItem).filter(MasterItem.item_code == "PISTON-ASSY").first()
        cylinder_assy = db.query(MasterItem).filter(MasterItem.item_code == "CYLINDER-ASSY").first()
        crankshaft = db.query(MasterItem).filter(MasterItem.item_code == "CRANK-01").first()
        gasket = db.query(MasterItem).filter(MasterItem.item_code == "GASKET-01").first()
        steel = db.query(MasterItem).filter(MasterItem.item_code == "STEEL-001").first()
        aluminum = db.query(MasterItem).filter(MasterItem.item_code == "ALUM-001").first()
        cast_iron = db.query(MasterItem).filter(MasterItem.item_code == "CAST-001").first()
        rubber = db.query(MasterItem).filter(MasterItem.item_code == "RUBBER-001").first()
        box = db.query(MasterItem).filter(MasterItem.item_code == "BOX-001").first()
        
        prod_loc = db.query(LocationMaster).filter(LocationMaster.location_code == "PROD-01").first()
        stor_loc = db.query(LocationMaster).filter(LocationMaster.location_code == "STOR-01").first()
        
        # Get machine IDs
        cnc_machine = db.query(MasterMachine).filter(MasterMachine.machine_code == "CNC-01").first()
        assy_line = db.query(MasterMachine).filter(MasterMachine.machine_code == "ASSY-LINE-01").first()

        
        if engine_item and piston_assy and cylinder_assy:
            # Level 1 BOM: V8 Engine Assembly
            engine_bom = [
                MasterBOM(
                    parent_item_id=engine_item.id,
                    child_item_id=piston_assy.id,
                    bom_type="ASSEMBLY",
                    is_template=True,
                    sequence_order=1,
                    quantity=Decimal("8"),  # 8 pistons for V8
                    scrap_factor=Decimal("2"),  # 2% scrap
                    production_location_id=prod_loc.id if prod_loc else None,
                    storage_location_id=stor_loc.id if stor_loc else None,
                    revision=1,
                    status=BOMStatus.ACTIVE,
                    remark="8 piston assemblies per V8 engine",
                    machine_id=assy_line.id if assy_line else None,
                    production_lead_time_days=Decimal("0.5")
                ),
                MasterBOM(
                    parent_item_id=engine_item.id,
                    child_item_id=cylinder_assy.id,
                    bom_type="ASSEMBLY",
                    is_template=True,
                    sequence_order=2,
                    quantity=Decimal("1"),
                    scrap_factor=Decimal("1"),
                    production_location_id=prod_loc.id if prod_loc else None,
                    revision=1,
                    status=BOMStatus.ACTIVE,
                    remark="Main cylinder block"
                ),
                MasterBOM(
                    parent_item_id=engine_item.id,
                    child_item_id=crankshaft.id,
                    bom_type="ASSEMBLY",
                    is_template=True,
                    sequence_order=3,
                    quantity=Decimal("1"),
                    scrap_factor=Decimal("0"),
                    revision=1,
                    status=BOMStatus.ACTIVE,
                    remark="Main crankshaft"
                ),
                MasterBOM(
                    parent_item_id=engine_item.id,
                    child_item_id=gasket.id,
                    bom_type="ASSEMBLY",
                    is_template=True,
                    sequence_order=4,
                    quantity=Decimal("2"),
                    scrap_factor=Decimal("5"),  # Higher scrap for gaskets
                    revision=1,
                    status=BOMStatus.ACTIVE,
                    is_optional=False,
                    remark="Head gaskets"
                ),
                MasterBOM(
                    parent_item_id=engine_item.id,
                    child_item_id=box.id,
                    bom_type="ASSEMBLY",
                    is_template=True,
                    sequence_order=99,
                    quantity=Decimal("1"),
                    revision=1,
                    status=BOMStatus.ACTIVE,
                    is_optional=True,
                    remark="Optional packaging"
                )
            ]
            db.add_all(engine_bom)
            
            # Level 2 BOM: Piston Sub-Assembly
            piston_bom = [
                MasterBOM(
                    parent_item_id=piston_assy.id,
                    child_item_id=aluminum.id,
                    bom_type="ASSEMBLY",
                    is_template=True,
                    sequence_order=1,
                    quantity=Decimal("0.5"),  # 0.5 kg aluminum per piston
                    scrap_factor=Decimal("3"),
                    revision=1,
                    status=BOMStatus.ACTIVE,
                    remark="Aluminum for piston body"
                ),
                MasterBOM(
                    parent_item_id=piston_assy.id,
                    child_item_id=steel.id,
                    bom_type="ASSEMBLY",
                    is_template=True,
                    sequence_order=2,
                    quantity=Decimal("0.2"),  # 0.2 kg steel for rings
                    scrap_factor=Decimal("5"),
                    revision=1,
                    status=BOMStatus.ACTIVE,
                    remark="Steel for piston rings"
                )
            ]
            db.add_all(piston_bom)
            
            # Level 2 BOM: Cylinder Block Assembly
            cylinder_bom = [
                MasterBOM(
                    parent_item_id=cylinder_assy.id,
                    child_item_id=cast_iron.id,
                    bom_type="ASSEMBLY",
                    is_template=True,
                    sequence_order=1,
                    quantity=Decimal("25"),  # 25 kg cast iron
                    scrap_factor=Decimal("4"),
                    revision=1,
                    status=BOMStatus.ACTIVE,
                    remark="Cast iron for cylinder block"
                ),
                MasterBOM(
                    parent_item_id=cylinder_assy.id,
                    child_item_id=steel.id,
                    bom_type="ASSEMBLY",
                    is_template=True,
                    sequence_order=2,
                    quantity=Decimal("5"),  # 5 kg steel for sleeves
                    scrap_factor=Decimal("2"),
                    revision=1,
                    status=BOMStatus.ACTIVE,
                    remark="Steel for cylinder sleeves"
                ),
                MasterBOM(
                    parent_item_id=cylinder_assy.id,
                    child_item_id=rubber.id,
                    bom_type="ASSEMBLY",
                    is_template=True,
                    sequence_order=3,
                    quantity=Decimal("0.5"),  # 0.5 m2 rubber for seals
                    scrap_factor=Decimal("10"),  # Higher scrap for seals
                    revision=1,
                    status=BOMStatus.ACTIVE,
                    remark="Rubber for seals"
                )
            ]
            db.add_all(cylinder_bom)
            
            db.commit()
            print("[OK] Created multi-level BOM structure (3 levels)")

            # 9. Create Thai Chart of Accounts (Enhanced with Hierarchy)
            print("Creating Thai Chart of Accounts...")
            accounts = [
                # 1. ASSETS (สินทรัพย์)
                {"code": "10000", "name_th": "สินทรัพย์", "name_en": "Assets", "type": AccountType.ASSET, "level": 1, "postable": False, "balance": "DEBIT"},
                {"code": "11000", "name_th": "สินทรัพย์หมุนเวียน", "name_en": "Current Assets", "type": AccountType.ASSET, "level": 2, "postable": False, "balance": "DEBIT"},
                {"code": "11100", "name_th": "เงินสดและเงินฝากธนาคาร", "name_en": "Cash and Bank", "type": AccountType.ASSET, "level": 3, "postable": False, "balance": "DEBIT"},
                {"code": "11110", "name_th": "เงินสด", "name_en": "Cash on Hand", "type": AccountType.ASSET, "level": 4, "postable": True, "balance": "DEBIT"},
                {"code": "11120", "name_th": "เงินฝากธนาคาร", "name_en": "Bank Savings", "type": AccountType.ASSET, "level": 4, "postable": True, "balance": "DEBIT"},
                {"code": "11300", "name_th": "ลูกหนี้การค้า", "name_en": "Accounts Receivable", "type": AccountType.ASSET, "level": 3, "postable": True, "balance": "DEBIT"},
                {"code": "11400", "name_th": "สินค้าคงเหลือ", "name_en": "Inventory", "type": AccountType.ASSET, "level": 3, "postable": True, "balance": "DEBIT"},
                {"code": "11500", "name_th": "ภาษีซื้อ", "name_en": "Input VAT", "type": AccountType.ASSET, "level": 3, "postable": True, "balance": "DEBIT"},
                {"code": "12000", "name_th": "สินทรัพย์ไม่หมุนเวียน", "name_en": "Non-Current Assets", "type": AccountType.ASSET, "level": 2, "postable": False, "balance": "DEBIT"},
                {"code": "12100", "name_th": "ที่ดิน อาคาร และอุปกรณ์", "name_en": "Property, Plant & Equipment", "type": AccountType.ASSET, "level": 3, "postable": True, "balance": "DEBIT"},

                # 2. LIABILITIES (หนี้สิน)
                {"code": "20000", "name_th": "หนี้สิน", "name_en": "Liabilities", "type": AccountType.LIABILITY, "level": 1, "postable": False, "balance": "CREDIT"},
                {"code": "21000", "name_th": "หนี้สินหมุนเวียน", "name_en": "Current Liabilities", "type": AccountType.LIABILITY, "level": 2, "postable": False, "balance": "CREDIT"},
                {"code": "21200", "name_th": "เจ้าหนี้การค้า", "name_en": "Accounts Payable", "type": AccountType.LIABILITY, "level": 3, "postable": True, "balance": "CREDIT"},
                {"code": "21300", "name_th": "ภาษีขาย", "name_en": "Output VAT", "type": AccountType.LIABILITY, "level": 3, "postable": True, "balance": "CREDIT"},
                {"code": "21400", "name_th": "ภาษีหัก ณ ที่จ่ายค้างจ่าย", "name_en": "WHT Payable", "type": AccountType.LIABILITY, "level": 3, "postable": True, "balance": "CREDIT"},

                # 3. EQUITY (ส่วนของผู้ถือหุ้น)
                {"code": "30000", "name_th": "ส่วนของผู้ถือหุ้น", "name_en": "Equity", "type": AccountType.EQUITY, "level": 1, "postable": False, "balance": "CREDIT"},
                {"code": "31000", "name_th": "ทุนจดทะเบียน", "name_en": "Share Capital", "type": AccountType.EQUITY, "level": 2, "postable": True, "balance": "CREDIT"},
                {"code": "32000", "name_th": "กำไรสะสม", "name_en": "Retained Earnings", "type": AccountType.EQUITY, "level": 2, "postable": True, "balance": "CREDIT"},

                # 4. REVENUE (รายได้)
                {"code": "40000", "name_th": "รายได้", "name_en": "Revenue", "type": AccountType.REVENUE, "level": 1, "postable": False, "balance": "CREDIT"},
                {"code": "41000", "name_th": "รายได้จากการขาย", "name_en": "Sales Revenue", "type": AccountType.REVENUE, "level": 2, "postable": True, "balance": "CREDIT"},
                {"code": "42000", "name_th": "รายได้อื่น", "name_en": "Other Income", "type": AccountType.REVENUE, "level": 2, "postable": True, "balance": "CREDIT"},

                # 5. EXPENSES (ค่าใช้จ่าย)
                {"code": "50000", "name_th": "ค่าใช้จ่าย", "name_en": "Expenses", "type": AccountType.EXPENSE, "level": 1, "postable": False, "balance": "DEBIT"},
                {"code": "51000", "name_th": "ต้นทุนขาย", "name_en": "Cost of Goods Sold", "type": AccountType.EXPENSE, "level": 2, "postable": True, "balance": "DEBIT"},
                {"code": "52000", "name_th": "ค่าใช้จ่ายในการขาย", "name_en": "Selling Expenses", "type": AccountType.EXPENSE, "level": 2, "postable": True, "balance": "DEBIT"},
                {"code": "53000", "name_th": "ค่าใช้จ่ายในการบริหาร", "name_en": "Administrative Expenses", "type": AccountType.EXPENSE, "level": 2, "postable": True, "balance": "DEBIT"},
            ]
            
            for acc in accounts:
                db_acc = MasterAccount(
                    code=acc["code"],
                    name_th=acc["name_th"],
                    name_en=acc["name_en"],
                    account_type=acc["type"],
                    account_level=acc["level"],
                    is_postable=acc["postable"],
                    normal_balance=acc["balance"],
                    is_active=True
                )
                db.add(db_acc)
            
            db.commit()
            print(f"[OK] Created {len(accounts)} Thai Chart of Accounts")

            # 10. Create GL Determination Configurations
            print("Creating GL Determination configurations...")
            
            # Helper to get account ID by code
            def get_account_id(code):
                return db.query(MasterAccount).filter_by(code=code).first().id
            
            gl_configs = [
                {"process": "SALES_REVENUE", "account_code": "41000", "desc": "Default Sales Revenue Account"},
                {"process": "SALES_VAT", "account_code": "21300", "desc": "Output VAT Account"},
                {"process": "AR_DOMESTIC", "account_code": "11300", "desc": "Accounts Receivable (Domestic)"},
                {"process": "COST_OF_GOODS", "account_code": "51000", "desc": "Cost of Goods Sold"},
                {"process": "INVENTORY_ASSET", "account_code": "11400", "desc": "Inventory Asset Account"},
                {"process": "AP_DOMESTIC", "account_code": "21200", "desc": "Accounts Payable (Domestic)"},
                {"process": "INPUT_VAT", "account_code": "11500", "desc": "Input VAT Account"},
                {"process": "WHT_PAYABLE", "account_code": "21400", "desc": "Withholding Tax Payable"},
                {"process": "BANK_ACCOUNT", "account_code": "11120", "desc": "Default Bank Account"},
            ]
            
            for config in gl_configs:
                gl_det = GLDetermination(
                    profile_name="Default",
                    process_key=config["process"],
                    account_id=get_account_id(config["account_code"]),
                    description=config["desc"]
                )
                db.add(gl_det)
            
            db.commit()
            print(f"[OK] Created {len(gl_configs)} GL Determination configurations")

            # 11. Create WHT Tax Codes (Thai Standard)
            print("Creating WHT Tax Codes...")
            wht_codes = [
                {"code": "W1", "rate": 1.00, "income_type": "40(1)", "desc_th": "เงินเดือน ค่าจ้าง", "desc_en": "Salary and Wages"},
                {"code": "W3", "rate": 3.00, "income_type": "40(2)", "desc_th": "ค่าบริการวิชาชีพ", "desc_en": "Professional Service Fees"},
                {"code": "W5", "rate": 5.00, "income_type": "40(3)", "desc_th": "ค่าเช่า", "desc_en": "Rental Income"},
                {"code": "W10", "rate": 10.00, "income_type": "40(4)(a)", "desc_th": "เงินปันผล", "desc_en": "Dividends"},
            ]
            
            for wht in wht_codes:
                wht_code = WHTTaxCode(
                    code=wht["code"],
                    rate=Decimal(str(wht["rate"])),
                    income_type_code=wht["income_type"],
                    description_th=wht["desc_th"],
                    description_en=wht["desc_en"],
                    is_active=True
                )
                db.add(wht_code)
            
            db.commit()
            print(f"[OK] Created {len(wht_codes)} WHT Tax Codes")

            # 12. Create VAT Tax Groups
            print("Creating VAT Tax Groups...")
            tax_groups = [
                {"code": "V7", "name": "VAT 7%", "rate": 7.00, "type": "OUTPUT"},
                {"code": "V7I", "name": "Input VAT 7%", "rate": 7.00, "type": "INPUT"},
                {"code": "Z0", "name": "Zero Rated", "rate": 0.00, "type": "OUTPUT"},
                {"code": "E0", "name": "Exempt", "rate": 0.00, "type": "OUTPUT"},
            ]
            
            for tg in tax_groups:
                tax_group = TaxGroup(
                    code=tg["code"],
                    name=tg["name"],
                    rate=Decimal(str(tg["rate"])),
                    tax_type=tg["type"],
                    is_active=True
                )
                db.add(tax_group)
            
            db.commit()
            print(f"[OK] Created {len(tax_groups)} VAT Tax Groups")
        
        print("\n[SUCCESS] Seed data created successfully!")
        print("\nLogin credentials:")
        print("  Admin:   username=admin,   password=admin123")
        print("  Manager: username=manager, password=manager123")
        print("  User:    username=user,    password=user123")
        print("\nBOM Test Data:")
        print("  ENGINE-001 (FG) -> PISTON-ASSY (WIP) -> ALUM-001, STEEL-001 (RM)")
        print("                  -> CYLINDER-ASSY (WIP) -> CAST-001, STEEL-001, RUBBER-001 (RM)")
        print("                  -> CRANK-01, GASKET-01 (Components)")
        print("                  -> BOX-001 (Optional Packaging)")
        print("\nTest BOM Explosion at: http://localhost:8000/docs#/BOM/explode_bom_simple_api_bom_explode__parent_item_id__get")
        
    except Exception as e:
        print(f"[ERROR] Error creating seed data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_seed_data()
