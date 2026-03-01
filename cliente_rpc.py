import xmlrpc.client
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class ClienteRentaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Renta de Autos - Marzo 2026")
        self.root.geometry("650x700")
        self.root.configure(padx=20, pady=20)

        self.proxy = None
        self.catalogo = {}
        self.usuario_id = ""
        self.solicitudes = []

        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, relief="flat", background="#0078D7", foreground="white")
        style.configure("TLabel", font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 14, "bold"), foreground="#333333")

        self.crear_pantalla_conexion()

    # ==========================================
    # PANTALLA 1: CONEXIÓN
    # ==========================================
    def crear_pantalla_conexion(self):
        self.frame_conexion = ttk.Frame(self.root)
        self.frame_conexion.pack(fill="both", expand=True, pady=50)

        ttk.Label(self.frame_conexion, text="Bienvenido al Sistema de Rentas", style="Header.TLabel").pack(pady=20)

        ttk.Label(self.frame_conexion, text="IP del Servidor (ej. localhost):").pack()
        self.entry_ip = ttk.Entry(self.frame_conexion, width=30)
        self.entry_ip.insert(0, "localhost")
        self.entry_ip.pack(pady=5)

        ttk.Label(self.frame_conexion, text="Identificador de Usuario:").pack()
        self.entry_usuario = ttk.Entry(self.frame_conexion, width=30)
        self.entry_usuario.pack(pady=5)

        btn_conectar = ttk.Button(self.frame_conexion, text="Conectar al Servidor", command=self.conectar_servidor)
        btn_conectar.pack(pady=20)

    def conectar_servidor(self):
        ip = self.entry_ip.get().strip()
        user = self.entry_usuario.get().strip()

        if not ip or not user:
            messagebox.showwarning("Faltan datos", "Por favor ingresa la IP y tu usuario.")
            return

        try:
            url = f"http://{ip}:8000/"
            self.proxy = xmlrpc.client.ServerProxy(url, allow_none=True)
            self.catalogo = self.proxy.obtener_catalogo()
            self.usuario_id = user
            
            # Si conecta, ocultamos esta pantalla y mostramos la principal
            self.frame_conexion.destroy()
            self.crear_pantalla_principal()
            
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar al servidor en {url}\n{e}")

    # ==========================================
    # PANTALLA 2: INTERFAZ PRINCIPAL (Mantiene TODA tu lógica)
    # ==========================================
    def crear_pantalla_principal(self):
        self.frame_main = ttk.Frame(self.root)
        self.frame_main.pack(fill="both", expand=True)

        ttk.Label(self.frame_main, text=f"Usuario Activo: {self.usuario_id}", style="Header.TLabel").pack(pady=10)

        # --- SECCIÓN CATÁLOGO ---
        ttk.Label(self.frame_main, text="Catálogo de Vehículos (Marzo 2026)", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        
        columnas = ('tipo', 'cupo', 'costo', 'unidades')
        self.tree_catalogo = ttk.Treeview(self.frame_main, columns=columnas, show='headings', height=4)
        self.tree_catalogo.heading('tipo', text='Vehículo')
        self.tree_catalogo.heading('cupo', text='Cupo Max.')
        self.tree_catalogo.heading('costo', text='Costo/Día')
        self.tree_catalogo.heading('unidades', text='Unidades')
        self.tree_catalogo.column('tipo', width=180)
        self.tree_catalogo.column('cupo', width=90, anchor='center')
        self.tree_catalogo.column('costo', width=90, anchor='center')
        self.tree_catalogo.column('unidades', width=80, anchor='center')
        self.tree_catalogo.pack(fill="x", pady=5)

        tipos_vehiculos = []
        for tipo, datos in self.catalogo.items():
            unidades = datos.get('unidades', 0)
            self.tree_catalogo.insert('', tk.END, values=(tipo, f"{datos['cupo']} personas", f"${datos['costo']}", f"{unidades} u."))
            tipos_vehiculos.append(tipo)

        # --- FORMULARIO DE SOLICITUD ---
        frame_form = ttk.LabelFrame(self.frame_main, text="Agregar Vehículo al Carrito", padding=15)
        frame_form.pack(fill="x", pady=15)

        ttk.Label(frame_form, text="Vehículo:").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_tipo = ttk.Combobox(frame_form, values=tipos_vehiculos, state="readonly", width=25)
        self.combo_tipo.grid(row=0, column=1, pady=5, padx=10)
        if tipos_vehiculos: self.combo_tipo.current(0)

        ttk.Label(frame_form, text="Ocupantes:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_ocupantes = ttk.Entry(frame_form, width=10)
        self.entry_ocupantes.grid(row=1, column=1, sticky="w", pady=5, padx=10)

        ttk.Label(frame_form, text="Día de Inicio (Marzo 2026):").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_inicio = ttk.Spinbox(frame_form, from_=1, to=31, width=13)
        self.entry_inicio.set('1')
        self.entry_inicio.grid(row=2, column=1, sticky="w", pady=5, padx=10)

        ttk.Label(frame_form, text="Día de Fin (Marzo 2026):").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_fin = ttk.Spinbox(frame_form, from_=1, to=31, width=13)
        self.entry_fin.set('1')
        self.entry_fin.grid(row=3, column=1, sticky="w", pady=5, padx=10)

        ttk.Button(frame_form, text="Agregar a Solicitud", command=self.agregar_vehiculo).grid(row=4, column=0, columnspan=2, pady=15)

        # --- SECCIÓN CARRITO ---
        self.lbl_carrito = ttk.Label(self.frame_main, text="Vehículos en carrito: 0 / 3", font=("Arial", 11, "bold"), foreground="#D32F2F")
        self.lbl_carrito.pack(anchor="w")

        self.list_carrito = tk.Listbox(self.frame_main, height=4, width=70)
        self.list_carrito.pack(pady=5)

        ttk.Button(self.frame_main, text="ENVIAR SOLICITUD AL SERVIDOR", command=self.enviar_renta).pack(pady=20)

    # ==========================================
    # LÓGICA DE VALIDACIÓN (Idéntica a tu consola)
    # ==========================================
    def agregar_vehiculo(self):
        if len(self.solicitudes) >= 3:
            messagebox.showerror("Límite Alcanzado", "Ya tienes 3 vehículos en tu carrito.")
            return

        tipo_vehiculo = self.combo_tipo.get()
        cupo_max = self.catalogo[tipo_vehiculo]['cupo']

        # Validación 1: Ocupantes
        try:
            ocupantes = int(self.entry_ocupantes.get().strip())
            if ocupantes <= 0:
                messagebox.showwarning("Error de Ocupantes", "La cantidad debe ser mayor a 0.")
                return
            if ocupantes > cupo_max:
                messagebox.showerror("Exceso de Cupo", f"El cupo máximo para '{tipo_vehiculo}' es de {cupo_max} personas.")
                return
        except ValueError:
            messagebox.showwarning("Error de Formato", "Ingresa un número entero válido para los ocupantes.")
            return

        # Validación 2: Fechas
        dia_inicio_str = self.entry_inicio.get().strip()
        dia_fin_str = self.entry_fin.get().strip()

        try:
            dia_inicio = int(dia_inicio_str)
            dia_fin = int(dia_fin_str)

            if dia_inicio < 1 or dia_inicio > 31 or dia_fin < 1 or dia_fin > 31:
                messagebox.showerror("Día Inválido", "Los días deben estar entre 1 y 31 de marzo.")
                return

            f_inicio_str = f"2026-03-{dia_inicio:02d}"
            f_fin_str = f"2026-03-{dia_fin:02d}"

            inicio = datetime.strptime(f_inicio_str, '%Y-%m-%d').date()
            fin = datetime.strptime(f_fin_str, '%Y-%m-%d').date()

            if inicio > fin:
                messagebox.showerror("Error Cronológico", "El día de inicio no puede ser mayor al de fin.")
                return

            if tipo_vehiculo == 'Camioneta 4 puertas' and (inicio.weekday() == 0 or fin.weekday() == 0):
                messagebox.showerror("Regla Especial", "La 'Camioneta 4 puertas' no se entrega ni recibe los lunes.")
                return

        except ValueError:
            messagebox.showwarning("Formato Inválido", "Ingresa un número de día válido (1 al 31).")
            return

        # Validación 3: Disponibilidad Dinámica RPC
        try:
            resp_disp = self.proxy.consultar_disponibilidad(tipo_vehiculo, f_inicio_str, f_fin_str)
            if not resp_disp.get('exito', False):
                messagebox.showerror("Sin Disponibilidad", resp_disp.get('mensaje', 'Error al consultar disponibilidad.'))
                return
            
            unidades_disponibles = resp_disp.get('unidades', 0)
            unidades_en_carrito = sum(1 for req in self.solicitudes if req['tipo'] == tipo_vehiculo)
            
            if unidades_en_carrito >= unidades_disponibles:
                messagebox.showerror("Límite de Unidades", f"Sólo quedan {unidades_disponibles} unidades disponibles de '{tipo_vehiculo}' para ese rango de fechas y ya las tienes en tu carrito.")
                return
        except Exception as e:
            messagebox.showerror("Error de Red", f"No se pudo contactar al servidor para checar disponibilidad:\n{e}")
            return

        # Si todo pasa, agregamos a la lista
        self.solicitudes.append({
            'tipo': tipo_vehiculo,
            'ocupantes': ocupantes,
            'inicio': f_inicio_str,
            'fin': f_fin_str
        })
        
        # Actualizamos la interfaz
        self.list_carrito.insert(tk.END, f"{tipo_vehiculo} | {ocupantes} pax | Mar {dia_inicio:02d} - Mar {dia_fin:02d}")
        self.lbl_carrito.config(text=f"Vehículos en carrito: {len(self.solicitudes)} / 3")
        
        # Limpiar campos
        self.entry_ocupantes.delete(0, tk.END)
        self.entry_inicio.set('1')
        self.entry_fin.set('1')
        
        messagebox.showinfo("Éxito", f"{tipo_vehiculo} agregado al carrito.")

    # ==========================================
    # COMUNICACIÓN FINAL CON EL SERVIDOR
    # ==========================================
    def enviar_renta(self):
        if not self.solicitudes:
            messagebox.showwarning("Carrito Vacío", "No has agregado ningún vehículo a tu solicitud.")
            return

        try:
            respuesta = self.proxy.procesar_renta(self.usuario_id, self.solicitudes)
            if respuesta['exito']:
                msg = f"{respuesta['mensaje']}\n\nMonto total a pagar: ${respuesta['monto_pagar']}"
                messagebox.showinfo("Transacción Aprobada ✅", msg)
                # Limpiamos todo para una nueva renta
                self.solicitudes.clear()
                self.list_carrito.delete(0, tk.END)
                self.lbl_carrito.config(text="Vehículos en carrito: 0 / 3")
                self.refrescar_catalogo()
            else:
                messagebox.showerror("Transacción Rechazada ❌", respuesta['mensaje'])
        except Exception as e:
            messagebox.showerror("Error del Servidor", f"Ocurrió un error de comunicación:\n{e}")

    def refrescar_catalogo(self):
        try:
            self.catalogo = self.proxy.obtener_catalogo()
            for item in self.tree_catalogo.get_children():
                self.tree_catalogo.delete(item)
            
            tipos_vehiculos = []
            for tipo, datos in self.catalogo.items():
                unidades = datos.get('unidades', 0)
                self.tree_catalogo.insert('', tk.END, values=(tipo, f"{datos['cupo']} personas", f"${datos['costo']}", f"{unidades} u."))
                tipos_vehiculos.append(tipo)
                
            self.combo_tipo['values'] = tipos_vehiculos
            if tipos_vehiculos and self.combo_tipo.get() not in tipos_vehiculos:
                self.combo_tipo.current(0)
        except Exception as e:
            print(f"Error actualizando catálogo de UI: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClienteRentaApp(root)
    root.mainloop()