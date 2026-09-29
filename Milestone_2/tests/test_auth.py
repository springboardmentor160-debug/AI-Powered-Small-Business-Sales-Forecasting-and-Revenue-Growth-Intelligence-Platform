"""
Unit & Integration Tests for Authentication & RBAC System (Milestone 2)
"""

import unittest
from fastapi.testclient import TestClient
from Milestone_2.backend.main import app
from Milestone_2.backend.auth import hash_password, verify_password

class TestAuthenticationAndRBAC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_password_hashing(self):
        plain = "MySecretPassword123!"
        hashed = hash_password(plain)
        self.assertNotEqual(plain, hashed)
        self.assertTrue(verify_password(plain, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_02_login_success(self):
        res = self.client.post("/api/auth/login", json={
            "email": "owner@marketmind.ai",
            "password": "OwnerPass123!"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["role"], "Business Owner")

    def test_03_login_invalid_password(self):
        res = self.client.post("/api/auth/login", json={
            "email": "owner@marketmind.ai",
            "password": "WrongPassword!"
        })
        self.assertEqual(res.status_code, 401)

    def test_04_rbac_business_owner_dashboard(self):
        # 1. Login as Business Owner
        login_res = self.client.post("/api/auth/login", json={
            "email": "owner@marketmind.ai",
            "password": "OwnerPass123!"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Access Business Owner dashboard
        res = self.client.get("/api/dashboard/business-owner", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["role"], "Business Owner")
        self.assertIn("kpis", data)
        self.assertIn("insights", data)

    def test_05_rbac_forbidden_access(self):
        # Login as Sales Executive
        login_res = self.client.post("/api/auth/login", json={
            "email": "sales@marketmind.ai",
            "password": "SalesPass123!"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Sales Executive trying to access Admin Users list should be 403 Forbidden
        res = self.client.get("/api/admin/users", headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_06_admin_user_creation(self):
        import uuid
        test_email = f"newmanager_{uuid.uuid4().hex[:6]}@marketmind.ai"
        
        # Login as Administrator
        login_res = self.client.post("/api/auth/login", json={
            "email": "admin@marketmind.ai",
            "password": "AdminPass123!"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create new user
        res = self.client.post("/api/admin/users", headers=headers, json={
            "name": "New Manager",
            "email": test_email,
            "role": "Store Manager",
            "password": "NewManagerPass123!"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["email"], test_email)

        # Verify new user can log in
        login_new = self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": "NewManagerPass123!"
        })
        self.assertEqual(login_new.status_code, 200)


if __name__ == "__main__":
    unittest.main()
