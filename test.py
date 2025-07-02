from OpenSSL import crypto, SSL
import os

def generate_self_signed_cert(cert_file="cert.pem", key_file="key.pem"):
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        # Create a key pair
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 4096)
        
        # Create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().CN = "localhost"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(365*24*60*60)  # 1 year
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, 'sha256')
        
        # Save files
        with open(cert_file, "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(key_file, "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        print(f"Generated {cert_file} and {key_file}")

# Generate certs if missing
generate_self_signed_cert()