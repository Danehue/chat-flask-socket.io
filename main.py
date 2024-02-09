from flask import Flask, render_template
from flask_socketio import SocketIO, send
from flask_socketio import join_room, leave_room, rooms

# Supabase
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

items = []

# **********************************
# *********** CONECTION ************
# **********************************
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def test_connect():
    print('my response', {'data': 'Connected'})
    # recover messages from db
    response = supabase.table('messages').select("*").execute()
    if len(response.data) > 0:
        for item in response.data:
            items.append(item)
            send(item['msg'])

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


# **********************************
# ******* RECEIVING MESSAGES *******
# **********************************    
@socketio.on('message')
def handle_msg(data):
    room = data['room']
    msg = data['data']
    send(msg, to=room)
    data, count = supabase.table('messages').insert({"msg": msg}).execute()
    
@socketio.on('my event')
def handle_json(json):
    print('received json: ' + str(json))


# **********************************
# ************ ROOMS ***************
# **********************************
@socketio.on('first_join')
def on_join(data):
    room = data['room']
    join_room(room)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ': online.', to=room)
    
    connected_users = rooms()
    print(f'Usuarios conectados en la sala {room}: {connected_users}')

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left ' + room, to=room)
    # join_room('general')


# **********************************
# ************* RUN ****************
# **********************************
if __name__ == '__main__':
    socketio.run(app)