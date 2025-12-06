"""
Permission Control Tests for MiPastel Application

Tests for:
- Admin can access all branches
- Branch users can only access their branch
- Cross-branch access denial
- Permission edge cases
"""

import pytest
from fastapi import HTTPException
from unittest.mock import Mock

from api.auth import (
    verificar_permiso_sucursal,
    requiere_permiso_sucursal
)


class TestAdminPermissions:
    """Test admin user permissions."""
    
    def test_admin_can_access_all_branches(self):
        """Test that admin can access any branch."""
        admin_data = {
            "username": "admin",
            "rol": "admin",
            "sucursal": None
        }
        
        branches = [
            "Jutiapa 1", "Jutiapa 2", "Jutiapa 3",
            "Progreso", "Quesada", "Acatempa",
            "Yupiltepeque", "Atescatempa", "Adelanto",
            "Jeréz", "Comapa", "Carina"
        ]
        
        for branch in branches:
            assert verificar_permiso_sucursal(admin_data, branch) is True
    
    def test_admin_can_access_nonexistent_branch(self):
        """Test that admin can access even non-existent branches."""
        admin_data = {
            "username": "admin",
            "rol": "admin",
            "sucursal": None
        }
        
        assert verificar_permiso_sucursal(admin_data, "Nonexistent Branch") is True
    
    def test_admin_permission_requirement_never_raises(self):
        """Test that admin never gets permission denied."""
        admin_data = {
            "username": "admin",
            "rol": "admin",
            "sucursal": None
        }
        
        # Should not raise exception for any branch
        requiere_permiso_sucursal(admin_data, "Jutiapa 1")
        requiere_permiso_sucursal(admin_data, "Any Branch")
        requiere_permiso_sucursal(admin_data, "")


class TestBranchUserPermissions:
    """Test branch user permissions."""
    
    def test_user_can_access_own_branch(self):
        """Test that user can access their own branch."""
        user_data = {
            "username": "jutiapa1",
            "rol": "sucursal",
            "sucursal": "Jutiapa 1"
        }
        
        assert verificar_permiso_sucursal(user_data, "Jutiapa 1") is True
    
    def test_user_cannot_access_other_branches(self):
        """Test that user cannot access other branches."""
        user_data = {
            "username": "jutiapa1",
            "rol": "sucursal",
            "sucursal": "Jutiapa 1"
        }
        
        other_branches = [
            "Jutiapa 2", "Jutiapa 3", "Progreso",
            "Quesada", "Acatempa", "Yupiltepeque"
        ]
        
        for branch in other_branches:
            assert verificar_permiso_sucursal(user_data, branch) is False
    
    def test_user_permission_requirement_own_branch(self):
        """Test permission requirement for own branch."""
        user_data = {
            "username": "jutiapa1",
            "rol": "sucursal",
            "sucursal": "Jutiapa 1"
        }
        
        # Should not raise exception
        requiere_permiso_sucursal(user_data, "Jutiapa 1")
    
    def test_user_permission_requirement_other_branch(self):
        """Test permission requirement for other branch."""
        user_data = {
            "username": "jutiapa1",
            "rol": "sucursal",
            "sucursal": "Jutiapa 1"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            requiere_permiso_sucursal(user_data, "Jutiapa 2")
        
        assert exc_info.value.status_code == 403
        assert "No tiene permiso" in exc_info.value.detail


class TestCrossBranchAccess:
    """Test cross-branch access scenarios."""
    
    def test_jutiapa1_cannot_access_jutiapa2(self):
        """Test that Jutiapa 1 user cannot access Jutiapa 2 data."""
        user_data = {
            "username": "jutiapa1",
            "rol": "sucursal",
            "sucursal": "Jutiapa 1"
        }
        
        assert verificar_permiso_sucursal(user_data, "Jutiapa 2") is False
    
    def test_progreso_cannot_access_quesada(self):
        """Test that Progreso user cannot access Quesada data."""
        user_data = {
            "username": "progreso",
            "rol": "sucursal",
            "sucursal": "Progreso"
        }
        
        assert verificar_permiso_sucursal(user_data, "Quesada") is False
    
    def test_all_branches_isolated(self):
        """Test that all branches are isolated from each other."""
        branches = [
            "Jutiapa 1", "Jutiapa 2", "Jutiapa 3",
            "Progreso", "Quesada", "Acatempa"
        ]
        
        for branch1 in branches:
            user_data = {
                "username": branch1.lower().replace(" ", ""),
                "rol": "sucursal",
                "sucursal": branch1
            }
            
            for branch2 in branches:
                if branch1 == branch2:
                    assert verificar_permiso_sucursal(user_data, branch2) is True
                else:
                    assert verificar_permiso_sucursal(user_data, branch2) is False


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_empty_sucursal_string(self):
        """Test permission check with empty sucursal string."""
        user_data = {
            "username": "test",
            "rol": "sucursal",
            "sucursal": ""
        }
        
        assert verificar_permiso_sucursal(user_data, "") is True
        assert verificar_permiso_sucursal(user_data, "Jutiapa 1") is False
    
    def test_none_sucursal_non_admin(self):
        """Test permission check with None sucursal for non-admin."""
        user_data = {
            "username": "test",
            "rol": "sucursal",
            "sucursal": None
        }
        
        # None should only match None
        assert verificar_permiso_sucursal(user_data, None) is True
        assert verificar_permiso_sucursal(user_data, "Jutiapa 1") is False
    
    def test_case_sensitive_branch_names(self):
        """Test that branch names are case-sensitive."""
        user_data = {
            "username": "jutiapa1",
            "rol": "sucursal",
            "sucursal": "Jutiapa 1"
        }
        
        # Exact match should work
        assert verificar_permiso_sucursal(user_data, "Jutiapa 1") is True
        
        # Different case should not match
        assert verificar_permiso_sucursal(user_data, "jutiapa 1") is False
        assert verificar_permiso_sucursal(user_data, "JUTIAPA 1") is False
    
    def test_whitespace_in_branch_names(self):
        """Test that whitespace matters in branch names."""
        user_data = {
            "username": "jutiapa1",
            "rol": "sucursal",
            "sucursal": "Jutiapa 1"
        }
        
        # Exact match should work
        assert verificar_permiso_sucursal(user_data, "Jutiapa 1") is True
        
        # Extra whitespace should not match
        assert verificar_permiso_sucursal(user_data, "Jutiapa  1") is False
        assert verificar_permiso_sucursal(user_data, " Jutiapa 1") is False
        assert verificar_permiso_sucursal(user_data, "Jutiapa 1 ") is False
    
    def test_missing_rol_field(self):
        """Test permission check with missing rol field."""
        user_data = {
            "username": "test",
            "sucursal": "Jutiapa 1"
            # Missing "rol" field
        }
        
        # Should not crash, should deny access (not admin)
        assert verificar_permiso_sucursal(user_data, "Jutiapa 1") is True
        assert verificar_permiso_sucursal(user_data, "Jutiapa 2") is False
    
    def test_missing_sucursal_field(self):
        """Test permission check with missing sucursal field."""
        user_data = {
            "username": "test",
            "rol": "sucursal"
            # Missing "sucursal" field
        }
        
        # Should not crash, should deny access
        assert verificar_permiso_sucursal(user_data, "Jutiapa 1") is False
    
    def test_unknown_rol_type(self):
        """Test permission check with unknown rol type."""
        user_data = {
            "username": "test",
            "rol": "unknown_role",
            "sucursal": "Jutiapa 1"
        }
        
        # Should treat as regular user, not admin
        assert verificar_permiso_sucursal(user_data, "Jutiapa 1") is True
        assert verificar_permiso_sucursal(user_data, "Jutiapa 2") is False


class TestPermissionErrorMessages:
    """Test that permission errors have helpful messages."""
    
    def test_permission_denied_message_includes_branch(self):
        """Test that permission denied message includes branch name."""
        user_data = {
            "username": "jutiapa1",
            "rol": "sucursal",
            "sucursal": "Jutiapa 1"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            requiere_permiso_sucursal(user_data, "Progreso")
        
        assert "Progreso" in exc_info.value.detail
    
    def test_permission_denied_status_code(self):
        """Test that permission denied uses correct status code."""
        user_data = {
            "username": "jutiapa1",
            "rol": "sucursal",
            "sucursal": "Jutiapa 1"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            requiere_permiso_sucursal(user_data, "Jutiapa 2")
        
        assert exc_info.value.status_code == 403  # Forbidden
