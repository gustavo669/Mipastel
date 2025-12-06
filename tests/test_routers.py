"""
Router Tests for MiPastel Application

Tests for:
- Authentication on all router endpoints
- Branch permission enforcement
- Normal and client order registration
- Unauthorized access attempts
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta

from api.auth import hash_session


@pytest.fixture
def authenticated_client(client):
    """Create a client with authenticated session for jutiapa1."""
    username = "jutiapa1"
    session_token = hash_session(username)
    
    client.cookies.set("session_token", session_token)
    client.cookies.set("username", username)
    client.cookies.set("sucursal", "Jutiapa 1")
    client.cookies.set("rol", "sucursal")
    
    return client


@pytest.fixture
def admin_client(client):
    """Create a client with authenticated session for admin."""
    username = "admin"
    session_token = hash_session(username)
    
    client.cookies.set("session_token", session_token)
    client.cookies.set("username", username)
    client.cookies.set("sucursal", "")
    client.cookies.set("rol", "admin")
    
    return client


class TestNormalesRouterAuthentication:
    """Test authentication requirements on normales router."""
    
    def test_formulario_requires_authentication(self, client):
        """Test that /normales/formulario requires authentication."""
        response = client.get("/normales/formulario")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_formulario_with_authentication(self, authenticated_client):
        """Test that /normales/formulario works with authentication."""
        response = authenticated_client.get("/normales/formulario")
        # May be 200 or redirect depending on implementation
        assert response.status_code in [200, 307, 308]
    
    def test_registrar_requires_authentication(self, client):
        """Test that /normales/registrar requires authentication."""
        response = client.post("/normales/registrar", data={
            "sabor": "Chocolate",
            "tamano": "Mediano",
            "cantidad": 1,
            "sucursal": "Jutiapa 1",
            "fecha_entrega": str(date.today() + timedelta(days=1))
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestClientesRouterAuthentication:
    """Test authentication requirements on clientes router."""
    
    def test_formulario_requires_authentication(self, client):
        """Test that /clientes/formulario requires authentication."""
        response = client.get("/clientes/formulario")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_formulario_with_authentication(self, authenticated_client):
        """Test that /clientes/formulario works with authentication."""
        response = authenticated_client.get("/clientes/formulario")
        assert response.status_code in [200, 307, 308]
    
    def test_registrar_requires_authentication(self, client):
        """Test that /clientes/registrar requires authentication."""
        response = client.post("/clientes/registrar", data={
            "sabor": "Vainilla",
            "tamano": "Grande",
            "cantidad": 1,
            "sucursal": "Jutiapa 1",
            "fecha_entrega": str(date.today() + timedelta(days=1))
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestBranchPermissionEnforcement:
    """Test branch permission enforcement on routers."""
    
    @patch('routers.normales.DatabaseManager')
    def test_normales_registrar_own_branch_allowed(self, mock_db, authenticated_client):
        """Test that user can register order for their own branch."""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.registrar_pastel_normal.return_value = True
        
        response = authenticated_client.post("/normales/registrar", data={
            "sabor": "Chocolate",
            "tamano": "Mediano",
            "cantidad": 1,
            "sucursal": "Jutiapa 1",  # Same as authenticated user
            "fecha_entrega": str(date.today() + timedelta(days=1)),
            "precio": 50.0
        })
        
        # Should succeed (200) or redirect to success page
        assert response.status_code in [200, 307, 308]
    
    def test_normales_registrar_other_branch_denied(self, authenticated_client):
        """Test that user cannot register order for other branch."""
        response = authenticated_client.post("/normales/registrar", data={
            "sabor": "Chocolate",
            "tamano": "Mediano",
            "cantidad": 1,
            "sucursal": "Jutiapa 2",  # Different from authenticated user
            "fecha_entrega": str(date.today() + timedelta(days=1)),
            "precio": 50.0
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch('routers.clientes.DatabaseManager')
    def test_clientes_registrar_own_branch_allowed(self, mock_db, authenticated_client):
        """Test that user can register client order for their own branch."""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.registrar_pedido_cliente.return_value = True
        
        response = authenticated_client.post("/clientes/registrar", data={
            "sabor": "Vainilla",
            "tamano": "Grande",
            "cantidad": 1,
            "sucursal": "Jutiapa 1",  # Same as authenticated user
            "fecha_entrega": str(date.today() + timedelta(days=1)),
            "precio": 75.0
        })
        
        assert response.status_code in [200, 307, 308]
    
    def test_clientes_registrar_other_branch_denied(self, authenticated_client):
        """Test that user cannot register client order for other branch."""
        response = authenticated_client.post("/clientes/registrar", data={
            "sabor": "Vainilla",
            "tamano": "Grande",
            "cantidad": 1,
            "sucursal": "Progreso",  # Different from authenticated user
            "fecha_entrega": str(date.today() + timedelta(days=1)),
            "precio": 75.0
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminPermissions:
    """Test that admin can access all branches."""
    
    @patch('routers.normales.DatabaseManager')
    def test_admin_can_register_any_branch(self, mock_db, admin_client):
        """Test that admin can register orders for any branch."""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.registrar_pastel_normal.return_value = True
        
        branches = ["Jutiapa 1", "Jutiapa 2", "Progreso", "Quesada"]
        
        for branch in branches:
            response = admin_client.post("/normales/registrar", data={
                "sabor": "Chocolate",
                "tamano": "Mediano",
                "cantidad": 1,
                "sucursal": branch,
                "fecha_entrega": str(date.today() + timedelta(days=1)),
                "precio": 50.0
            })
            
            # Admin should be able to register for any branch
            assert response.status_code in [200, 307, 308], f"Failed for branch {branch}"


class TestPedidosAPIAuthentication:
    """Test authentication on pedidos API endpoints."""
    
    def test_get_normales_requires_authentication(self, client):
        """Test that /api/pedidos/normales requires authentication."""
        response = client.get("/api/pedidos/normales")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_clientes_requires_authentication(self, client):
        """Test that /api/pedidos/clientes requires authentication."""
        response = client.get("/api/pedidos/clientes")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('routers.pedidos_api.DatabaseManager')
    def test_get_normales_with_authentication(self, mock_db, authenticated_client):
        """Test that /api/pedidos/normales works with authentication."""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.obtener_pasteles_normales.return_value = []
        
        response = authenticated_client.get("/api/pedidos/normales")
        assert response.status_code == 200
        assert "pedidos" in response.json()
    
    @patch('routers.pedidos_api.DatabaseManager')
    def test_get_clientes_with_authentication(self, mock_db, authenticated_client):
        """Test that /api/pedidos/clientes works with authentication."""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.obtener_pedidos_clientes.return_value = []
        
        response = authenticated_client.get("/api/pedidos/clientes")
        assert response.status_code == 200
        assert "pedidos" in response.json()


class TestDataFiltering:
    """Test that users only see data from their branch."""
    
    @patch('routers.pedidos_api.DatabaseManager')
    def test_user_sees_only_own_branch_normales(self, mock_db, authenticated_client):
        """Test that user only sees orders from their branch."""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        # Mock database to return orders from multiple branches
        mock_db_instance.obtener_pasteles_normales.return_value = [
            {"id": 1, "sucursal": "Jutiapa 1", "sabor": "Chocolate"},
            {"id": 2, "sucursal": "Jutiapa 2", "sabor": "Vainilla"},
        ]
        
        response = authenticated_client.get("/api/pedidos/normales")
        
        # Verify that DatabaseManager was called with the user's branch
        mock_db_instance.obtener_pasteles_normales.assert_called_once()
        call_kwargs = mock_db_instance.obtener_pasteles_normales.call_args[1]
        assert call_kwargs.get("sucursal") == "Jutiapa 1"
    
    @patch('routers.pedidos_api.DatabaseManager')
    def test_admin_can_see_all_branches(self, mock_db, admin_client):
        """Test that admin can see orders from all branches."""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.obtener_pasteles_normales.return_value = []
        
        response = admin_client.get("/api/pedidos/normales")
        
        # Verify that DatabaseManager was called without branch filter
        mock_db_instance.obtener_pasteles_normales.assert_called_once()
        call_kwargs = mock_db_instance.obtener_pasteles_normales.call_args[1]
        # Admin should have sucursal=None or empty
        assert call_kwargs.get("sucursal") in [None, ""]
