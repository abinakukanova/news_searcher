from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Like, Bookmark, Comment
from search_tfidf import TfidfSearcher
from searcher_fasttext import FastTextSearcher
import time


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pukataka@localhost/news_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

tf_idf = TfidfSearcher(matrix_file_name='tfidf_index_matrix.pickle')
fasttext = FastTextSearcher(fasttext_index_matrix='fasttext_index_matrix.pickle')


# Инициализация SQLAlchemy
db.init_app(app)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Создаем контекст приложения для SQLAlchemy
@app.before_request
def before_request():
    pass  # Удаляем db.session() — оно здесь не нужно

# Удаляем сессию после обработки запроса
@app.teardown_request
def remove_session(exception=None):
    db.session.remove()

# Функция для загрузки пользователя Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Маршруты
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/search', methods=['GET'])
def search():
    try:  # log exceptions
        if request.args:
            if "n" in request.args:  
                n = request.args["n"]
                if n:
                    n = int(n)
                else:
                    n = 10
            else:  
                n = 10
            metrics = []
            text = request.args["query_text"]  
            if "engine" in request.args:  
                engine = request.args["engine"]
            else:  
                engine = "tf-idf"
            if engine == "tf-idf":
                start_time = time.time()
                metrics = tf_idf.search(text, n=n)
                duration = time.time() - start_time
            elif engine == "fasttext":
                start_time = time.time()
                metrics = fasttext.search(text, n=n)
                duration = time.time() - start_time
            if not metrics[0][0]:
                return render_template("search.html", text=text, engine=engine)
            metrics = [item for item in metrics if item[0]]
            if n != len(metrics):
                n = len(metrics)
            return render_template("search.html", text=text, engine=engine, n=n, metrics=metrics, duration=duration)
        else:
            return render_template("search.html")
    except Exception as ex:  
        return render_template("search.html", exception=ex)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Пароли не совпадают!', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        # Создаем нового пользователя
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Аккаунт успешно создан!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)  # Входим в аккаунт пользователя
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('dashboard'))

        flash('Неверные учетные данные', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required  # Ограничиваем доступ только для авторизованных пользователей
def dashboard():
    return render_template('dashboard.html', user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'success')
    return redirect(url_for('home'))




@app.route('/like', methods=['POST'])
def like_news():
    """
    Добавление лайка к новости.
    """
    user_id = request.form.get('user_id')
    news_id = request.form.get('news_id')
    like = Like(user_id=user_id, news_id=news_id)
    db.session.add(like)
    db.session.commit()
    return jsonify({'message': 'Лайк добавлен!'})


@app.route('/comment', methods=['POST'])
def comment_news():
    """
    Добавление комментария к новости.
    """
    user_id = request.form.get('user_id')
    news_id = request.form.get('news_id')
    text = request.form.get('text')
    comment = Comment(user_id=user_id, news_id=news_id, text=text)
    db.session.add(comment)
    db.session.commit()
    return jsonify({'message': 'Комментарий добавлен!'})


@app.route('/bookmark', methods=['POST'])
def bookmark_news():
    """
    Добавление закладки на новость.
    """
    user_id = request.form.get('user_id')
    news_id = request.form.get('news_id')
    bookmark = Bookmark(user_id=user_id, news_id=news_id)
    db.session.add(bookmark)
    db.session.commit()
    return jsonify({'message': 'Закладка добавлена!'})




if __name__ == "__main__":
    app.run(debug=True)