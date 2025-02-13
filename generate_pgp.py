import pgpy

# Generate a new PGP key
key = pgpy.PGPKey.new(pgpy.constants.PubKeyAlgorithm.RSAEncryptOrSign, 4096)

# Create a user ID
user_id = pgpy.PGPUID.new("Your Name", email="your@email.com")

# Bind the user ID to the key
key.add_uid(user_id, usage={pgpy.constants.KeyFlags.Sign, pgpy.constants.KeyFlags.EncryptCommunications},
            hashes=[pgpy.constants.HashAlgorithm.SHA256],
            ciphers=[pgpy.constants.SymmetricKeyAlgorithm.AES256],
            compression=[pgpy.constants.CompressionAlgorithm.ZLIB])

# Print Public Key
print("\n🔹 PUBLIC KEY (Upload This to PGP Websites) 🔹\n")
print(str(key.pubkey))

# Print Private Key (Keep This Safe!)
print("\n🔒 PRIVATE KEY (DO NOT SHARE!) 🔒\n")
print(str(key))

# Save private key
with open("private_key.asc", "w") as priv_file:
    priv_file.write(str(key))

# Save public key
with open("public_key.asc", "w") as pub_file:
    pub_file.write(str(key.pubkey))

print("\n✅ PGP keys generated successfully!")
print("📂 Public Key: public_key.asc (Use this for encryption & uploading)")
print("📂 Private Key: private_key.asc (Keep this safe for decryption)")
