import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import func
import os
from flask import render_template
from datetime import datetime


from flask_sqlalchemy import SQLAlchemy
from flask_admin.base import BaseView, expose


app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'




basedir = os.path.abspath(os.path.dirname(__file__))


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'user_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['SQLALCHEMY_POOL_SIZE'] = 20  
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30  


conn = sqlite3.connect('user_data.db')
c = conn.cursor()

# This automaticly creates a table in the database 
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (id INTEGER PRIMARY KEY, 
             first_name TEXT, 
             surname TEXT, 
             email TEXT,
             username TEXT,
             
             password TEXT)''')



c.execute('''CREATE TABLE IF NOT EXISTS tickets 
             (id INTEGER PRIMARY KEY,
             user_id INTEGER,
             adults INTEGER,
             children INTEGER,
             total_price REAL,
             FOREIGN KEY(user_id) REFERENCES users(id))''')



c.execute('''CREATE TABLE IF NOT EXISTS hotel_purchases 
             (id INTEGER PRIMARY KEY,
             user_id INTEGER,
             name TEXT,
             email TEXT,
             phone TEXT,
             credit_card TEXT,
             pin_code TEXT,
             expiry TEXT,
             FOREIGN KEY(user_id) REFERENCES users(id))''')

c.execute('''CREATE TABLE IF NOT EXISTS user_details 
             (id INTEGER PRIMARY KEY,
             user_id INTEGER,
             full_name TEXT,
             email TEXT,
             FOREIGN KEY(user_id) REFERENCES users(id))''')

c.execute('''CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY,
                room_type TEXT,
                num_guests INTEGER,
                full_name TEXT,
                email TEXT,
                booking_date DATE 
             )''')





conn.commit()
conn.close()

db = SQLAlchemy(app)
admin = Admin(app)

# This retrives to view email in flask admin
class EmailView(BaseView):
    @expose('/')
    def index(self):
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute("SELECT email FROM users")
        emails = [row[0] for row in c.fetchall()]
        conn.close()
        return self.render('admin/emails.html', emails=emails)

admin.add_view(EmailView(name='Emails', endpoint='emails'))

# This retrives to view totaltickets in flask admin
class TotalTicketsView(BaseView):
    @expose('/')
    def index(self):
        
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()

        
        c.execute("SELECT adults, children FROM tickets")
        tickets_data = c.fetchall()

        
        conn.close()

        
        total_tickets = sum(adults + children for adults, children in tickets_data)

        
        total_sales = sum((adults + children) * 20 for adults, children in tickets_data)  
        total_sales += sum((adults + children) * 10 for adults, children in tickets_data)  

        
        return self.render('admin/total_tickets.html', total_tickets=total_tickets, total_sales=total_sales)


admin.add_view(TotalTicketsView(name='Total Tickets', endpoint='total_tickets')) 




# This retrives to view booking data in flask admin
class BookingView(BaseView):
    @expose('/')
    def index(self):
        
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()

    
        c.execute("SELECT room_type, num_guests, email FROM bookings")
        data = c.fetchall()

    
        conn.close()

        
        return render_template('admin/bookings.html', data=data)


admin.add_view(BookingView(name='Bookings', endpoint='bookings'))




UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




@app.route('/')
def index():
    return render_template('home.html')

# Gets data from the register and post it in the table 
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstName']
        surname = request.form['surname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        try:
            conn = sqlite3.connect('user_data.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (first_name, surname, email, username, password) VALUES (?, ?, ?, ?, ?)",
                (first_name, surname, email, username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            session.rollback()
        else:
            conn.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')




#Gets data from the login and post it in the table
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        if user and user[5] == password:
            session['user_id'] = user[0]
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template('login.html')

# automatically goes to the home page 
@app.route('/home')
def home():
    
    if 'user_id' in session:
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        user_id = session['user_id']
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = c.fetchone()
        conn.close()

        if user:
            return render_template('home.html', user=user)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    
    
    
#Routes the user to the purchase tickets and renders the page
@app.route('/purchaseticket.html')
def purchaseticket():
    return render_template('purchaseticket.html')


@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/login.html')
def login1():
    return render_template('login.html')

@app.route('/purchasehotel.html')
def hotel():
    return render_template('purchasehotel.html')


@app.route('/home.html')
def home1():
    return render_template('home.html')

@app.route('/hotel.html')
def hotel1():
    return render_template('hotel.html')

@app.route('/register.html')
def register1():
    return render_template('register.html')

@app.route('/education.html')
def education1():
    return render_template('education.html')

@app.route('/attraction.html')
def attraction1():
    return render_template('attraction.html')

@app.route('/Policy.html')
def Policy():
    return render_template('Policy.html')




# post request
@app.route('/process_booking', methods=['POST'])
def process_booking():
    if request.method == 'POST':
        
        adults_tickets = int(request.form['adults'])
        children_tickets = int(request.form['children'])
        is_member = 'member' in request.form 

        
        total_price = (adults_tickets * 20) + (children_tickets * 10)

        
        if is_member:
            total_price *= 0.9  

        
        user_id = session.get('user_id')

        try:
            
            conn = sqlite3.connect('user_data.db')
            c = conn.cursor()

    
            c.execute("INSERT INTO tickets (user_id, adults, children, total_price) VALUES (?, ?, ?, ?)",
                      (user_id, adults_tickets, children_tickets, total_price))

            
            conn.commit()
            conn.close()

            
            return f"Booking processed successfully. Total Price: ${total_price}"
        except Exception as e:
        
            
            conn.rollback()
            conn.close()
            
            return str(e)

        


#Post request sending room type etc
@app.route('/book_room', methods=['POST'])
def book_room():
    if request.method == 'POST':
        room_type = request.form['roomType']
        num_guests = request.form['numGuests']
        full_name = request.form['fullName']
        email = request.form['email']
        booking_date = request.form['bookingDate'] 

        
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM bookings WHERE booking_date = ?", (booking_date,))
        count = c.fetchone()[0]
        conn.close()

        
        if count > 0:
            return "Sorry, this date is already booked. Please select another date."

        
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute("INSERT INTO bookings (room_type, num_guests, full_name, email, booking_date) VALUES (?, ?, ?, ?, ?)",
                  (room_type, num_guests, full_name, email, booking_date))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))


if __name__ == "__main__":
    #Creates the table base on one model
    with app.app_context():
     db.create_all()
    app.run(debug=True)
   
    
   
