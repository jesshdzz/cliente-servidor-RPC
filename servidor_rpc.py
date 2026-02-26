from socketserver import ThreadingMixIn
from datetime import datetime, date
import xmlrpc.server
import threading

class ThreadedXMLRPCServer(ThreadingMixIn, xmlrpc.server.SimpleXMLRPCServer):
    """Servidor XML-RPC que soporta concurrencia multihilo."""
    pass

class SistemaRentaAutos:
    def __init__(self):
        # Candado para evitar condiciones de carrera cuando múltiples hilos modifiquen el inventario
        self.lock = threading.Lock()
        
        self.catalogo = {
            'Auto 4 puertas': {'cupo': 4, 'costo': 600, 'unidades': 5},
            'Camioneta 4 puertas': {'cupo': 5, 'costo': 750, 'unidades': 5},
            'Camioneta 3 puertas': {'cupo': 10, 'costo': 1200, 'unidades': 3}
        }
        
        # Calendario de disponibilidad para marzo 2026 (del 1 al 31)
        # Formato: { 'Tipo': { 1: 5, 2: 5, ..., 31: 5 } }
        self.inventario_marzo = {
            tipo: {dia: datos['unidades'] for dia in range(1, 32)}
            for tipo, datos in self.catalogo.items()
        }

    def obtener_catalogo(self):
        """El stub servidor presenta los tipos de vehículos con sus características."""
        return self.catalogo

    def _validar_fechas(self, str_inicio, str_fin):
        """Convierte y valida que las fechas pertenezcan a marzo de 2026."""
        try:
            inicio = datetime.strptime(str_inicio, '%Y-%m-%d').date()
            fin = datetime.strptime(str_fin, '%Y-%m-%d').date()
            if inicio.month != 3 or fin.month != 3 or inicio.year != 2026:
                return False, "Las fechas deben ser de marzo de 2026."
            if inicio > fin:
                return False, "La fecha de inicio no puede ser mayor a la fecha de fin."
            return True, (inicio, fin)
        except ValueError:
            return False, "Formato de fecha inválido. Use YYYY-MM-DD."

    def procesar_renta(self, usuario_id, solicitudes):
        """
        Procesa hasta 3 vehículos por usuario de forma atómica.
        solicitudes es una lista de diccionarios: [{'tipo': str, 'ocupantes': int, 'inicio': str, 'fin': str}]
        """
        if len(solicitudes) > 3:
            return {'exito': False, 'mensaje': "Un usuario solo puede rentar hasta 3 vehículos."}

        # Adquirimos el candado antes de leer/escribir inventario para garantizar transacciones seguras
        with self.lock:
            monto_total = 0
            dias_a_modificar = [] # Guardaremos los cambios para aplicarlos solo si TODA la solicitud es válida

            for req in solicitudes:
                tipo = req['tipo']
                ocupantes = req['ocupantes']
                
                # 1. Validar Tipo y Cupo
                if tipo not in self.catalogo:
                    return {'exito': False, 'mensaje': f"Vehículo '{tipo}' no existe."}
                if ocupantes > self.catalogo[tipo]['cupo']:
                    return {'exito': False, 'mensaje': f"El vehículo {tipo} no soporta {ocupantes} ocupantes."}

                # 2. Validar Fechas
                valido, resultado = self._validar_fechas(req['inicio'], req['fin'])
                if not valido:
                    return {'exito': False, 'mensaje': resultado}
                inicio, fin = resultado
                
                # 3. Validar Regla B (Camioneta 4 puertas: no inicia ni termina en lunes)
                # weekday() devuelve 0 para el lunes
                if tipo == 'Camioneta 4 puertas':
                    if inicio.weekday() == 0 or fin.weekday() == 0:
                        return {'exito': False, 'mensaje': "La 'Camioneta 4 puertas' no puede iniciar ni entregarse en lunes."}

                # 4. Verificar Disponibilidad día por día
                dias_renta = (fin - inicio).days + 1
                for dia in range(inicio.day, fin.day + 1):
                    if self.inventario_marzo[tipo][dia] <= 0:
                        return {'exito': False, 'mensaje': f"No hay disponibilidad para {tipo} el {dia} de marzo."}
                    # Preparamos la modificación temporal
                    dias_a_modificar.append((tipo, dia))
                
                # Calcular costo parcial
                monto_total += dias_renta * self.catalogo[tipo]['costo']

            # Si llegamos aquí, TODA la solicitud es válida. Aplicamos los descuentos al inventario real.
            for tipo, dia in dias_a_modificar:
                self.inventario_marzo[tipo][dia] -= 1

            return {
                'exito': True, 
                'mensaje': f"Renta confirmada para el usuario {usuario_id}.", 
                'monto_pagar': monto_total
            }

def iniciar_servidor():
    # 0.0.0.0 permite conexiones desde cualquier IP en la red local
    host = "0.0.0.0"
    puerto = 8000
    
    print("Iniciando servidor RPC...")
    # Es vital mantener el ThreadedXMLRPCServer para la concurrencia real
    server = ThreadedXMLRPCServer((host, puerto), allow_none=True)
        
    server.register_instance(SistemaRentaAutos())
    print(f"Servidor escuchando en todas las interfaces en el puerto {puerto}.")
    print("Presiona Ctrl+C para detener.")
    server.serve_forever()

if __name__ == "__main__":
    iniciar_servidor()