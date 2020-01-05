from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64


def to_16(key):
    key = bytes(key, encoding="utf8")
    while len(key) % 16 != 0:
        key += b'\0'
    return key  # 返回bytes


class USE_AES:
    def __init__(self, key):
        if len(key) > 32:
            key = key[0:32]
        self.key = to_16(key)

    def aes(self):
        return AES.new(self.key, AES.MODE_ECB)  # 初始化加密器

    def encrypt(self, text):
        aes = self.aes()
        return str(base64.encodebytes(aes.encrypt(to_16(text))), encoding='utf8').replace('\n', '')  # 加密

    def decodeBytes(self, text):
        aes = self.aes()
        return str(aes.decrypt(base64.decodebytes(bytes(text, encoding='utf-8'))).rstrip(b'\0').decode("utf-8"))  # 解密


if __name__ == '__main__':
    aes_test = USE_AES('ciusiy2y498fw41')
    encrypt = aes_test.encrypt('1234567891011121314151617181920')
    decode = aes_test.decodeBytes(encrypt)
    print(encrypt)
    print(decode)

