from flask import *
from flask_sqlalchemy import *
from flask_login import login_required, logout_user, current_user, login_user, UserMixin, current_user
from werkzeug.security import *
from datetime import datetime
from sqlalchemy import *
from pytz import timezone
from flask_login import LoginManager
import random
import string
import smtplib
from flask_migrate import Migrate

### initializations ###

## Application configuration
app = Flask(__name__, static_folder="./static")
app.secret_key = "pass"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

## Login Managaer
lm = LoginManager()
lm.init_app(app)

# Database File
db = SQLAlchemy(app)
migrate = Migrate(app, db)


## User Class
class User(db.Model, UserMixin):
    __tablename__ = "Login"
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String, unique=True)
    firstName = db.Column(db.String)
    lastName = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)
    bday = db.Column(db.String)
    gender = db.Column(db.String)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
            return check_password_hash(self.password, password)
    def __repr__(self):
        return "User {0}".format(self.id)

class posts(db.Model):
    __tablename__ = "Post"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = True)
    author = db.Column(db.String)
    username = db.Column(db.String)
    content = db.Column(db.Text)
    date =  db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return 'Post #{0}'.format(str(self.id))

#### Pages ####

@app.route("/")
@app.route("/index")

##  Check if user is logged in, if not redirect to login/registration page
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    else:
        return render_template("index.html")
        
##  Login
@app.route("/login", methods=["GET", "POST"])
def login_():
    print('main file')
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        userQ = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=userQ).first()
        if request.form["username"] != None or user != "":
            if user.check_password(request.form["password"]):
                login_user(user)
                return redirect(url_for("home"))
            else:
                passwordErr = "Incorrect password"
        else:
            passwordErr = "Username/password error"
            return redirect(request.referrer)
        return redirect(url_for("login_"))
    return redirect("/")


##  Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        password2 = request.form["password2"]
        gender = request.form["gender"]
        global err
        if User.query.filter_by(email=email).first() is None:
            if User.query.filter_by(username=username).first() is None:
                if password == password2:
                    client = User(first=firstName, last=lastName, email=email, gender=gender, username=username, bday=date)
                    client.set_password(password)
                    db.session.add(client)
                    db.session.commit()
                    login_user(client)
                    return redirect(url_for("login_"))
                else:
                    err = "Password not confirmed - passwords need to match"
                    return redirect(request.referrer)
            else:
                err = "Cannot select a username already exists"
                return redirect(request.referrer)
        else:
            err = "Cannot select an email that already exists"
            return redirect(request.referrer)
    return redirect("/")


##  Home
@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    return render_template("home.html", User=User())

## Making posts
@app.route("/home/new", methods=["GET", "POST"])
@login_required
def post_Announcement():
    if request.method == "POST":
        title = "{0} says".format(current_user.username)
        author = "{0} {1}".format(current_user.firstName, current_user.lastName)
        userPost = request.form["content"]
        return redirect(request.referrer)
    else:
        return render_template("/includes/new_post.html")


##  Account 
@app.route("/my-account", methods=["GET", "POST"])
@login_required
def profile():
    userPosts = posts.query.filter_by(username = current_user.username).all()
    return render_template("my-account.html", User=User(), posts=userPosts)


##  Search function
@app.route("/search", methods=["GET", "POST"])
def search_():
    if request.method == "POST":
        search = str(request.form.get('search'))
        search1 = User.query.filter(User.firstName.like(search))
        query = search1.all()
        return render_template("search.html", search=query)
    else:
        return redirect("/")

@app.route('/user/<username>')
def findUser(username):
    posts_ = posts.query.filter_by(username=username).order_by(posts.date.desc()).all()
    return render_template("user1.html", user=User.query.filter_by(username=username).first(), posts=posts_, User=User)
#Logout
@app.route("/logout")
@login_required
def logout_page():
    """User log-out logic."""
    logout_user()
    return redirect("/")

#Made just for Making it possible to edit profile information
@app.route("/logout1")
@login_required
def logout1():
    logout_user()

@lm.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None    

@lm.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    return redirect(url_for('index'))

#Make it compatible to deploy on heroku
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
