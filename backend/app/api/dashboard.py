from fastapi import APIRouter, Depends
from app.auth.database_models import User
from app.auth.dependencies import require_permission

router = APIRouter(
    prefix="/api",
    tags=["Dashboard"]
)


@router.get("/dashboard")
def get_dashboard(
    current_user: User = Depends(
        require_permission("dashboard:view")
    )
):
    user_roles = [role.name for role in current_user.roles]

    # Business Owner
    if "Business Owner" in user_roles:
        return {
            "role": "Business Owner",
            "dashboard": "business",
            "message": "Welcome to the Business Owner dashboard",
            "total_sales": 125000,
            "total_orders": 3200,
            "total_customers": 850,
            "total_products": 450
        }

    # Store Manager
    if "Store Manager" in user_roles:
        return {
            "role": "Store Manager",
            "dashboard": "store",
            "message": "Welcome to the Store Manager dashboard",
            "total_sales": 95000,
            "total_orders": 2400,
            "total_products": 380
        }

    # Sales Executive
    if "Sales Executive" in user_roles:
        return {
            "role": "Sales Executive",
            "dashboard": "sales",
            "message": "Welcome to the Sales Executive dashboard",
            "total_sales": 45000,
            "total_orders": 1200,
            "total_customers": 500
        }

    # Administrator
    if "Administrator" in user_roles:
        return {
            "role": "Administrator",
            "dashboard": "admin",
            "message": "Welcome to the Administrator dashboard",
            "system_status": "Operational",
            "total_users": 1
        }

    return {
        "role": "Unknown",
        "dashboard": "none",
        "message": "No dashboard access assigned"
    }