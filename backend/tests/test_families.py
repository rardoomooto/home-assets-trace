import pytest
from fastapi.testclient import TestClient
from app.models import User, Family, FamilyMember
from app.auth import get_password_hash, create_access_token
from conftest import TestingSessionLocal


@pytest.fixture
def test_family(test_user):
    """Create a test family"""
    db = TestingSessionLocal()
    family = Family(name="Test Family", is_default=False)
    db.add(family)
    db.commit()
    db.refresh(family)
    
    # Add user as owner
    member = FamilyMember(
        family_id=family.id,
        user_id=test_user.id,
        role="owner"
    )
    db.add(member)
    db.commit()
    family_id = family.id
    db.close()
    return family_id


@pytest.fixture
def test_families(test_user):
    """Create multiple test families"""
    db = TestingSessionLocal()
    family1 = Family(name="Family 1", is_default=False)
    family2 = Family(name="Family 2", is_default=False)
    db.add(family1)
    db.add(family2)
    db.commit()
    db.refresh(family1)
    db.refresh(family2)
    
    # Add user as member of both families
    member1 = FamilyMember(
        family_id=family1.id,
        user_id=test_user.id,
        role="owner"
    )
    member2 = FamilyMember(
        family_id=family2.id,
        user_id=test_user.id,
        role="member"
    )
    db.add(member1)
    db.add(member2)
    db.commit()
    family1_id = family1.id
    family2_id = family2.id
    db.close()
    return {"family1": family1_id, "family2": family2_id}


class TestFamilyAPI:
    """Test family API endpoints"""
    
    def test_create_family(self, client, auth_headers):
        """Test creating a new family"""
        response = client.post(
            "/api/families",
            headers=auth_headers,
            json={"name": "My New Family"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My New Family"
        assert data["is_default"] is False
        assert "id" in data
        assert "created_at" in data
        assert len(data["members"]) == 1
        assert data["members"][0]["role"] == "owner"
        assert data["members"][0]["username"] == "testuser"
    
    def test_create_family_without_auth(self, client):
        """Test creating family without authentication"""
        response = client.post(
            "/api/families",
            json={"name": "Unauthorized Family"}
        )
        assert response.status_code == 401
    
    def test_get_families(self, client, auth_headers, test_families):
        """Test getting user's families"""
        response = client.get("/api/families", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "families" in data
        families = data["families"]
        assert len(families) == 2
        family_names = [f["name"] for f in families]
        assert "Family 1" in family_names
        assert "Family 2" in family_names
    
    def test_get_family(self, client, auth_headers, test_family):
        """Test getting a specific family"""
        response = client.get(
            f"/api/families/{test_family}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Family"
        assert data["id"] == test_family
        assert len(data["members"]) == 1
    
    def test_get_family_not_member(self, client, test_user):
        """Test getting family when user is not a member"""
        # Create another user and family
        db = TestingSessionLocal()
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("otherpass")
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)
        
        other_family = Family(name="Other Family")
        db.add(other_family)
        db.commit()
        db.refresh(other_family)
        
        member = FamilyMember(
            family_id=other_family.id,
            user_id=other_user.id,
            role="owner"
        )
        db.add(member)
        db.commit()
        
        # Create token for test_user
        token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            f"/api/families/{other_family.id}",
            headers=headers
        )
        assert response.status_code == 404
        db.close()
    
    def test_update_family(self, client, auth_headers, test_family):
        """Test updating family name"""
        response = client.put(
            f"/api/families/{test_family}",
            headers=auth_headers,
            json={"name": "Updated Family Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Family Name"
    
    def test_update_family_not_admin(self, client, test_user):
        """Test updating family when user is not admin/owner"""
        # Create another user and family
        db = TestingSessionLocal()
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("otherpass")
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)
        
        family = Family(name="Test Family")
        db.add(family)
        db.commit()
        db.refresh(family)
        
        # Add other_user as owner
        member1 = FamilyMember(
            family_id=family.id,
            user_id=other_user.id,
            role="owner"
        )
        # Add test_user as member
        member2 = FamilyMember(
            family_id=family.id,
            user_id=test_user.id,
            role="member"
        )
        db.add(member1)
        db.add(member2)
        db.commit()
        
        # Create token for test_user
        token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.put(
            f"/api/families/{family.id}",
            headers=headers,
            json={"name": "Trying to Update"}
        )
        assert response.status_code == 403
        db.close()
    
    def test_delete_family(self, client, auth_headers, test_family):
        """Test deleting a family"""
        response = client.delete(
            f"/api/families/{test_family}",
            headers=auth_headers
        )
        assert response.status_code == 204
        
        # Verify family is deleted
        response = client.get(
            f"/api/families/{test_family}",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_delete_family_not_owner(self, client, test_user):
        """Test deleting family when user is not owner"""
        # Create another user and family
        db = TestingSessionLocal()
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("otherpass")
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)
        
        family = Family(name="Test Family")
        db.add(family)
        db.commit()
        db.refresh(family)
        
        # Add other_user as owner
        member1 = FamilyMember(
            family_id=family.id,
            user_id=other_user.id,
            role="owner"
        )
        # Add test_user as member
        member2 = FamilyMember(
            family_id=family.id,
            user_id=test_user.id,
            role="member"
        )
        db.add(member1)
        db.add(member2)
        db.commit()
        
        # Create token for test_user
        token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(
            f"/api/families/{family.id}",
            headers=headers
        )
        assert response.status_code == 403
        db.close()
    
    def test_add_member(self, client, auth_headers, test_family):
        """Test adding a member to family"""
        # Create another user
        db = TestingSessionLocal()
        other_user = User(
            username="newmember",
            email="newmember@example.com",
            hashed_password=get_password_hash("newpass")
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)
        db.close()
        
        response = client.post(
            f"/api/families/{test_family}/members",
            headers=auth_headers,
            json={"username": "newmember", "role": "member"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newmember"
        assert data["role"] == "member"
    
    def test_add_member_not_admin(self, client, test_user):
        """Test adding member when user is not admin/owner"""
        # Create another user and family
        db = TestingSessionLocal()
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("otherpass")
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)
        
        family = Family(name="Test Family")
        db.add(family)
        db.commit()
        db.refresh(family)
        
        # Add other_user as owner
        member1 = FamilyMember(
            family_id=family.id,
            user_id=other_user.id,
            role="owner"
        )
        # Add test_user as member
        member2 = FamilyMember(
            family_id=family.id,
            user_id=test_user.id,
            role="member"
        )
        db.add(member1)
        db.add(member2)
        db.commit()
        
        # Create token for test_user
        token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a third user to add
        third_user = User(
            username="thirduser",
            email="third@example.com",
            hashed_password=get_password_hash("thirdpass")
        )
        db.add(third_user)
        db.commit()
        
        response = client.post(
            f"/api/families/{family.id}/members",
            headers=headers,
            json={"username": "thirduser", "role": "member"}
        )
        assert response.status_code == 403
        db.close()
    
    def test_remove_member(self, client, auth_headers, test_family):
        """Test removing a member from family"""
        # Add another member first
        db = TestingSessionLocal()
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("otherpass")
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)
        
        member = FamilyMember(
            family_id=test_family,
            user_id=other_user.id,
            role="member"
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        other_user_id = other_user.id
        db.close()
        
        response = client.delete(
            f"/api/families/{test_family}/members/{other_user_id}",
            headers=auth_headers
        )
        assert response.status_code == 204
    
    def test_remove_member_self(self, client, test_user, test_family):
        """Test removing self from family"""
        # Create token for test_user
        token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(
            f"/api/families/{test_family}/members/{test_user.id}",
            headers=headers
        )
        # Should succeed (owner can leave)
        assert response.status_code == 204
    
    def test_remove_member_not_admin(self, client, test_user):
        """Test removing member when user is not admin/owner"""
        # Create another user and family
        db = TestingSessionLocal()
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=get_password_hash("otherpass")
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)
        
        third_user = User(
            username="thirduser",
            email="third@example.com",
            hashed_password=get_password_hash("thirdpass")
        )
        db.add(third_user)
        db.commit()
        db.refresh(third_user)
        
        family = Family(name="Test Family")
        db.add(family)
        db.commit()
        db.refresh(family)
        
        # Add other_user as owner
        member1 = FamilyMember(
            family_id=family.id,
            user_id=other_user.id,
            role="owner"
        )
        # Add test_user as member
        member2 = FamilyMember(
            family_id=family.id,
            user_id=test_user.id,
            role="member"
        )
        # Add third_user as member
        member3 = FamilyMember(
            family_id=family.id,
            user_id=third_user.id,
            role="member"
        )
        db.add(member1)
        db.add(member2)
        db.add(member3)
        db.commit()
        
        # Create token for test_user
        token = create_access_token(data={"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to remove third_user (not allowed)
        response = client.delete(
            f"/api/families/{family.id}/members/{third_user.id}",
            headers=headers
        )
        assert response.status_code == 403
        db.close()