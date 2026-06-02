# QUALCOMM PRO UNLOCKER

Herramienta profesional para eliminar bloqueos de pantalla y cuenta Google (FRP) en dispositivos con procesador Qualcomm (Snapdragon).

## DISPOSITIVOS SOPORTADOS
- BlackBerry KEYone (Snapdragon 625)
- Genéricos con procesadores MSM8953, MSM8937, MSM8917.

## REQUISITOS (WINDOWS)

Para que el script pueda comunicarse con el procesador en modo EDL, necesitas los drivers adecuados:

1.  **Drivers Qualcomm HS-USB QDLoader 9008:** Esenciales para que Windows reconozca el puerto COM.
2.  **Cable USB de buena calidad.**

## INSTALACIÓN

1. Instala Python 3.10 o superior.
2. Instala las librerías necesarias:
   ```bash
   pip install -r requirements.txt
   ```

## MODO DE USO (COMO CONECTAR)

1. Apaga el celular completamente.
2. Mantén presionados **VOLUMEN ARRIBA + VOLUMEN ABAJO**.
3. Conecta el cable USB mientras mantienes los botones.
4. Ejecuta el programa:
   ```bash
   python frp_bypass_tool.py
   ```
5. Ve a la pestaña de **CONTROL PRINCIPAL** y dale a **CONECTAR**.

---
**Nota:** Para quitar el bloqueo sin borrar fotos, usa la pestaña de **FUERZA BRUTA** si tienes el hash de la contraseña.
