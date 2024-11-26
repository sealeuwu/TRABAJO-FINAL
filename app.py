from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = 'clave_secreta_para_flash'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'  # Configura la base de datos SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)


class Biblioteca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    anime_nombre = db.Column(db.String(150), nullable=False)
    anime_tipo = db.Column(db.String(100))
    anime_calificacion = db.Column(db.Integer)
    anime_estado = db.Column(db.String(100))
    usuario = db.relationship('Usuario', backref=db.backref('bibliotecas', lazy=True))


with app.app_context():
    db.create_all()


datos_animes = [
    { "nombre": "Attack on Titan", "tipo": "acción", "calificacion": 5, "estado": "completado", "imagen": "https://via.placeholder.com/100?text=AoT", "resumen": "Los titanes atacan la humanidad, y un joven luchará por salvar el mundo.", "link": "https://example.com/aot" },
    { "nombre": "My Hero Academia", "tipo": "acción", "calificacion": 5, "estado": "en_emision", "imagen": "https://via.placeholder.com/100?text=MHA", "resumen": "Un chico sin superpoderes aspira a convertirse en el héroe más grande.", "link": "https://example.com/mha" },
    { "nombre": "One Piece", "tipo": "aventura", "calificacion": 5, "estado": "en_emision", "imagen": "https://via.placeholder.com/100?text=One+Piece", "resumen": "Un joven pirata busca el tesoro más grande del mundo.", "link": "https://example.com/onepiece" },
    { "nombre": "Hunter x Hunter", "tipo": "aventura", "calificacion": 5, "estado": "completado", "imagen": "https://via.placeholder.com/100?text=HxH", "resumen": "Un niño aspira a convertirse en cazador y descubrir los secretos del mundo.", "link": "https://example.com/hxh" },
    { "nombre": "One Punch Man", "tipo": "comedia", "calificacion": 4, "estado": "completado", "imagen": "https://via.placeholder.com/100?text=OPM", "resumen": "Un hombre extremadamente poderoso busca un reto que lo haga sentir vivo.", "link": "https://example.com/onepunchman" },
    { "nombre": "KonoSuba", "tipo": "comedia", "calificacion": 5, "estado": "completado", "imagen": "https://via.placeholder.com/100?text=KonoSuba", "resumen": "Un joven es reencarnado en un mundo de fantasía donde forma un equipo poco común.", "link": "https://example.com/konosuba" },
    { "nombre": "Your Name", "tipo": "romance", "calificacion": 5, "estado": "completado", "imagen": "https://via.placeholder.com/100?text=Your+Name", "resumen": "Dos jóvenes intercambian cuerpos y se enamoran a través del tiempo.", "link": "https://example.com/yourname" },
    { "nombre": "Toradora!", "tipo": "romance", "calificacion": 4, "estado": "completado", "imagen": "https://via.placeholder.com/100?text=Toradora", "resumen": "Una chica pequeña y un chico rudo forman una extraña relación llena de enredos románticos.", "link": "https://example.com/toradora" },
    { "nombre": "Haikyuu!!", "tipo": "deportes", "calificacion": 5, "estado": "en_emision", "imagen": "https://via.placeholder.com/100?text=Haikyuu", "resumen": "Un joven que sueña con ser un gran jugador de voleibol se une a su escuela.", "link": "https://example.com/haikyuu" },
    { "nombre": "Kuroko no Basket", "tipo": "deportes", "calificacion": 5, "estado": "completado", "imagen": "https://via.placeholder.com/100?text=Kuroko", "resumen": "Un equipo de baloncesto lucha por llegar a la cima, con un jugador misterioso que es su as bajo la manga.", "link": "https://example.com/kuroko" },
    { "nombre": "Death Note", "tipo": "sobrenatural", "calificacion": 5, "estado": "completado", "imagen": "https://via.placeholder.com/100?text=Death+Note", "resumen": "Un estudiante encuentra un cuaderno que le permite matar a cualquier persona cuyo nombre escriba en él.", "link": "https://example.com/deathnote" },
    { "nombre": "Mob Psycho 100", "tipo": "sobrenatural", "calificacion": 4, "estado": "en_emision", "imagen": "https://via.placeholder.com/100?text=Mob", "resumen": "Un joven con poderes psíquicos lucha por llevar una vida normal.", "link": "https://example.com/mobpsycho100" },
    { "nombre": "Steins;Gate", "tipo": "psicológico", "calificacion": 5, "estado": "completado", "imagen": "https://via.placeholder.com/100?text=SteinsGate", "resumen": "Un grupo de jóvenes descubre cómo viajar en el tiempo y las consecuencias de sus actos.", "link": "https://example.com/steinsgate" },
    { "nombre": "Monster", "tipo": "psicológico", "calificacion": 5, "estado": "completado", "imagen": "https://via.placeholder.com/100?text=Monster", "resumen": "Un neurocirujano se ve envuelto en un misterio que podría destruir su vida.", "link": "https://example.com/monster" },
    { "nombre": "Your Lie in April", "tipo": "melancolicas", "calificacion": 5, "estado": "completado", "imagen": "https://via.placeholder.com/100?text=YLIAS", "resumen": "Un joven pianista lucha con el dolor y la pérdida mientras redescubre la música.", "link": "https://example.com/yourlieinapril" },
    { "nombre": "Clannad", "tipo": "melancolicas", "calificacion": 5, "estado": "completado", "imagen": "https://via.placeholder.com/100?text=Clannad", "resumen": "Un grupo de estudiantes enfrenta desafíos emocionales mientras buscan un propósito.", "link": "https://example.com/clannad" },
]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:  
            flash("Debes iniciar sesión para acceder a esta página.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))  
    return render_template('index.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usuario = Usuario.query.filter_by(username=username, password=password).first()
        if usuario:
            session['user'] = username  # Iniciar sesión
            flash("Sesión iniciada correctamente.")
            return redirect(url_for('index'))
        else:
            flash("Usuario o contraseña incorrectos.")
            return redirect(url_for('login'))
    return render_template('login.html')

# Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if Usuario.query.filter_by(username=username).first():
            flash("Este usuario ya existe.")
            return redirect(url_for('register'))
        nuevo_usuario = Usuario(username=username, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Registro exitoso. Ahora puedes iniciar sesión.")
        return redirect(url_for('login'))
    return render_template('register.html')

# Recomendaciones de animes
@app.route('/recomendar', methods=['GET'])
@login_required
def recomendar():
    tipo = request.args.get('tipo', 'random')  
    calificacion = request.args.get('calificacion', '5')  
    estado = request.args.get('estado', 'completado')  

    calificacion = int(calificacion) if calificacion.isdigit() else 5  

    recomendaciones = [
        anime for anime in datos_animes
        if (tipo == "random" or anime["tipo"] == tipo)
        and anime["calificacion"] >= calificacion
        and anime["estado"] == estado
    ]

    return render_template('recomendaciones.html', recomendaciones=recomendaciones)

# Biblioteca
@app.route('/biblioteca')
@login_required
def biblioteca():
    username = session['user']
    usuario = Usuario.query.filter_by(username=username).first()
    
    
    biblioteca_usuario = Biblioteca.query.filter_by(usuario_id=usuario.id).all()
    
    
    animes_en_biblioteca = []
    for item in biblioteca_usuario:
        anime = next((anime for anime in datos_animes if anime['nombre'] == item.anime_nombre), None)
        if anime:
            animes_en_biblioteca.append(anime)

    return render_template('biblioteca.html', biblioteca=animes_en_biblioteca)

@app.route('/agregar_a_biblioteca/<nombre_anime>', methods=['GET'])
@login_required
def agregar_a_biblioteca(nombre_anime):
    username = session['user']
    usuario = Usuario.query.filter_by(username=username).first()
    
    
    anime_en_biblioteca = Biblioteca.query.filter_by(usuario_id=usuario.id, anime_nombre=nombre_anime).first()
    
    if anime_en_biblioteca:
        flash(f"¡El anime {nombre_anime} ya está en tu biblioteca!")
    else:
        
        nuevo_anime = Biblioteca(usuario_id=usuario.id, anime_nombre=nombre_anime)
        db.session.add(nuevo_anime)
        db.session.commit()
        flash(f"{nombre_anime} se agregó a tu biblioteca.")
    
    return redirect(url_for('biblioteca'))


# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Sesión cerrada correctamente.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
