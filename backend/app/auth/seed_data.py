from app.database import SessionLocal
from app.auth.database_models import Role, Permission


ROLES = [
    {
        "name": "Business Owner",
        "description": "Full access to business operations and analytics"
    },
    {
        "name": "Store Manager",
        "description": "Access to store-level operations and management"
    },
    {
        "name": "Sales Executive",
        "description": "Access to sales and customer-related functions"
    },
    {
        "name": "Administrator",
        "description": "System administration and user management"
    }
]


PERMISSIONS = [
    ("dashboard:view", "View dashboard"),

    ("sales:view", "View sales"),
    ("sales:create", "Create sales"),

    ("inventory:view", "View inventory"),
    ("inventory:update", "Update inventory"),

    ("customers:view", "View customers"),

    ("reports:view", "View reports"),

    ("users:view", "View users"),
    ("users:create", "Create users"),
    ("users:update", "Update users"),

    ("roles:view", "View roles"),
    ("roles:update", "Update roles"),

    ("permissions:view", "View permissions"),
]


ROLE_PERMISSIONS = {
    "Business Owner": [
        "dashboard:view",
        "sales:view",
        "sales:create",
        "inventory:view",
        "inventory:update",
        "customers:view",
        "reports:view",
        "users:view",
    ],

    "Store Manager": [
        "dashboard:view",
        "sales:view",
        "sales:create",
        "inventory:view",
        "inventory:update",
        "customers:view",
        "reports:view",
    ],

    "Sales Executive": [
        "dashboard:view",
        "sales:view",
        "sales:create",
        "customers:view",
    ],

    "Administrator": [
        "dashboard:view",
        "sales:view",
        "sales:create",
        "inventory:view",
        "inventory:update",
        "customers:view",
        "reports:view",
        "users:view",
        "users:create",
        "users:update",
        "roles:view",
        "roles:update",
        "permissions:view",
    ],
}


def seed_roles(db):
    for role_data in ROLES:
        role = db.query(Role).filter(
            Role.name == role_data["name"]
        ).first()

        if not role:
            role = Role(**role_data)
            db.add(role)

    db.commit()


def seed_permissions(db):
    for name, description in PERMISSIONS:
        permission = db.query(Permission).filter(
            Permission.name == name
        ).first()

        if not permission:
            permission = Permission(
                name=name,
                description=description
            )
            db.add(permission)

    db.commit()


def seed_role_permissions(db):
    for role_name, permission_names in ROLE_PERMISSIONS.items():

        role = db.query(Role).filter(
            Role.name == role_name
        ).first()

        if not role:
            continue

        for permission_name in permission_names:

            permission = db.query(Permission).filter(
                Permission.name == permission_name
            ).first()

            if permission and permission not in role.permissions:
                role.permissions.append(permission)

    db.commit()


def seed_database():

    db = SessionLocal()

    try:
        seed_roles(db)
        seed_permissions(db)
        seed_role_permissions(db)

        print("Roles seeded successfully.")
        print("Permissions seeded successfully.")
        print("Role-permission assignments completed.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()