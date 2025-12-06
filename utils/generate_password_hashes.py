#!/usr/bin/env python3
"""
Password Hash Generator for MiPastel Application

This script generates bcrypt password hashes for user accounts.
Use this to create secure password hashes that should be stored in
environment variables or secure configuration files.

Usage:
    python generate_password_hashes.py

Example:
    $ python generate_password_hashes.py
    Enter username: jutiapa1
    Enter password: 
    
    Generated hash for user 'jutiapa1':
    $2b$12$KQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu
    
    Add this to your .env file:
    JUTIAPA1_PASSWORD_HASH=$2b$12$KQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu
"""

import bcrypt
import getpass
import sys


def generate_hash(password: str) -> str:
    """
    Generate a bcrypt hash for the given password.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        str: Bcrypt hash of the password
    """
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')


def verify_hash(password: str, password_hash: str) -> bool:
    """
    Verify that a password matches a hash.
    
    Args:
        password: Plain text password
        password_hash: Bcrypt hash to verify against
        
    Returns:
        bool: True if password matches hash
    """
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def main():
    """Main function to generate password hashes interactively."""
    print("=" * 70)
    print("MiPastel Password Hash Generator")
    print("=" * 70)
    print()
    
    while True:
        # Get username
        username = input("Enter username (or 'quit' to exit): ").strip()
        
        if username.lower() in ('quit', 'exit', 'q'):
            print("\nExiting...")
            break
            
        if not username:
            print("Error: Username cannot be empty\n")
            continue
        
        # Get password securely
        password = getpass.getpass("Enter password: ")
        
        if not password:
            print("Error: Password cannot be empty\n")
            continue
        
        # Confirm password
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            print("Error: Passwords do not match\n")
            continue
        
        # Generate hash
        print("\nGenerating hash...")
        password_hash = generate_hash(password)
        
        # Verify the hash works
        if verify_hash(password, password_hash):
            print("✓ Hash verified successfully\n")
        else:
            print("✗ Warning: Hash verification failed\n")
            continue
        
        # Display results
        print("-" * 70)
        print(f"Generated hash for user '{username}':")
        print(password_hash)
        print()
        print("Add this to your .env file:")
        env_var_name = f"{username.upper()}_PASSWORD_HASH"
        print(f"{env_var_name}={password_hash}")
        print()
        print("Or add to USERS_DB in api/auth.py:")
        print(f'    "{username}": {{')
        print(f'        "password_hash": "{password_hash}",')
        print(f'        "nombre": "...",')
        print(f'        "sucursal": "...",')
        print(f'        "rol": "..."')
        print('    }')
        print("-" * 70)
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
