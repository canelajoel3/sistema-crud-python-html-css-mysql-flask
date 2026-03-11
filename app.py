from flask import Flask 
from flask import render_template, request, redirect, url_for, session, jsonify
from base_datos.conexion import database
from base_datos.models import Usuario, Curso
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os 


app = Flask(__name__)
app.config["DEBUG"] = True 

# CONEXION A LA BASE DE DATOS 
# USER = "canela"
# PASSWORD = "1313"
# URL_DB = "localhost"
# NAME_DB = "paginaweb"

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

print(f"DEBUG - El usuario es: {os.getenv('DB_USER')}")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqldb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 

database.init_app(app) 

with app.app_context():
    database.create_all() 


app.secret_key = os.urandom(25)

# Pagina de inicio en la pagina 
@app.route("/")
def index():
    return redirect(url_for("inicio"))

@app.route("/login", methods=["GET", "POST"])
def inicio():
    if request.method == "POST":
        correo = request.form.get("correo_electronico")
        contrasena = request.form.get("contrasena")

        if not correo or not contrasena:
            return "Por favor ingrese la contraseña o el correo"

        usuario = Usuario.query.filter_by(correo_electronico=correo).first()

        if not usuario: 
            return "Usuario no Registrado, Por favor registrarse para acceder..." 
        
        if not check_password_hash(usuario.contrasena, contrasena):
            return "Contraseña Incorrecta."

        # GUARDAR USUARIO EN SESSION
        session["usuario_id"] = usuario.id
        session["usuario_nombre"] = usuario.nombre
        session["usuario_rol"] = usuario.rol
        session["usuario_fecha"] = usuario.fecha_registro.strftime("%B %Y")

        if usuario.rol == "admin":
            return redirect(url_for("admin"))

        return redirect(url_for("dashboard"))
        
    return render_template("login.html") 

@app.route("/registro", methods=["GET", "POST"])
def registro():

    if request.method == "POST": 
        terminos = request.form.get("terminos")
        if not terminos: 
            return "Debe aceptar los términos"
        # TOMAR LOS DATOS DEL FOMULARIO
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        correo_electronico = request.form["correo_electronico"]
        contrasena = request.form["contrasena"]
        telefono = request.form.get("telefono")
        fecha_nacimiento = request.form.get("fecha_nacimiento")
        rol = "usuario"

        usuario_existente = Usuario.query.filter_by(correo_electronico=correo_electronico).first()
        if usuario_existente:
            return "Este usuario ya esta registrado"
    
        # CREAR USUARIO CON CONTRASEÑA HASH
        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            correo_electronico=correo_electronico,
            contrasena=generate_password_hash(contrasena),
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento,
            rol=rol
        ) 
        
        # GUARDAR EN LA BASE DE DATOS
        database.session.add(nuevo_usuario)
        database.session.commit()

        # REDIRIGIR AL LOGIN
        return redirect(url_for("inicio"))
        

    return render_template("registro.html") 


@app.route("/dashboard")
def dashboard():
    if "usuario_id" not in session:
        return redirect(url_for("inicio"))
    
    usuario_id = session["usuario_id"]
    usuario = Usuario.query.get(usuario_id)
    cursos = usuario.cursos
    
    return render_template(
        "dashboard.html", 
        nombre=session["usuario_nombre"],
        rol=session["usuario_rol"],
        fecha=session["usuario_fecha"],
        cursos=cursos
    )

@app.route("/logout")
def salir():
    session.clear()
    return redirect(url_for("inicio"))

@app.route("/admin")
def admin():
    if "usuario_id" not in session:
        return redirect(url_for("inicio"))
    
    if session["usuario_rol"] != "admin":
        return "Acceso denegado" 
    
    usuarios = Usuario.query.all()
    
    return render_template("admin.html", usuarios=usuarios)

@app.route("/eliminar_usuario/<int:id>")
def eliminar_usuario(id):

    if "usuario_id" not in session: 
        return redirect(url_for("inicio"))
    
    if session["usuario_rol"] != "admin":
        return "Acceso Denegado"
    
    usuario = Usuario.query.get(id)

    if usuario:
        database.session.delete(usuario)
        database.session.commit()

    return redirect(url_for("admin"))

@app.route("/crear_curso", methods=["POST"])
def crear_curso():
    usuario_id = session.get("usuario_id")

    if not usuario_id:
        return "Debes iniciar sesiòn para crear un curso."
    
    nombre = request.form.get("nombre_curso")
    descripcion = request.form.get("descripcion")
    instructor = request.form.get("instructor")

    usuario = Usuario.query.get(usuario_id)

    if usuario:
        try:
            nuevo_curso = Curso(
                nombre_curso=nombre,
                descripcion=descripcion,
                instructor=instructor,
                usuario_id=usuario.id
            )
            database.session.add(nuevo_curso)
            database.session.commit()

            return redirect(url_for("dashboard"))
        
        except Exception as e:
            database.session.rollback()
            return f"Error al crear el curso: {e}"
    else: 
        return "Usuario no encontrado, no se puede crear el curso."
    

@app.route("/api/usuarios/<int:usuarios_id>/cursos", methods=["GET"])
def obtener_cursos_usuarios(usuarios_id):
    usuario = Usuario.query.get(usuarios_id)

    if not usuario: 
        return jsonify({"Error": "Usuario no encontrado"}), 404

    lista_curso = []
    for curso in usuario.cursos:
        lista_curso.append({
            "id": curso.id,
            "nombre_curso": curso.nombre_curso,
            "descripcion": curso.descripcion,
            "instructor": curso.instructor,
            "fecha_creacion": curso.fecha_creacion.strftime("%Y-%m-%d")
        })

    return jsonify(lista_curso)


@app.route("/api/cursos", methods=["GET"])
def obtener_todos_cursos():
    cursos = Curso.query.all()

    lista_curso = []
    for curso in cursos:
        lista_curso.append({
            "id": curso.id,
            "nombre_curso": curso.nombre_curso,
            "descripcion": curso.descripcion,
            "instructor": curso.instructor,
            "usuario_id": curso.usuario_id,
            "fecha_creacion": curso.fecha_creacion.strftime("%Y-%m-%d")
        })

    return jsonify(lista_curso)

    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)