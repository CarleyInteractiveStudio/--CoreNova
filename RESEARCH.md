# Investigación Técnica: MediaTek BROM & Exploits (SLA/DAA)

## 1. El Protocolo BootROM (BROM)
El procesador MediaTek contiene un código de arranque inmutable (ROM) que se ejecuta al encender el dispositivo. Si se detecta una señal específica (como presionar botones de volumen), entra en modo **BROM (BOOTROM)**.

### Comandos Clave:
- `0xA0`: Handshake (Eco). El dispositivo responde con `0x5A`.
- `0xA1`: Obtener versión de almacenamiento.
- `0x10`: Obtener versión de hardware (HW_CODE). Para MT6771 el código es `0x0707`.
- `0xD4`: Comando de formateo (FORMAT). Requiere dirección de inicio y tamaño.
- `0xD1`: Escribir datos (WRITE).
- `0xD2`: Leer datos (READ).

## 2. Seguridad: SLA y DAA
Los dispositivos modernos (como el Oukitel WP36) protegen el BROM:
- **SLA (Serial Link Authentication):** El BROM requiere que se le envíe un token firmado antes de aceptar comandos sensibles como `0xD4`.
- **DAA (Download Agent Authentication):** Solo se permite ejecutar código (Download Agents) que esté firmado por el fabricante.

## 3. Exploit Kamakiri
El exploit Kamakiri aprovecha una vulnerabilidad en la pila USB del BootROM. Al enviar transferencias de control malformadas, se puede provocar un desbordamiento de búfer o una corrupción de memoria que desactiva la verificación de firmas (SLA/DAA).

### Pasos del Exploit:
1. **Trigger:** Enviar una secuencia de `USB CONTROL TRANSFERS` con longitudes específicas que corrompen el puntero de configuración del BROM.
2. **Payload:** Una vez corrompido, el BROM deja de validar los comandos.
3. **Patcher:** Se envían comandos para "parchear" en memoria las variables `auth_required` y `daa_required` a `0`.

## 4. Estructura de Memoria (Oukitel WP36)
- **Chipset:** MT6771 (Helio P60) / MT8788.
- **Partición FRP:** `0x1588000` (Linear Start Address).
- **Tamaño:** `0x100000`.

## 5. Manual de la Herramienta V5 (Research Edition)

### Estructura de Archivos:
- `frp_bypass_tool.py`: Interfaz principal.
- `lib/brom.py`: Protocolo de bajo nivel (Handshake, Read, Write, Format).
- `lib/payloads.py`: Lógica del exploit USB Kamakiri.
- `lib/chips.py`: Base de datos de chipsets y direcciones.
- `payloads/`: Carpeta para scripts de inyección (.txt).

### Cómo usar los Payloads:
Crea un archivo `.txt` en la carpeta `payloads/` con el formato:
`DIRECCIÓN_HEX: VALOR_HEX`
Ejemplo: `0x10007000: 0x2200` para desactivar el Watchdog.

### Recomendaciones para la Próxima Competencia:
1. **Zadig siempre listo:** LibUSB es necesario para que el exploit Kamakiri (USB) funcione.
2. **Fallback Serial:** Si el USB falla, el script intentará conectar por COM para usar los comandos BROM estándar si la seguridad ya fue saltada.
3. **Hex Dump:** Usa la pestaña de memoria para verificar si la partición FRP está realmente vacía (deberían verse puros `00` o `FF`).
