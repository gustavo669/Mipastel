"""
Audit Logging System for MiPastel Application

This module provides comprehensive audit logging for:
- Data modifications (create, update, delete)
- Authentication events (login, logout, failed attempts)
- Permission denials
- All user actions with context

Audit logs are stored with timestamp, user, action, and details.
"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
from config.settings import settings

# Configure audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Create audit log file handler
audit_log_file = settings.LOGS_DIR / "audit.log"
file_handler = logging.FileHandler(audit_log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# Add handler to logger
if not audit_logger.handlers:
    audit_logger.addHandler(file_handler)


class AuditLogger:
    """Centralized audit logging for the application."""
    
    @staticmethod
    def _format_log_entry(
        action: str,
        username: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "SUCCESS",
        ip_address: Optional[str] = None
    ) -> str:
        """
        Format a log entry as JSON.
        
        Args:
            action: Action being performed
            username: Username performing the action
            details: Additional details about the action
            status: Status of the action (SUCCESS, FAILURE, DENIED)
            ip_address: IP address of the user
            
        Returns:
            str: Formatted JSON log entry
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "username": username or "anonymous",
            "status": status,
            "details": details or {},
        }
        
        if ip_address:
            log_data["ip_address"] = ip_address
        
        return json.dumps(log_data, ensure_ascii=False)
    
    @staticmethod
    def log_login_success(username: str, ip_address: Optional[str] = None):
        """Log successful login."""
        entry = AuditLogger._format_log_entry(
            action="LOGIN",
            username=username,
            status="SUCCESS",
            ip_address=ip_address
        )
        audit_logger.info(entry)
    
    @staticmethod
    def log_login_failure(username: str, reason: str, ip_address: Optional[str] = None):
        """Log failed login attempt."""
        entry = AuditLogger._format_log_entry(
            action="LOGIN",
            username=username,
            status="FAILURE",
            details={"reason": reason},
            ip_address=ip_address
        )
        audit_logger.warning(entry)
    
    @staticmethod
    def log_logout(username: str, ip_address: Optional[str] = None):
        """Log user logout."""
        entry = AuditLogger._format_log_entry(
            action="LOGOUT",
            username=username,
            status="SUCCESS",
            ip_address=ip_address
        )
        audit_logger.info(entry)
    
    @staticmethod
    def log_permission_denied(
        username: str,
        action: str,
        resource: str,
        reason: str,
        ip_address: Optional[str] = None
    ):
        """Log permission denial."""
        entry = AuditLogger._format_log_entry(
            action="PERMISSION_DENIED",
            username=username,
            status="DENIED",
            details={
                "attempted_action": action,
                "resource": resource,
                "reason": reason
            },
            ip_address=ip_address
        )
        audit_logger.warning(entry)
    
    @staticmethod
    def log_create(
        username: str,
        resource_type: str,
        resource_id: Any,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """Log resource creation."""
        entry = AuditLogger._format_log_entry(
            action="CREATE",
            username=username,
            status="SUCCESS",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id,
                **(details or {})
            },
            ip_address=ip_address
        )
        audit_logger.info(entry)
    
    @staticmethod
    def log_update(
        username: str,
        resource_type: str,
        resource_id: Any,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """Log resource update."""
        entry = AuditLogger._format_log_entry(
            action="UPDATE",
            username=username,
            status="SUCCESS",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "changes": changes or {}
            },
            ip_address=ip_address
        )
        audit_logger.info(entry)
    
    @staticmethod
    def log_delete(
        username: str,
        resource_type: str,
        resource_id: Any,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """Log resource deletion."""
        entry = AuditLogger._format_log_entry(
            action="DELETE",
            username=username,
            status="SUCCESS",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id,
                **(details or {})
            },
            ip_address=ip_address
        )
        audit_logger.info(entry)
    
    @staticmethod
    def log_action(
        action: str,
        username: str,
        details: Optional[Dict[str, Any]] = None,
        status: str = "SUCCESS",
        ip_address: Optional[str] = None
    ):
        """Log a generic action."""
        entry = AuditLogger._format_log_entry(
            action=action,
            username=username,
            status=status,
            details=details,
            ip_address=ip_address
        )
        
        if status == "SUCCESS":
            audit_logger.info(entry)
        elif status == "FAILURE":
            audit_logger.warning(entry)
        else:
            audit_logger.error(entry)


# Convenience functions for common operations
def log_pedido_normal_created(username: str, pedido_id: int, sucursal: str, sabor: str, tamano: str):
    """Log creation of a normal cake order."""
    AuditLogger.log_create(
        username=username,
        resource_type="pedido_normal",
        resource_id=pedido_id,
        details={
            "sucursal": sucursal,
            "sabor": sabor,
            "tamano": tamano
        }
    )


def log_pedido_cliente_created(username: str, pedido_id: int, sucursal: str, sabor: str, tamano: str):
    """Log creation of a client order."""
    AuditLogger.log_create(
        username=username,
        resource_type="pedido_cliente",
        resource_id=pedido_id,
        details={
            "sucursal": sucursal,
            "sabor": sabor,
            "tamano": tamano
        }
    )


def log_pedido_updated(username: str, pedido_type: str, pedido_id: int, changes: Dict[str, Any]):
    """Log update of an order."""
    AuditLogger.log_update(
        username=username,
        resource_type=pedido_type,
        resource_id=pedido_id,
        changes=changes
    )


def log_pedido_deleted(username: str, pedido_type: str, pedido_id: int, sucursal: str):
    """Log deletion of an order."""
    AuditLogger.log_delete(
        username=username,
        resource_type=pedido_type,
        resource_id=pedido_id,
        details={"sucursal": sucursal}
    )


def log_price_updated(username: str, price_id: int, old_price: float, new_price: float):
    """Log price update."""
    AuditLogger.log_update(
        username=username,
        resource_type="precio",
        resource_id=price_id,
        changes={
            "old_price": old_price,
            "new_price": new_price
        }
    )


# Export main class and convenience functions
__all__ = [
    'AuditLogger',
    'log_pedido_normal_created',
    'log_pedido_cliente_created',
    'log_pedido_updated',
    'log_pedido_deleted',
    'log_price_updated'
]
