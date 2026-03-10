from base_datos.conexion import database

class Usuario(database.Model): 
    __tablename__ = "usuarios"

    id = database.Column(database.Integer, primary_key=True)
    nombre = database.Column(database.String(100), nullable=False)
    apellido = database.Column(database.String(100), nullable=False)
    correo_electronico = database.Column(database.String(100), nullable=False, unique=True)
    contrasena = database.Column(database.String(100), nullable=False)
    telefono = database.Column(database.String(15))
    fecha_nacimiento = database.Column(database.Date)
    rol = database.Column(database.String(12), nullable=False)
    fecha_registro = database.Column(database.DateTime, default=database.func.current_timestamp())

    def __str__(self):
        return f"""ID: {self.id}
                Nombre: {self.nombre}
                Apellido: {self.apellido}
                Correo Electrónico: {self.correo_electronico}
                Contraseña: {self.contrasena}
                Telefono: {self.telefono}
                Fecha de Nacimiento: {self.fecha_nacimiento}
                Rol: {self.rol}
                Fecha de Regristo: {self.fecha_registro} """
    