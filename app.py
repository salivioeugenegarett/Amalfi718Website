import requests
import os
import vonage
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from datetime import datetime, date, time
from sqlalchemy import Date, Time, and_, func
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from functools import wraps

load_dotenv('.env')

encryption_key = os.getenv('ENCRYPTION_KEY')
fernet = Fernet(encryption_key.encode())

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.LargeBinary, nullable=False) 
    email = db.Column(db.String, nullable=False) 
    password = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.LargeBinary, nullable=False) 
    address = db.Column(db.LargeBinary, nullable=False)
    datein = db.Column(Date, nullable=False)
    timein = db.Column(Time, nullable=False) 
    dateout = db.Column(Date, nullable=False)
    timeout = db.Column(Time, nullable=False)          
    room = db.Column(db.String(50))          
    guestadult = db.Column(db.Integer)        
    guestchild = db.Column(db.Integer)        
    request = db.Column(db.String(250))

    def decrypt_name(self):
        return fernet.decrypt(self.name).decode()

    def decrypt_phone(self):
        return fernet.decrypt(self.phone).decode()

    def decrypt_address(self):
        return fernet.decrypt(self.address).decode()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('You need to be logged in as an admin to access this page.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/standard-room')
def standard_room():
    return render_template('StandardRoom.html')

@app.route('/superior-room')
def superior_room():
    return render_template('SuperiorRoom.html')

@app.route('/deluxe-room')
def deluxe_room():
    return render_template('DeluxeRoom.html')

@app.route('/suite-room')
def suite_room():
    return render_template('SuiteRoom.html')

@app.route('/esuite-room')
def esuite_room():
    return render_template('ESuiteRoom.html')

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/reset-password')
def reset_password():
    return render_template('reset_password.html')


@app.route('/user-interface')
def user_interface():
    user_email = session.get('user_email')
        
    if user_email:
        bookings = User.query.filter_by(email=user_email).all()
        decrypted_bookings = []
        for booking in bookings:
            decrypted_bookings.append({
                'id': booking.id,
                'name': booking.decrypt_name(),
                'email': booking.email,
                'phone': booking.decrypt_phone(),
                'address': booking.decrypt_address(),
                'datein': booking.datein,
                'timein': booking.timein,
                'dateout': booking.dateout,
                'timeout': booking.timeout,
                'room': booking.room,
                'guestadult': booking.guestadult,
                'guestchild': booking.guestchild,
                'request': booking.request,
            })
    else:
        decrypted_bookings = []

    return render_template('userinterface.html', bookings=decrypted_bookings)

@app.route('/admin-login')
def admin_login():
    return render_template('adminlogin.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin_username = os.getenv('ADMIN_USERNAME')
        admin_password = os.getenv('ADMIN_PASSWORD')

        if username == admin_username and password == admin_password:
            session['admin_logged_in'] = True 
            return redirect(url_for('admin_page')) 
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin.html')

@app.route('/admin_page')  
@admin_required
def admin_page():
    users = User.query.all()

    decrypted_users = []
    for user in users:
        decrypted_users.append({
            'id': user.id,
            'name': user.decrypt_name(),
            'email': user.email,
            'phone': user.decrypt_phone(),
            'address': user.decrypt_address(),
            'datein': user.datein,
            'timein': user.timein,
            'dateout': user.dateout,
            'timeout': user.timeout,
            'room': user.room,
            'guestadult': user.guestadult,
            'guestchild': user.guestchild,
            'request': user.request,
        })

    return render_template('admin.html', users=decrypted_users)

@app.route('/add-booking', methods=['POST'])
def add_booking():

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']
    address = request.form['address']
    datein = request.form['datein']
    timein = request.form['timein']
    dateout = request.form['dateout']
    timeout = request.form['timeout']
    room = request.form['room']
    guestadult = request.form['guestadult']
    guestchild = request.form['guestchild']
    request_text = request.form['request']

    encrypted_name = fernet.encrypt(name.encode())
    encrypted_phone = fernet.encrypt(phone.encode())
    encrypted_address = fernet.encrypt(address.encode())

    new_user = User(
        name=encrypted_name, 
        email=email, 
        password=bcrypt.generate_password_hash(password).decode('utf-8'),
        phone=encrypted_phone, 
        address=encrypted_address,
        datein=date.fromisoformat(datein),
        timein=time.fromisoformat(timein),
        dateout=date.fromisoformat(dateout), 
        timeout=time.fromisoformat(timeout),
        room=room, 
        guestadult=int(guestadult), 
        guestchild=int(guestchild), 
        request=request_text
    )

    db.session.add(new_user)
    db.session.commit()
    
    flash('Booking added/updated successfully!', 'success')

    return redirect(url_for('admin_page'))

@app.route('/add-book', methods=['POST'])
def add_book():

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']
    address = request.form['address']
    datein = request.form['datein']
    timein = request.form['timein']
    dateout = request.form['dateout']
    timeout = request.form['timeout']
    room = request.form['room']
    guestadult = request.form['guestadult']
    guestchild = request.form['guestchild']

    encrypted_name = fernet.encrypt(name.encode())
    encrypted_phone = fernet.encrypt(phone.encode())
    encrypted_address = fernet.encrypt(address.encode())

    new_user = User(
        name=encrypted_name, 
        email=email, 
        password=bcrypt.generate_password_hash(password).decode('utf-8'),
        phone=encrypted_phone, 
        address=encrypted_address,
        datein=date.fromisoformat(datein),
        timein=time.fromisoformat(timein),
        dateout=date.fromisoformat(dateout), 
        timeout=time.fromisoformat(timeout),
        room=room, 
        guestadult=int(guestadult),
        guestchild=int(guestchild), 
    )

    db.session.add(new_user)
    db.session.commit()
    
    total_price_str = request.form.get('hidden_total_price', '0')
    print(f"Received total_price: {total_price_str}")

    flash('Booking added/updated successfully!', 'success')

    return

@app.route('/delete-booking/<int:id>', methods=['DELETE'])
@admin_required  
def delete_booking(id):
    booking = User.query.get(id)
    if booking:
        db.session.delete(booking)
        db.session.commit()
        return jsonify({'message': 'Booking deleted successfully!'}), 200
    return jsonify({'message': 'Booking not found!'}), 404

@app.route('/edit-booking/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_booking(id):
    booking = User.query.get(id)
    if request.method == 'GET':
        if booking:
            return render_template('edit_booking.html', booking=booking)
        else:
            flash('Booking not found.', 'danger')
            return redirect(url_for('admin_page'))

    if request.method == 'POST':
        booking.name = fernet.encrypt(request.form['name'].encode())
        booking.email = request.form['email']
        booking.phone = fernet.encrypt(request.form['phone'].encode())
        booking.address = fernet.encrypt(request.form['address'].encode())
        booking.datein = date.fromisoformat(request.form['datein'])
        booking.timein = time.fromisoformat(request.form['timein'])
        booking.dateout = date.fromisoformat(request.form['dateout'])
        booking.timeout = time.fromisoformat(request.form['timeout'])
        booking.room = request.form['room']
        booking.guestadult = request.form['guestadult']
        booking.guestchild = request.form['guestchild']
        booking.request = request.form['request']

        db.session.commit()
        flash('Booking updated successfully!', 'success')
        return redirect(url_for('admin_page'))

@app.route('/useredit-booking/<int:id>', methods=['GET', 'POST'])
def useredit_booking(id):
    booking = User.query.get(id)
    if request.method == 'GET':
        if booking:
            return render_template('edit_booking.html', booking=booking)
        else:
            flash('Booking not found.', 'danger')
            return redirect(url_for('user_interface'))

    if request.method == 'POST':
        booking.name = fernet.encrypt(request.form['name'].encode())
        booking.email = request.form['email']
        booking.phone = fernet.encrypt(request.form['phone'].encode())
        booking.address = fernet.encrypt(request.form['address'].encode())
        booking.datein = date.fromisoformat(request.form['datein'])
        booking.timein = time.fromisoformat(request.form['timein'])
        booking.dateout = date.fromisoformat(request.form['dateout'])
        booking.timeout = time.fromisoformat(request.form['timeout'])
        booking.room = request.form['room']
        booking.guestadult = request.form['guestadult']
        booking.guestchild = request.form['guestchild']
        booking.request = request.form['request']

        db.session.commit()
        flash('Booking updated successfully!', 'success')
        return redirect(url_for('user_interface'))


@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)  
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        session['user_email'] = email
        flash('Logged in successfully!', 'success')
        return redirect(url_for('user_interface'))
    else:
        flash('Invalid email or password.', 'danger')
        return redirect(url_for('index'))


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:
            token = user.generate_password_reset_token()
            reset_url = url_for('reset_password', token=token, _external=True)

            msg = Message('Password Reset Request', sender=os.getenv('MAIL_USERNAME'), recipients=[email])
            msg.body = f'Please click the link to reset your password: {reset_url}'
            mail.send(msg)

            flash('A password reset link has been sent to your email.', 'info')
        else:
            flash('This email is not registered.', 'danger')
        
        return redirect(url_for('index'))

    return render_template('forgot_password.html')


@app.route('/pay', methods=['GET', 'POST'])
def pay():

    name = request.form['name']
    email = request.form['email']
    password = request.form['password'] 
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    phone = request.form['phone']
    address = request.form['address']
    datein = request.form['datein']
    timein = request.form['timein']
    dateout = request.form['dateout']
    timeout = request.form['timeout']
    room = request.form['room']
    guestadult = request.form['guestadult']
    guestchild = request.form['guestchild']

    encrypted_name = fernet.encrypt(name.encode())
    encrypted_phone = fernet.encrypt(phone.encode())
    encrypted_address = fernet.encrypt(address.encode())

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email already exists! Booking will be updated.', 'warning')
        existing_user.name = encrypted_name
        existing_user.phone = encrypted_phone
        existing_user.address = encrypted_address
        existing_user.datein = date.fromisoformat(request.form['datein'])
        existing_user.timein = time.fromisoformat(request.form['timein'])
        existing_user.dateout = date.fromisoformat(request.form['dateout'])
        existing_user.timeout = time.fromisoformat(request.form['timeout'])
        existing_user.room = room
        existing_user.guestadult = int(guestadult)
        existing_user.guestchild = int(guestchild)
        
        db.session.commit()
    else:
        new_user = User(
            name=encrypted_name, 
            email=email, 
            password=hashed_password,
            phone=encrypted_phone, 
            address=encrypted_address,
            datein=date.fromisoformat(datein),
            timein=time.fromisoformat(timein),
            dateout=date.fromisoformat(dateout), 
            timeout=time.fromisoformat(timeout),
            room=room, 
            guestadult=int(guestadult),
            guestchild=int(guestchild), 
        )

        db.session.add(new_user)
        db.session.commit()
    
    total_price_str = request.form.get('hidden_total_price', '0')
    print(f"Received total_price: {total_price_str}")
    flash('Booking added/updated successfully!', 'success')

    if request.method == 'POST':
        print(request.form)
        total_price_str = request.form.get('hidden_total_price', '0')
        print(f"Received total_price: {total_price_str}")

        try:
            total_amount = int(total_price_str)
            print(f"Total amount as integer: {total_amount}")  
        except ValueError:
            total_amount = 0
            print("Failed to convert total_price to an integer, using total_amount = 0")

    if request.method == 'POST':
        client = vonage.Client(key="0275150b", secret="BqazgTkjKFGS5AIc")
        sms = vonage.Sms(client)
        
        responseData = sms.send_message(
            {
                "from": "Amalfi 718 Hotel",
                "to": "639673671662",
                "text": "Amalfi 718 Hotel\n\nHello " + name + ".\nYou successfully paid Php " + str(total_amount) + ".\n" + "Details:\nRoom Type: " + room + "Room\nCheck In: " + str(datein)+ "\nCheck Out: " + str(dateout) + "\n\nThankyou for using InstaReserve.\n",
            }
        )

        if responseData["messages"][0]["status"] == "0":
            print("Message sent successfully.")
        else:
            print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
            
        url = "https://api.paymongo.com/v1/links"
        headers = {
            "accept": "application/json",
            "authorization": "Basic c2tfdGVzdF9pQWdIbWRaMmZSaDVTTnppOVJvY1ZjS0U6",
            "content-type": "application/json"
        }        

        payload = {
            "data": {
                "attributes": {
                    "amount": total_amount*100,
                    "description": "Amalfi 718 Hotel",
                    "remarks": "Thank you for Booking!"
                }
            }
        }

        print(f"Pay: {total_price_str}")

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            checkout_url = data['data']['attributes']['checkout_url']
            return redirect(checkout_url)
        else:
            return f"Failed to create payment link: {response.text}", response.status_code
        
@app.route('/backup')
def backup():
    database_file = 'users.db'
    if os.path.exists(database_file):
        return send_file(database_file, as_attachment=True)
    return abort(404)


def check_room_availability(room, datein, dateout):
    # Convert date strings to datetime objects
    date_in = datetime.strptime(datein, '%Y-%m-%d')
    date_out = datetime.strptime(dateout, '%Y-%m-%d')

    # Query the database to check if the room is available
    reservations = User.query.filter(
        User.room == room,  # Use 'room' variable instead of 'room_type'
        and_(
            User.datein < date_out,  # Check if the current booking ends before the new booking starts
            User.dateout > date_in   # Check if the current booking starts after the new booking ends
        )
    ).all()

    # If any reservations exist for this room in the date range, it's unavailable
    return len(reservations) == 0  # Return True if no reservations, else False

@app.route('/check-availability')
def check_availability():
    room = request.args.get('room')  # The room type or identifier
    datein = request.args.get('datein')  # Check-in date
    dateout = request.args.get('dateout')  # Check-out date

    # Perform the logic to check if the room is available for the given dates
    available = check_room_availability(room, datein, dateout)

    return jsonify({'available': available})



if __name__ == '__main__':
    with app.app_context():
        db_path = 'users.db' 
        if not os.path.exists(db_path):
            print("Creating database...")
            db.create_all()
            print("Database created!")
        else:
            print("Database already exists.")
        
        absolute_path = os.path.abspath(db_path)
        print(f"Database file location: {absolute_path}")

    app.run(debug=True)