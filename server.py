from flask import Flask, render_template, request  # Добавляем импорт request
from flask_socketio import SocketIO, emit, join_room
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Простое хранилище комнат: {room_id: [socket_id1, socket_id2]}
rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 200

@socketio.on('create_room')
def handle_create_room():
    room_id = str(uuid.uuid4())[:8]
    rooms[room_id] = [request.sid]  # Теперь request импортирован
    join_room(room_id)
    emit('room_created', {'room_id': room_id, 'your_id': request.sid})
    print(f"Room created: {room_id} by {request.sid}")

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data.get('room_id')
    if not room_id or room_id not in rooms:
        emit('error', {'message': 'Invalid room ID'})
        return
    
    # Добавляем участника в комнату
    rooms[room_id].append(request.sid)
    join_room(room_id)
    
    # Отправляем новому участнику список ВСЕХ участников комнаты
    emit('joined_room', {
        'room_id': room_id,
        'your_id': request.sid,
        'all_participants': rooms[room_id]
    })
    
    # Уведомляем остальных участников о новичке
    emit('new_participant', {
        'socket_id': request.sid
    }, room=room_id, include_self=False)
    
    print(f"User {request.sid} joined room {room_id}")

@socketio.on('webrtc_offer')
def handle_webrtc_offer(data):
    # Пересылаем offer целевому участнику
    target_id = data.get('target_id')
    if not target_id:
        return
    
    emit('webrtc_offer', {
        'sender_id': request.sid,
        'offer': data['offer']
    }, room=target_id)

@socketio.on('webrtc_answer')
def handle_webrtc_answer(data):
    # Пересылаем answer целевому участнику
    target_id = data.get('target_id')
    if not target_id:
        return
    
    emit('webrtc_answer', {
        'sender_id': request.sid,
        'answer': data['answer']
    }, room=target_id)

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    # Пересылаем ICE кандидат целевому участнику
    target_id = data.get('target_id')
    if not target_id:
        return
    
    emit('ice_candidate', {
        'sender_id': request.sid,
        'candidate': data['candidate']
    }, room=target_id)

@socketio.on('disconnect')
def handle_disconnect():
    # Удаляем участника из всех комнат
    for room_id, participants in list(rooms.items()):
        if request.sid in participants:
            participants.remove(request.sid)
            
            # Если комната пуста - удаляем
            if not participants:
                del rooms[room_id]
            
            # Уведомляем остальных участников
            emit('participant_left', {
                'socket_id': request.sid
            }, room=room_id)
            break

app.run(host='0.0.0.0', 
        port=8080, )  # HTTPS!