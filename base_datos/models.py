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

    cursos = database.relationship("Curso", backref="usuarios")

    
class Curso(database.Model):
    __tablename__ = "cursos"

    id = database.Column(database.Integer, primary_key=True)
    nombre_curso = database.Column(database.String(100), nullable=False)
    descripcion = database.Column(database.Text)
    instructor = database.Column(database.String(100), nullable=False)
    fecha_creacion = database.Column(database.DateTime, default=database.func.current_timestamp())

    usuario_id = database.Column(database.Integer, database.ForeignKey("usuarios.id"))