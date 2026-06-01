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
        else:
            print(msg)

    def crack_sha1_salt(self, target_hash_hex, salt_hex, charset="0123456789", max_len=4):
        """
        Ejemplo de crackeo para Android antiguo (SHA1(password + salt)).
        """
        try:
            target_hash = binascii.unhexlify(target_hash_hex)
            salt = binascii.unhexlify(salt_hex)
        except Exception:
            return "Error: Hash o Salt inválido (deben ser hexadecimales)."

        self.log(f"Iniciando fuerza bruta sobre {target_hash_hex}...")
        start_time = time.time()

        found = [None]
        def recurse(current_pass):
            if found[0] or len(current_pass) > max_len:
                return

            # Probar actual
            guess = current_pass.encode()
            h = hashlib.sha1(guess + salt).digest()
            if h == target_hash:
                found[0] = current_pass
                return

            # Siguiente nivel
            for char in charset:
                recurse(current_pass + char)

        recurse("")

        elapsed = time.time() - start_time
        if found[0]:
            return f"¡ÉXITO! Contraseña encontrada: {found[0]} (Tiempo: {elapsed:.2f}s)"
        else:
            return f"No se encontró la contraseña en el rango definido. (Tiempo: {elapsed:.2f}s)"
