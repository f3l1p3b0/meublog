from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)
UPLOAD_FOLDER='static/images'
ALLOWED_EXTENSIONS={'png','jpg','jpeg','gif'}
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  
app.secret_key="^TTvrXXjxkMx@-2~VpJBhjWR@5Vt>jX'^kNY"
USUARIO="admin"
SENHA_HASH=generate_password_hash("profiterolis")
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER=os.path.join(BASE_DIR,'static','images')
POSTS_FILE=os.path.join(BASE_DIR,'posts.json')
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

def carregar_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE,"r",encoding="utf-8")as f:
            return json.load(f)
    return []

def salvar_posts(posts):
    with open(POSTS_FILE,"w",encoding="utf-8")as f:
        json.dump(posts,f,indent=4,ensure_ascii=False)

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.',1)[1].lower()in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    posts=carregar_posts()
    return render_template('index.html',posts=posts)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if not session.get("logado"):
        return redirect(url_for("login"))
    if request.method == 'POST':
        if 'imagem' not in request.files:
            return "Nenhum arquivo enviado", 400 
        file = request.files['imagem']
        if file.filename == '':
            return "Nenhum arquivo selecionado", 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(caminho)  
            novo_post = {
                'id': str(uuid.uuid4()),
                'titulo': request.form['titulo'],
                'conteudo': request.form['conteudo'],
                'imagem': f"images/{filename}"
            }
            posts = carregar_posts()
            posts.insert(0, novo_post)
            salvar_posts(posts)
            return redirect(url_for('index'))
        else:
            return "Arquivo inválido", 400
    return render_template('add.html')

@app.route('/post/<post_id>', methods=['GET', 'POST'])
def ver_post(post_id):
    posts = carregar_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    if not post:
        return "Post não encontrado", 404
    if request.method == 'POST':
        nome = request.form['autor']
        texto = request.form['comentario']
        comentario = {"autor": nome, "texto": texto}
        post.setdefault("comentarios", []).append(comentario)
        salvar_posts(posts)
        flash("Comentário adicionado!", "success")
        return redirect(url_for('ver_post', post_id=post_id))
    return render_template('post.html', post=post)

@app.route('/edit/<post_id>', methods=['GET', 'POST'])
def edit(post_id):
    if not session.get("logado"):
        return redirect(url_for("login"))
    posts = carregar_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    if not post:
        return "Post não encontrado", 404
    if request.method == 'POST':
        post['titulo'] = request.form['titulo']
        post['conteudo'] = request.form['conteudo']
        file = request.files.get('imagem')
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(caminho)
            post['imagem'] = f"images/{filename}"
        salvar_posts(posts)
        flash('Post atualizado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('edit.html', post=post)

@app.route('/delete/<post_id>', methods=['POST'])
def delete(post_id):
    if not session.get("logado"):
        return redirect(url_for("login"))
    posts = carregar_posts()
    posts = [p for p in posts if p['id'] != post_id]
    salvar_posts(posts)
    flash('Post excluído com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario'].strip()
        senha = request.form['senha'].strip()
        if usuario==USUARIO and check_password_hash(SENHA_HASH,senha):
            session['logado'] = True
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('index'))
        else:
            flash("Usuário ou senha incorretos", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logado', None)
    flash('Logout realizado.',"success")
    return redirect(url_for('login'))

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

if __name__ =='__main__':
    port=int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0',port=port)
