def encrypt_caesar(plaintext):
    """
        >>> encrypt_caesar("PYTHON")
        'SBWKRQ'
        >>> encrypt_caesar("python")
        'sbwkrq'
        >>> encrypt_caesar("")
        ''
        >>> encrypt_caesar("123+,-")
        '123+,-'
        """
    ciphertext = ""
    for i in range(0, len(plaintext)):
        if ord(plaintext[i]) < 65 or 90 < ord(plaintext[i]) < 97 or ord(plaintext[i]) > 122:
            ciphertext += plaintext[i]
        else:
            if (90 < ord(plaintext[i]) + 3 < 96) or (ord(plaintext[i]) + 3 > 122):
                ciphertext += chr(ord(plaintext[i]) - 23)
            else:
                ciphertext += chr(ord(plaintext[i]) + 3)
    return ciphertext


def decrypt_caesar(plaintext):
    """
       >>> decrypt_caesar("SBWKRQ")
       'PYTHON'
       >>> decrypt_caesar("sbwkrq")
       'python'
       >>> decrypt_caesar("")
       ''
       >>> decrypt_caesar("123+,-")
       '123+,-'
       """
    ciphertext = ""
    for i in range(0, len(plaintext)):
        if ord(plaintext[i]) < 65 or 90 < ord(plaintext[i]) < 97 or ord(plaintext[i]) > 122:
            ciphertext += plaintext[i]
        else:
            if (ord(plaintext[i]) - 3 < 65) or (97 > ord(plaintext[i]) - 3 > 91):
                ciphertext += chr(ord(plaintext[i]) + 23)
            else:
                ciphertext += chr(ord(plaintext[i]) - 3)
    return ciphertext
