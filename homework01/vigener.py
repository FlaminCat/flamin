def encrypt_vigenere(plaintext, keyword):
    """
        >>> encrypt_vigenere("PYTHON", "A")
        'PYTHON'
        >>> encrypt_vigenere("python", "a")
        'python'
        >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
        'LXFOPVEFRNHR'
        """
    ciphertext = ""
    new_keyword = ""  # new_keyword - ключевое слово, переведенное в верхний регистр
    for j in range(0, len(keyword)):
        if ord(keyword[j]) > 90:
            new_keyword += chr(ord(keyword[j]) - 32)
        else:
            new_keyword += keyword[j]
    for i in range(0, len(plaintext)):
        if 64 < ord(plaintext[i]) < 91:
            if ord(plaintext[i]) + ord(new_keyword[i % len(new_keyword)]) - 65 > 90:
                ciphertext += chr(ord(new_keyword[i % len(new_keyword)]) - (91 - ord(plaintext[i])))
            else:
                ciphertext += chr(ord(plaintext[i]) + ord(new_keyword[i % len(new_keyword)]) - 65)
        else:
            if ord(plaintext[i]) + ord(new_keyword[i % len(new_keyword)]) - 65 > 122:
                ciphertext += chr(32 + ord(new_keyword[i % len(new_keyword)]) - (123 - ord(plaintext[i])))
            else:
                ciphertext += chr(ord(plaintext[i]) + ord(new_keyword[i % len(new_keyword)]) - 65)
    return ciphertext


def decrypt_vigenere(ciphertext, keyword):
    """
        >>> decrypt_vigenere("PYTHON", "A")
        'PYTHON'
        >>> decrypt_vigenere("python", "a")
        'python'
        >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
        'ATTACKATDAWN'
        """
    plaintext = ""
    new_keyword = ""
    for j in range(0, len(keyword)):
        if ord(keyword[j]) > 90:
            new_keyword += chr(ord(keyword[j]) - 32)
        else:
            new_keyword += keyword[j]
    for i in range(0, len(ciphertext)):
        if 64 < ord(ciphertext[i]) < 91:
            if ord(ciphertext[i]) - (ord(new_keyword[i % len(new_keyword)]) - 65) < 65:
                plaintext += chr(90 - (ord(new_keyword[i % len(new_keyword)]) - 65 - (ord(ciphertext[i]) - 64)))
            else:
                plaintext += chr(ord(ciphertext[i]) - (ord(new_keyword[i % len(new_keyword)]) - 65))
        else:
            if ord(ciphertext[i]) + ord(new_keyword[i % len(new_keyword)]) - 65 < 97:
                plaintext += chr(122 - (ord(new_keyword[i % len(new_keyword)]) - 65 - (ord(ciphertext[i]) - 96)))
            else:
                plaintext += chr(ord(ciphertext[i]) - (ord(new_keyword[i % len(new_keyword)]) - 65))
    return plaintext
