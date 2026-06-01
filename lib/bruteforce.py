import hashlib
import binascii
import time

class BruteForceModule:
    """
    Módulo para intentar descifrar el hash de la contraseña si no se puede borrar.
    """
    def __init__(self, log_callback=None):
        self.log_callback = log_callback

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)

    def crack_sha1_salt(self, target_hash_hex, salt_hex, charset="0123456789", max_len=4):
        """
        Algoritmo compatible con Android 4.4 - 5.1 (SHA1(pass+salt)).
        NOTA: Android 6.0+ (como BlackBerry KEYone) usa Scrypt/PBKDF2.
        Esta herramienta es para fines de investigación educativa.
        """
        try:
            target_hash = binascii.unhexlify(target_hash_hex)
            salt = binascii.unhexlify(salt_hex)
        except Exception:
            return "Error: Hash o Salt inválido."

        self.log(f"Iniciando ataque (Modo: Legacy SHA1+Salt)...")
        start_time = time.time()

        found = [None]
        def recurse(current_pass):
            if found[0] or len(current_pass) > max_len:
                return
            guess = current_pass.encode()
            h = hashlib.sha1(guess + salt).digest()
            if h == target_hash:
                found[0] = current_pass
                return
            for char in charset:
                recurse(current_pass + char)

        recurse("")

        elapsed = time.time() - start_time
        if found[0]:
            return f"¡CONTRASEÑA HALLADA!: {found[0]}\n(Tiempo: {elapsed:.2f}s)"
        else:
            return f"No se encontró en este rango.\nNota: KEYone podría requerir algoritmos PBKDF2/Scrypt."
