import xmlrpc.client
import sys
from datetime import datetime

def mostrar_catalogo(catalogo):
    print("\n" + "="*40)
    print("--- CATÁLOGO DE VEHÍCULOS (MARZO 2026) ---")
    print("="*40)
    for tipo, datos in catalogo.items():
        print(f"Vehículo: {tipo}")
        print(f"  - Cupo máximo: {datos['cupo']} personas")
        print(f"  - Costo por día: ${datos['costo']}")
        print(f"  - Unidades totales en flotilla: {datos['unidades']}")
        print("-" * 40)

def main():
    print("=== SISTEMA DE RENTA DE AUTOS ===")
    ip_servidor = input("Ingresa la IP local del servidor (ej. localhost): ").strip()
    puerto = 8000
    
    url_servidor = f"http://{ip_servidor}:{puerto}/"
    
    try:
        proxy = xmlrpc.client.ServerProxy(url_servidor, allow_none=True)
        catalogo = proxy.obtener_catalogo()
        print("\n[+] Conexión exitosa con el servidor.")
    except Exception as e:
        print(f"\n[!] Error de conexión: No se pudo alcanzar el servidor en {url_servidor}")
        sys.exit(1)

    usuario_id = input("Ingresa tu identificador de usuario: ").strip()
    solicitudes = []

    while True:
        mostrar_catalogo(catalogo)
        
        if len(solicitudes) >= 3:
            print("Has alcanzado el límite de 3 vehículos.")
            break
            
        opcion = input(f"\nUsuario: {usuario_id} | Carrito: {len(solicitudes)}/3\n¿Agregar vehículo? (s/n): ").strip().lower()
        if opcion != 's':
            break
            
        print("\n1. Auto 4 puertas\n2. Camioneta 4 puertas\n3. Camioneta 3 puertas")
        seleccion = input("Elige el número del vehículo (1/2/3): ").strip()
        mapa_seleccion = {'1': 'Auto 4 puertas', '2': 'Camioneta 4 puertas', '3': 'Camioneta 3 puertas'}
        
        if seleccion not in mapa_seleccion:
            print("[!] Selección inválida.")
            continue
            
        tipo_vehiculo = mapa_seleccion[seleccion]
        cupo_max = catalogo[tipo_vehiculo]['cupo']

        # --- VALIDACIÓN DE OCUPANTES (Bucle hasta que sea correcto) ---
        while True:
            try:
                ocupantes = int(input(f"Cantidad de ocupantes (Máximo {cupo_max}): ").strip())
                if ocupantes <= 0:
                    print("[!] La cantidad debe ser mayor a 0.")
                elif ocupantes > cupo_max:
                    print(f"[!] Error: El cupo máximo es de {cupo_max} personas.")
                else:
                    break # Dato correcto, salimos del bucle de ocupantes
            except ValueError:
                print("[!] Ingresa un número entero válido.")

        # --- VALIDACIÓN DE FECHAS (Bucle hasta que sea correcto) ---
        while True:
            print("\nFechas para Marzo 2026 (YYYY-MM-DD):")
            f_inicio_str = input("Fecha de inicio: ").strip()
            f_fin_str = input("Fecha de fin: ").strip()

            try:
                inicio = datetime.strptime(f_inicio_str, '%Y-%m-%d').date()
                fin = datetime.strptime(f_fin_str, '%Y-%m-%d').date()

                # 1. Validar que sean de Marzo 2026
                if inicio.month != 3 or fin.month != 3 or inicio.year != 2026 or fin.year != 2026:
                    print("[!] Error: Las fechas deben ser exclusivamente de marzo de 2026.")
                    continue

                # 2. Validar que inicio no sea mayor a fin
                if inicio > fin:
                    print("[!] Error: La fecha de inicio no puede ser mayor a la de fin.")
                    continue

                # 3. Validar regla especial de Camioneta 4 puertas (Lunes)
                if tipo_vehiculo == 'Camioneta 4 puertas':
                    if inicio.weekday() == 0 or fin.weekday() == 0:
                        print("[!] Error: La 'Camioneta 4 puertas' no se entrega ni recibe los lunes.")
                        continue
                
                # Si pasa todas las pruebas locales
                fecha_inicio, fecha_fin = f_inicio_str, f_fin_str
                break 

            except ValueError:
                print("[!] Formato inválido. Usa YYYY-MM-DD (ej. 2026-03-05).")

        solicitudes.append({
            'tipo': tipo_vehiculo,
            'ocupantes': ocupantes,
            'inicio': fecha_inicio,
            'fin': fecha_fin
        })
        print(f"[+] {tipo_vehiculo} agregado exitosamente.")

    if solicitudes:
        print("\n" + "="*40)
        print("Enviando solicitud final al servidor...")
        try:
            respuesta = proxy.procesar_renta(usuario_id, solicitudes)
            if respuesta['exito']:
                print(f"\n[+] APROBADA: {respuesta['mensaje']}")
                print(f"Monto total: ${respuesta['monto_pagar']}")
            else:
                print(f"\n[-] RECHAZADA: {respuesta['mensaje']}")
        except Exception as e:
            print(f"\n[!] Error: {e}")

if __name__ == "__main__":
    main()