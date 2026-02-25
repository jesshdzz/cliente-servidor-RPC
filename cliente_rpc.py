import xmlrpc.client

def main():
    # Conexión al servidor que proporcionaste
    proxy = xmlrpc.client.ServerProxy("http://localhost:8000/", allow_none=True)

    try:
        print("\t=== CATÁLOGO DE VEHÍCULOS ===")
        catalogo = proxy.obtener_catalogo()
        for tipo, info in catalogo.items():
            print(f"{tipo:20} | Cupo: {info['cupo']} | Stock Base: {info['unidades']} | Costo: ${info['costo']}")
        print("-" * 75)

        # 2. Casos de prueba diseñados para activar cada validación del servidor
        casos_prueba = [
            {
                'id': 'Usuario_Isabel',
                'descripcion': 'SOLICITUD EXITOSA (Todo en orden)',
                'solicitudes': [
                    {'tipo': 'Auto 4 puertas', 'ocupantes': 2, 'inicio': '2026-03-01', 'fin': '2026-03-03'},
                    {'tipo': 'Camioneta 3 puertas', 'ocupantes': 8, 'inicio': '2026-03-10', 'fin': '2026-03-12'}
                ]
            },
            {
                'id': 'Usuario_Juan',
                'descripcion': 'FALLO POR CUPO (10 personas en auto de 5)',
                'solicitudes': [
                    {'tipo': 'Camioneta 4 puertas', 'ocupantes': 10, 'inicio': '2026-03-15', 'fin': '2026-03-17'}
                ]
            },
            {
                'id': 'Usuario_Maria',
                'descripcion': 'FALLO POR LÍMITE DE AUTOS (Intenta rentar 4)',
                'solicitudes': [
                    {'tipo': 'Auto 4 puertas', 'ocupantes': 2, 'inicio': '2026-03-01', 'fin': '2026-03-02'},
                    {'tipo': 'Auto 4 puertas', 'ocupantes': 2, 'inicio': '2026-03-04', 'fin': '2026-03-05'},
                    {'tipo': 'Auto 4 puertas', 'ocupantes': 2, 'inicio': '2026-03-07', 'fin': '2026-03-08'},
                    {'tipo': 'Auto 4 puertas', 'ocupantes': 2, 'inicio': '2026-03-10', 'fin': '2026-03-11'}
                ]
            },
            {
                'id': 'Usuario_Luis',
                'descripcion': 'FALLO REGLA ESPECIAL (Camioneta 4p en Lunes 02-Mar)',
                'solicitudes': [
                    {'tipo': 'Camioneta 4 puertas', 'ocupantes': 3, 'inicio': '2026-03-02', 'fin': '2026-03-04'}
                ]
            },
            {
                'id': 'Usuario_Ana',
                'descripcion': 'FALLO POR FECHA (Fuera de marzo 2026)',
                'solicitudes': [
                    {'tipo': 'Auto 4 puertas', 'ocupantes': 2, 'inicio': '2026-04-01', 'fin': '2026-04-05'}
                ]
            }
        ]

        # 3. Ejecución de las solicitudes
        for caso in casos_prueba:
            print(f"\n>>> EJECUTANDO PRUEBA PARA: {caso['id']}")
            print(f"Descripción: {caso['descripcion']}")
            
            # El servidor procesa todas las reglas que mencionaste
            resultado = proxy.procesar_renta(caso['id'], caso['solicitudes'])
            
            if resultado['exito']:
                print(f"RESULTADO: {resultado['mensaje']}")
                print(f"MONTO TOTAL A PAGAR: ${resultado['monto_pagar']}")
            else:
                print(f"RESULTADO: FALLIDO - Motivo: {resultado['mensaje']}")

    except Exception as e:
        print(f"Error de conexión con el servidor: {e}")

if __name__ == "__main__":
    main()