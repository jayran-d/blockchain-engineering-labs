from ipv8.keyvault.crypto import default_eccrypto

KEY_FILE = "keys/lab_identity_key.pem"

crypto = default_eccrypto
private_key = crypto.key_from_private_bin(open(KEY_FILE, "rb").read())

public_key_hex = private_key.pub().key_to_bin().hex()

print(public_key_hex)