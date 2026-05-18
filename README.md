# OUKITEL WP36 FRP HACKER TOOL

Herramienta profesional para eliminar el bloqueo de cuenta Google (FRP) en dispositivos Oukitel WP36 con procesador MediaTek MT8788.

## REQUISITOS OBLIGATORIOS (WINDOWS)

Para que el script pueda "hablar" directamente con el procesador, necesitas preparar los drivers:

1.  **Drivers VCOM:** Debes tener instalados los drivers de MediaTek.
2.  **Filtro LibUSB (CRÍTICO):**
    *   Descarga **Zadig** (https://zadig.akeo.ie/).
    *   Conecta el celular apagado presionando **Volumen+ y Volumen-**.
    *   En Zadig, ve a `Options` -> `List All Devices`.
    *   Busca el dispositivo que diga **"MediaTek USB Port"** o **"Preloader USB VCOM"**.
    *   Selecciona el driver **libusb-win32 (v1.2.6.0)** y dale a **"Replace Driver"**.
    *   *Nota: Tienes que ser rápido porque el celular solo se queda en ese modo unos segundos.*

## INSTALACIÓN

1. Instala Python 3.10 o superior.
2. Instala las librerías necesarias:
   ```bash
   pip install -r requirements.txt
   ```

## MODO DE USO

1. Ejecuta el programa:
   ```bash
   python frp_bypass_tool.py
   ```
2. Haz clic en el botón rojo **"EJECUTAR HACK"**.
3. El programa dirá: "ESPERANDO DISPOSITIVO".
4. Con el celular **APAGADO**, presiona **AMBOS BOTONES DE VOLUMEN** y conecta el cable USB.
5. El programa detectará el celular, saltará la seguridad y borrará el bloqueo en menos de 5 segundos.

---
**Desarrollado para la competencia de hackeo de dispositivos.**
