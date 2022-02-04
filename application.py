import os

from flask import Flask, render_template, redirect, url_for, request, abort, session
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room, send

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
socketio = SocketIO(app)
Session(app)

rooms = {}
chats = {}
rooms['universalChat'] = 'thispasswordisbeyondyourreach'
chats['universalChat'] = []

def nameCheck():
    if 'name' in session:
        return True
    else:
        return False

def delName():
    if nameCheck():
        session.pop('name', None)
    else:
        pass

def roomCheck():
    if 'room' in session:
        return True
    else:
        return False

def delRoom():
    if roomCheck():
        session.pop('room', None)
    else:
        pass

def addRoom(room, pwd):    
    if room in rooms.keys():
        return -1
    else:
        rooms[room] = pwd
        print(rooms)
        return 1

def removeRoom(room, pwd):
    if room in rooms.keys():
        print('initiated')
        if rooms[room] == pwd:
            rooms.pop(room)
            print('room found')
            if delChats(room):
                print('success!')
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def createChats(room):
    if room in chats.keys():
        return -1
    else:
        chats[room] = []
        print(chats)
        return 1

def addMessage(room, message):
    try:    
        chats[room].append(message)
        print(chats[room])
    except:
        return -1
    
    return 1
    

def retChats(room):
    return chats[room]

def delChats(room):
    chats.pop(room)
    return True
   

def messDelete(room, mess):
    if room in chats.keys():
        for m in chats[room]:
            if m == mess:
                print('reached here!')
                chats[room].remove(m)
                return 1
            else:
                pass
    else:
        return -1
    

@app.route("/")
def index():
    if nameCheck():
        if roomCheck():
            return redirect(url_for('chatArea', room=session['room']))
        else:
            return redirect(url_for('initChat'))
    else:
        return render_template('index.html')

@app.route('/getuser', methods=["GET", "POST"])
def getuser():
    if request.method == "POST":
        name = request.form.get("name")
        if name == 'Admin':
            return render_template('error.html', message="Admin is not allowed!")
        else:
            session['name'] = name
            print('Init chats: ')
            print(rooms, chats)
            return render_template('next.html', name=name, roomnames=rooms.keys())
    else:
        return render_template('error.html', message="Method not allowed!")

@app.route('/initChat')
def initChat():
    if nameCheck():
        delRoom()
        return render_template('next.html', name=session['name'], roomnames=rooms.keys())
    else:
        return render_template('error.html', message="Method not allowed!")

@app.route('/newroom', methods=["GET", "POST"])
def newroom():
    if nameCheck():
        delRoom()
        if request.method == "POST":
            room = request.form.get('roomname')
            rpass = request.form.get('roompass')
            session['room'] = room
            if addRoom(room, rpass):
                if createChats(room):
                    return redirect(url_for('chatArea', room=room))
                else:
                    return render_template('error.html', message="Cannot initialize room!")
            else:
                return render_template('error.html', message="Room already exists!")
        else:
            return render_template('error.html', message="Method not allowed!")
    else:
        return render_template('error.html', message="User not logged in!")

@app.route('/joinroom', methods=["GET", "POST"])
def joinroom():
    if nameCheck():
        delRoom()
        if request.method == "POST":
            room = request.form.get('roomname')
            print(room+'is none')
            if room in rooms.keys():
                session['room'] = room
                return redirect(url_for('chatArea', room=room))
            else:
                return render_template('error.html', message="Room does not exist!")
        else:
            return render_template('error.html', message="Method not allowed!")     
    else:
        return render_template('error.html', message="User not logged in!")

@app.route('/chatArea/<room>')
def chatArea(room):
    if nameCheck():
        if roomCheck():
            chats = retChats(room)
            print('Chat area:- ')
            print(rooms, chats)
            dataset = []
            for m in chats:
                dataset.append(m.split('-')[0])
            #print(dataset)
            n = len(dataset)
            return render_template('chatarea.html', room=session['room'], name=session['name'], chats_dset_n = zip(chats,dataset,range(0,n)))
        else:
            return render_template('error.html', message="Room not found!")
    else:
        return render_template('error.html', message="User not logged in!")

@app.route('/logout')
def logout():
    if nameCheck():
        delName()
        print('logout route:-')
        print(rooms, chats)
        return redirect(url_for('index'))
    else:
        return render_template('error.html', message="User already logged out!")

@app.route('/back')
def back():
    if nameCheck():
        if roomCheck():
            delRoom()
        return redirect(url_for('initChat'))
    else:
        return render_template('error.html', message="Cannot process request!")

@app.route('/delroom')
def delroom():
    if nameCheck():
        if roomCheck():
            return render_template('askpass.html')
        else:
            return render_template('error.html', message="Room not found!")
    else:
        return render_template('error.html', message="User not logged in!")

@app.route('/endroom', methods=["GET", "POST"])
def endroom():
    if nameCheck():
        if roomCheck():
            room = request.form.get('roomname')
            rpass = request.form.get('roompass')
            print(room+' '+rpass)
            if removeRoom(room, rpass):
                return redirect(url_for('initChat'))
            else:
                return render_template('error.html', message="Room not found!")
        else:
            return render_template('error.html', message="Room not found!")
    else:
        return render_template('error.html', message="User not logged in!")


@socketio.on('sendmsg')
def sendmsg(data):
    name = data['name']
    room = data['room']
    msg = data['msg']
    time = data['time']
    mess = msg+' '+time
    addMessage(room, mess)
    print('Add message -> ')
    print(chats)
    emit('loadmsg', {'room': room, 'name': name, 'mess': mess}, broadcast=True)

@socketio.on('delmsg')
def delmsg(data):
    print('initialized')
    mess = data['mess']
    room = data['room']
    if messDelete(room, mess):
        print(chats)
    else:
        print('Did not match!')
    emit('successmsg', {'msg': "Successful!"}, broadcast=True)