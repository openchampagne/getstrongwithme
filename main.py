import eventlet
from flask import *
from flask_socketio import SocketIO, join_room, leave_room, rooms, emit
from flask_session import Session
from flask_sqlalchemy import *
from flask_login import login_required, logout_user, current_user, login_user, UserMixin, current_user
from werkzeug.security import *
from datetime import datetime
from sqlalchemy import *
from pytz import timezone
from flask_login import LoginManager
from collections import defaultdict
import random
import string
import smtplib
from flask_migrate import Migrate

### initializations ###
upload_profile = "./static/images/profile"
upload_media = "./static/posts"

## Application configuration
app = Flask(__name__, static_folder="./static")
app.debug = False
app.secret_key = 'pass'
app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['UPLOAD_PROFILE'] = upload_profile
app.config['UPLOAD_MEDIA'] = upload_media

## Login Managaer
lm = LoginManager()
lm.init_app(app)

## Database File
db = SQLAlchemy(app)
migrate = Migrate(app, db)

## SocketIO 
Session(app)
socketio = SocketIO(app)
users = []

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
    about_me = db.Column(db.String(140), default="No Bio")
    location = db.Column(db.String, default="No Location")
    profile_pic = db.Column(db.String, default="/static/images/profile/404.jpg")

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

class DirectMessage(db.Model):
    __tablename__ = "directMessages"
    id = db.Column(db.Integer, primary_key = True)
    rec_id = db.Column(db.Integer)
    send_id = db.Column(db.Integer)
    message = db.Column(db.Text)
    date = db.Column(db.Text)

    def __repr__(self):
        return 'Message id: {0}'.format(str(self.id))

class friendRequests(db.Model):
    __tablename__="friendRequests"
    id=db.Column(db.Integer, primary_key=True)
    user_from=db.Column(db.String)
    user_to=db.Column(db.String)

class Chatroom(db.Model):
    __tablename__ = "chatrooms"
    id = db.Column(db.Integer, primary_key = True)
    rec_id = db.Column(db.Integer)
    send_id = db.Column(db.Integer)
    chatroom = db.Column(db.String)

    def __repr__(self):
        return 'Chatroom: {0}'.format(str(self.id))

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

@app.route("/file", methods=["GET", "POST"])
@login_required
def file_upload():
    if request.method == "POST":
        file=request.files['file']
        filename=file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('includes/file.html')
    else:
        return render_template('includes/file.html')

##  Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        firstName = request.form["first"]
        lastName = request.form["last"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["pass1"]
        password2 = request.form["pass2"]
        gender = request.form["gender"]
        bday = request.form["bday"]
        global err
        if User.query.filter_by(email=email).first() is None:
            if User.query.filter_by(username=username).first() is None:
                if password == password2:
                    client = User(firstName=firstName, lastName=lastName, email=email, gender=gender, username=username, bday=bday)
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

## Returns list of Direct Messages 
def dms_():
    dms_ = []
    dms = DirectMessage.query.filter_by(rec_id=current_user.id).all()
    for dm in dms:
        users = User.query.filter_by(id=dm.send_id).first()
        dms_.append([users.firstName, dm.message, dm.date])
    return dms_

## Home
@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    user_posts = posts.query.order_by(posts.date.desc()).all()
    return render_template("home.html", User=User(), posts=user_posts, blogposts=posts.query.order_by(posts.date.desc()), dms=dms_())

## Making posts
@app.route("/home/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        post_title = "Post by "+current_user.username
        post_content = request.form['content']
        post_author = current_user.firstName+" "+current_user.lastName
        post_media = request.files.get('media')
        #If the user uploads or chooses to upload images
        if post_media:
            if post_content != "":
                file=request.files['media']
                filename = file.filename
                extension = filename.split('.')[1]
                letters = string.ascii_lowercase
                random1 = ''.join(random.choice(letters) for i in range(10)) 
                medianame = random1+"."+extension
                pathtomedia = "/static/posts/"+medianame
                new_post = posts(title=post_title, content="media,"+pathtomedia+","+post_content,author=post_author, username=current_user.username)
                file.save(os.path.join(app.config['UPLOAD_MEDIA'], medianame))
                db.session.add(new_post)
                db.session.commit()
                getd=posts.query.all()[-1].id
                #like= likes(pid=int(getd),total=0)
                #db.session.add(like)
                db.session.commit()
                return redirect(request.referrer)
            else:
                file=request.files['media']
                filename = file.filename
                extension = filename.split('.')[1]
                letters = string.ascii_lowercase
                random1 = ''.join(random.choice(letters) for i in range(10)) 
                medianame = random1+"."+extension
                pathtomedia = "/static/posts/"+medianame
                new_post = posts(title=post_title, content="media,"+pathtomedia,author=post_author, username=current_user.username)
                file.save(os.path.join(app.config['UPLOAD_MEDIA'], medianame))
                db.session.add(new_post)
                db.session.commit()
                getd=posts.query.all()[-1].id
                #like= likes(pid=int(getd),total=0)
                #db.session.add(like)
                db.session.commit()
                return redirect(request.referrer)
        #If no photo is chosen
        else:
            if post_content != "":
                new_post = posts(title=post_title, content=post_content,author=post_author, username=current_user.username)
                db.session.add(new_post)
                db.session.commit()
                getd=posts.query.all()[-1].id
                #like= likes(pid=int(getd),total=0)
                #db.session.add(like)
                db.session.commit()
                return redirect(request.referrer)
            else:
                global errmsg
                errmsg = "Cannot Post Somethig Not written! "
                return redirect(request.referrer)
    else:
        all_post = posts.query.all()
        return render_template('includes/new_post.html')


##  Account 
@app.route("/my-account", methods=["GET", "POST"])
@login_required
def profile():
    userPosts = posts.query.filter_by(username = current_user.username).all()
    return render_template("my-account.html", User=User(), posts=userPosts)

@app.route("/my-account/edit/<int:id>",methods=['GET','POST'])
def profile_info_change(id):
    if request.method == "POST":
        info = User.query.get(id)
        info.username = request.form['username']
        info.firstname=request.form['firstName']
        info.lastname=request.form['lastName']
        info.email=request.form['email']
        info.about_me = request.form['about_me']
        profilepic=request.files.get('file')
        if profilepic: 
            file=request.files.get('file')
            filename= file.filename
            new_filename=current_user.username+"."+filename.split('.')[1]
            file.save(os.path.join(app.config['UPLOAD_PROFILE'], new_filename))
            info.profile_pic="/static/images/my-account/"+new_filename
            db.session.commit()
            return redirect(request.referrer)
        db.session.commit()
        return redirect(request.referrer)
    else:
        return redirect("/profile")

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

@app.route('/user/<username>', methods=["GET", "POST"])
def findUser(username):
    user = User.query.filter_by(username=username).first()
    posts_ = posts.query.filter_by(username=username).order_by(posts.date.desc()).all()
    return render_template("user1.html", user=user, posts=posts_, User=User)

@app.route('/addfriend/<username>',methods=['GET','POST'])
def addfriend(username):
    a=User.query.filter_by(username=username).first()
    if request.method == "POST":
        user_to=a.username
        user_from=current_user.username
        addf=friendRequests(user_from=user_from,user_to=user_to)
        db.session.add(addf)
        b="/user/"+username
        db.session.commit()
        return redirect(request.referrer)

#################################################### 
## Room Dict
r = {}
r = defaultdict(lambda: 0, r)
## Chat function
@app.route('/chat', methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        username = current_user.username
        rec_id = str(request.form.get('rec-id'))
        recipient = User.query.filter_by(id=rec_id).first()
        sql = 'SELECT COUNT(*) FROM chatrooms WHERE rec_id = {0} AND send_id = {1} OR rec_id = {1} AND send_id = {0}'.format(rec_id, current_user.id)
        print("\n\nRecipient ID = {0}".format(rec_id))
        print('Current user ID = {0}'.format(current_user.id))
        print('The recipient is {0}'.format(recipient.username))

        ## query Chatrooms table if a chatroom exists by checking if 2 ids exist in 1 query, pull chatroom string if it does
        rec_id = int(rec_id)
        result = db.engine.execute(sql)
        result_ = [row[0] for row in result]
        print(result_[0])
        # If 2 ids exist in 1 query
        if result_[0] != 0:
            chatroom = Chatroom.query.filter_by(rec_id=rec_id, send_id=current_user.id).first()
            # print('\n\nchatroom 1: {0}'.format(chatroom.chatroom))
            if chatroom == None:
                chatroom = Chatroom.query.filter_by(rec_id=current_user.id, send_id=rec_id).first()
                # print('\n\nchatroom 2: {0}'.format(chatroom.chatroom))
        ## if it doesn't exist, generate random string
            chatroom = chatroom.chatroom
        else:
            chatroom = (''.join(random.choice(string.ascii_uppercase) for i in range(9)))
            print('Chatroom wasn\'t found, new chatroom made \nChatroom: {0}\n'.format(chatroom))
            chatroom_ = Chatroom(rec_id=rec_id, send_id=current_user.id, chatroom=chatroom)
            db.session.add(chatroom_)
            db.session.commit()
        print(chatroom)
        room = chatroom
        ## 
        session['username'] = username
        session['room'] = room
        session['rec_id'] = rec_id
        session['recipient_name'] = recipient.firstName
    return render_template("chat.html", session=session) 


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    rec_id = session.get('rec_id')
    recipient = User.query.filter_by(id=rec_id).first()
    print('Users in chatroom: {0}'.format(users))
    print('Rooms active: {0}'.format(r))
    
    if r[room] > 1:
        emit('message', {'msg': '{0}:{1}'.format(session.get('username'), message['msg'])}, room=room)
        print('Number of users in chat: {0}'.format(r[room]))
    else:
        send_id = current_user.id
        date_ = '{3}:{4} - {0}/{1}/{2}'.format(datetime.now().day, datetime.now().month, datetime.now().year, datetime.now().hour, datetime.now().minute)
        dm = DirectMessage(rec_id=rec_id, send_id=send_id, message=message['msg'], date=date_)
        db.session.add(dm)
        db.session.commit()
        emit('message', {'msg': '{0}:{1}'.format(session.get('username'), message['msg'])}, room=room)
        emit('status', {'msg': '{0} is currenly offline, your message was sent to their inbox.'.format(recipient.firstName)}, room=room)


@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
    join_room(room)
    if session.get('username') not in users:
        users.append(session.get('username'))
    # print('Users in chatroom: {0}'.format(users))
    r[room] += 1
    print(r)
    emit('status', {'msg': '{0} is online.'.format(session.get('username'))}, room=room)

@socketio.on('left', namespace='/chat')
def left(message):
    username = session.get('username')
    print(username)
    room = session.get('room')
    r[room] -= 1
    print(r)
    leave_room(room)
    users.remove(username)
    session.clear()
    emit('status', {'msg': '{0} is offline.'.format(username)}, room=room)


#################################################### 

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
    socketio.run(app)
    db.create_all()
    app.run(debug=True)
