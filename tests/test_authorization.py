import time

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.auth import ALGORITHM, SECRET_KEY
from backend.database import Base, get_db
from backend.main import app
import backend.routers.inventory as inventory_router
import backend.routers.invoices as invoices_router


# ============================================================
# TEST DATABASE AND CLIENT
# ============================================================

@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


# ============================================================
# JWT TEST HELPER
# ============================================================

def make_token(role="admin", expires_in=300):
    return jwt.encode(
        {
            "sub": "authorization-test@example.com",
            "role": role,
            "exp": int(time.time()) + expires_in,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def auth_headers(role="admin", expires_in=300):
    token = make_token(
        role=role,
        expires_in=expires_in,
    )

    return {
        "Authorization": f"Bearer {token}",
    }


# ============================================================
# AUTHENTICATION FAILURE TESTS
# ============================================================

@pytest.mark.parametrize(
    "endpoint",
    [
        "/admin/users",
        "/sales/summary",
        "/forecast/demand",
        "/forecast/revenue",
        "/forecast/models",
        "/inventory/preview",
        "/invoices/view",
        "/segments",
    ],
)
def test_protected_endpoints_reject_missing_token(
    client,
    endpoint,
):
    response = client.get(endpoint)

    # FastAPI validates the required header before the
    # authentication dependency can execute.
    assert response.status_code == 422


@pytest.mark.parametrize(
    "authorization",
    [
        "Basic abc123",
        "Bearer ",
        "Bearer invalid-token",
    ],
)
def test_protected_endpoint_rejects_invalid_authorization(
    client,
    authorization,
):
    response = client.get(
        "/admin/users",
        headers={"Authorization": authorization},
    )

    assert response.status_code == 401


def test_protected_endpoint_rejects_expired_token(client):
    headers = auth_headers(
        role="admin",
        expires_in=-60,
    )

    response = client.get(
        "/admin/users",
        headers=headers,
    )

    assert response.status_code == 401


# ============================================================
# ROLE-BASED ACCESS CONTROL: ADMIN USER DIRECTORY
# ============================================================

@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        ("admin", 200),
        ("business_owner", 403),
        ("store_manager", 403),
        ("sales_executive", 403),
    ],
)
def test_admin_user_directory_permissions(
    client,
    role,
    expected_status,
):
    response = client.get(
        "/admin/users",
        headers=auth_headers(role),
    )

    assert response.status_code == expected_status


# ============================================================
# ROLE-BASED ACCESS CONTROL: SALES SUMMARY
# ============================================================

@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        ("business_owner", 200),
        ("admin", 200),
        ("store_manager", 403),
        ("sales_executive", 403),
    ],
)
def test_sales_summary_permissions(
    client,
    role,
    expected_status,
):
    response = client.get(
        "/sales/summary",
        headers=auth_headers(role),
    )

    assert response.status_code == expected_status


# ============================================================
# ROLE-BASED ACCESS CONTROL: FORECAST ENDPOINTS
# ============================================================

@pytest.mark.parametrize(
    "endpoint",
    [
        "/forecast/demand",
        "/forecast/revenue",
        "/forecast/models",
    ],
)
@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        ("business_owner", 200),
        ("admin", 200),
        ("store_manager", 200),
        ("sales_executive", 403),
    ],
)
def test_forecast_permissions(
    client,
    endpoint,
    role,
    expected_status,
):
    response = client.get(
        endpoint,
        headers=auth_headers(role),
    )

    assert response.status_code == expected_status


# ============================================================
# ROLE-BASED ACCESS CONTROL: CUSTOMER SEGMENTS
# ============================================================

@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        ("business_owner", 200),
        ("admin", 200),
        ("store_manager", 200),
        ("sales_executive", 403),
    ],
)
def test_customer_segment_permissions(
    client,
    role,
    expected_status,
):
    response = client.get(
        "/segments",
        headers=auth_headers(role),
    )

    assert response.status_code == expected_status


# ============================================================
# ROLE-BASED ACCESS CONTROL: INVENTORY PREVIEW
# ============================================================

@pytest.mark.parametrize(
    "role",
    [
        "business_owner",
        "admin",
        "store_manager",
        "sales_executive",
    ],
)
def test_all_supported_roles_can_access_inventory_preview(
    client,
    monkeypatch,
    role,
):
    # Avoid dependence on actual UCI CSV files.
    monkeypatch.setattr(
        inventory_router,
        "generate_inventory_preview",
        lambda db: {"items": []},
    )

    response = client.get(
        "/inventory/preview",
        headers=auth_headers(role),
    )

    assert response.status_code == 200


# ============================================================
# ROLE-BASED ACCESS CONTROL: INVOICE VIEWING
# ============================================================

@pytest.mark.parametrize(
    "role",
    [
        "business_owner",
        "admin",
        "store_manager",
        "sales_executive",
    ],
)
def test_all_supported_roles_can_view_invoices(
    client,
    role,
    monkeypatch,
):
    monkeypatch.setattr(
        invoices_router,
        "load_invoice_records",
        lambda db: [],
    )

    response = client.get(
        "/invoices/view",
        headers=auth_headers(role),
    )

    assert response.status_code == 200


# ============================================================
# ROLE-BASED ACCESS CONTROL: INVOICE CREATION
# ============================================================

INVOICE_PAYLOAD = {
    "customer_name": "Test Customer",
    "product_name": "Test Product",
    "quantity": 2,
    "unit_price": 100.0,
    "payment_status": "Pending",
}


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        ("sales_executive", 200),
        ("admin", 200),
        ("business_owner", 403),
        ("store_manager", 403),
    ],
)
def test_invoice_creation_permissions(
    client,
    monkeypatch,
    role,
    expected_status,
):
    # The service is mocked so the test focuses on
    # authorization rather than invoice persistence.
    monkeypatch.setattr(
        invoices_router,
        "create_invoice_record",
        lambda db, **kwargs: {
            "invoice_id": "TEST-INV-001",
        },
    )

    response = client.post(
        "/invoices/create",
        headers=auth_headers(role),
        json=INVOICE_PAYLOAD,
    )

    assert response.status_code == expected_status