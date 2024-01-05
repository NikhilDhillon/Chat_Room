from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
import string

app = Flask(__name__)
app.config["SECRET_KEY"] = "KBSKJBSS"
socketio = SocketIO(app)

rooms = {}

def generate_unique_code(length):
    while True:
         code = "".join(random.choice(string.ascii_uppercase) for _ in range(length))
         
         if code not in rooms:
            break
    
    return code

@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        
        if not name:
          return render_template("home.html", error="Please enter a name!", code=code, name=name)
                  
        if not code:
          code = generate_unique_code(4)
        room = code
        if join != False:
            rooms[room] = {"members": 0, "messages": []}
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] < 0:
          del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    socketio.run(app, debug=True)




# from flask import Flask, render_template, request, session, redirect, url_for
# from flask_socketio import join_room, leave_room, send, SocketIO
# from flask_sqlalchemy import SQLAlchemy
# import random
# import string
# from datetime import datetime

# app = Flask(__name__)
# app.config["SECRET_KEY"] = "hjhjsdahhds"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# socketio = SocketIO(app)
# db = SQLAlchemy(app)

# class Room(db.Model):
#     id = db.Column(db.String(4), primary_key=True)
#     members = db.Column(db.Integer, default=0)
#     messages = db.relationship("Message", backref="room", lazy="dynamic")

# class Message(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(200))
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
#     room_id = db.Column(db.String(4), db.ForeignKey("room.id"))
#     name = db.Column(db.String(50))

# def generate_unique_code(length):
#     while True:
#         code = "".join(random.choice(string.ascii_uppercase) for _ in range(length))
#         existing_room = Room.query.filter_by(id=code).first()
#         if not existing_room:
#             break
#         else:
#             print(f"Code {code} already exists in the database. Trying a new one.")
#     return code

# # Use app.app_context() here for database operations outside of the route
# with app.app_context():
#     db.drop_all()
#     db.create_all()

# @app.route("/", methods=["POST", "GET"])
# def home():
#     session.clear()
#     if request.method == "POST":
#         name = request.form.get("name")
#         code = request.form.get("code")
#         join = request.form.get("join", False)
        
#         if not name:
#             return render_template("home.html", error="Please enter a name.", code=code, name=name)
                  
#         if not code:
#             code = generate_unique_code(4)
#             room = Room(id=code, members=0)
#             db.session.add(room)
#             db.session.commit()
#         elif join != False:
#             existing_room = Room.query.filter_by(id=code).first()
#             if not existing_room:
#                 return render_template("home.html", error="Invalid room code.", code=code, name=name)

#         session["room"] = code
#         session["name"] = name
#         return redirect(url_for("room"))

#     return render_template("home.html")

# @app.route("/room")
# def room():
#     room_code = session.get("room")
#     name = session.get("name")
#     if room_code is None or name is None:
#         return redirect(url_for("home"))

#     room = Room.query.get(room_code)
#     messages = room.messages.order_by(Message.id).all()

#     return render_template("room.html", code=room_code, messages=messages)

# @socketio.on("message")
# def message(data):
#     room_code = session.get("room")
#     if room_code is None:
#         return 
    
#     room = Room.query.get(room_code)

#     name = session.get("name")
    
#     content = Message(content=data["data"])
#     room.messages.append(content)

#     db.session.add(content)
#     db.session.commit()

#     send({"name": name, "message": data["data"], "timestamp": content.timestamp.strftime("%Y-%m-%d %H:%M:%S")}, to=room_code)
#     print(f"{session.get('name')} said: {data['data']}")

# @socketio.on("connect")
# def connect(auth):
#     room_code = session.get("room")
#     name = session.get("name")
#     if not room_code or not name:
#         return

#     room = Room.query.get(room_code)
#     if room is None:
#         leave_room(room_code)
#         return
    
#     join_room(room_code)
#     send({"name": name, "message": "has entered the room"}, to=room_code)
#     room.members += 1
#     db.session.commit()
#     print(f"{name} joined room {room_code}")

# @socketio.on("disconnect")
# def disconnect():
#     room_code = session.get("room")
#     name = session.get("name")
#     leave_room(room_code)

#     room = Room.query.get(room_code)
#     if room:
#         room.members -= 1
#         if room.members < 0:
#             with app.app_context():
#                 db.session.delete(room)
#         else:
#             db.session.commit()
    
#     send({"name": name, "message": "has left the room"}, to=room_code)
#     print(f"{name} has left the room {room_code}")

# if __name__ == "__main__":
#     socketio.run(app, debug=True)