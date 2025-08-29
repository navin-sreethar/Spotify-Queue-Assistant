#!/usr/bin/env python3
"""
Generate self-signed SSL certificates for local HTTPS development.
"""

import subprocess
import os
import sys

def generate_ssl_certificates():
    """Generate self-signed SSL certificates for localhost."""
    
    cert_dir = "ssl_certs"
    
    # Create directory for certificates
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
        print(f"Created {cert_dir} directory")
    
    key_file = os.path.join(cert_dir, "localhost.key")
    cert_file = os.path.join(cert_dir, "localhost.crt")
    
    # Check if certificates already exist
    if os.path.exists(key_file) and os.path.exists(cert_file):
        print("SSL certificates already exist!")
        return key_file, cert_file
    
    try:
        # Generate private key
        subprocess.run([
            "openssl", "genrsa", "-out", key_file, "2048"
        ], check=True)
        print(f"Generated private key: {key_file}")
        
        # Generate certificate
        subprocess.run([
            "openssl", "req", "-new", "-x509", "-key", key_file,
            "-out", cert_file, "-days", "365", "-subj",
            "/C=US/ST=Local/L=Local/O=Local/OU=Local/CN=localhost"
        ], check=True)
        print(f"Generated certificate: {cert_file}")
        
        print("\n✅ SSL certificates generated successfully!")
        print("⚠️  Note: You may see browser warnings about self-signed certificates.")
        print("   This is normal for local development - just click 'Advanced' and 'Proceed'.")
        
        return key_file, cert_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating certificates: {e}")
        print("\nMake sure OpenSSL is installed:")
        print("  macOS: brew install openssl")
        print("  Ubuntu: sudo apt-get install openssl")
        print("  Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ OpenSSL not found. Please install OpenSSL first:")
        print("  macOS: brew install openssl")
        print("  Ubuntu: sudo apt-get install openssl")
        print("  Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        sys.exit(1)

if __name__ == "__main__":
    generate_ssl_certificates()
