# Herramienta REAL de Bypass FRP - Oukitel WP36 (MT8788)

Esta herramienta está diseñada para eliminar el bloqueo de cuenta de Google (FRP) en el Oukitel WP36 mediante la manipulación directa del procesador MediaTek en modo BROM.

## Especificaciones del Objetivo
- **Modelo:** Oukitel WP36
- **Chipset:** MediaTek MT8788 (MT6771)
- **Dirección FRP (Scatter):** `0x1588000`
- **Tamaño:** `0x100000` (1 MB)

## Requisitos de Sistema
1. **Python 3.10+**
2. **Drivers MediaTek VCOM** instalados en Windows.
3. **Filtro LibUSB (Opcional pero recomendado):** Si la herramienta no detecta el dispositivo, usa `Zadig` para instalar el driver `libusb-win32` en el dispositivo "MediaTek USB Port" mientras lo conectas con los botones presionados.

## Instalación
Ejecuta el siguiente comando en tu terminal para instalar las dependencias necesarias:
```bash
pip install -r requirements.txt
```

## Uso de la Herramienta
1. Ejecuta el programa: `python frp_bypass_tool.py`.
2. Haz clic en **"EJECUTAR BORRADO FÍSICO"**.
3. **Apaga el teléfono.**
4. Presiona y mantén **Volumen Arriba (+)** y **Volumen Abajo (-)**.
5. Conecta el cable USB a la PC.
6. Suelta los botones cuando veas que el log avanza (Handshake exitoso).
7. Espera a que aparezca el mensaje de éxito.

## Solución de Problemas
- **Si se queda en "Buscando dispositivo":** Revisa el Administrador de Dispositivos. Si aparece como "Dispositivo desconocido" o con un triángulo amarillo, reinstala los drivers VCOM.
- **Error de Handshake:** Intenta conectar el cable con más rapidez después de presionar los botones. Algunos modelos entran en modo carga muy rápido.

---
**ADVERTENCIA:** Esta herramienta realiza escrituras de bajo nivel. Úsela bajo su propio riesgo. No nos hacemos responsables por dispositivos dañados ("bricked").
