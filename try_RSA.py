from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

data = "I met aliens in UFO. Here is the map.".encode("utf-8")

key = RSA.generate(2048)
print(key)
private_key = key.export_key()
print(private_key)
# file_out = open("private.pem", "wb")
# file_out.write(private_key)

public_key = key.publickey().export_key()
print(public_key)
# file_out = open("receiver.pem", "wb")
# file_out.write(public_key)

public_key = RSA.import_key(public_key)
print(public_key)
# Encrypt the session key with the public RSA key
cipher_rsa = PKCS1_OAEP.new(public_key)
enc_data = cipher_rsa.encrypt(data)

private_key = RSA.import_key(private_key)
cipher_rsa = PKCS1_OAEP.new(private_key)
dec_data = cipher_rsa.decrypt(enc_data)

print(dec_data)
