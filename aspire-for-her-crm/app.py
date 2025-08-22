from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'aspire_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ===================== MODELS =====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='Staff')

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50))
    program = db.Column(db.String(100))

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))  # Corporate / NGO / Govt
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    role = db.Column(db.String(50))  # Sponsor / Partner / Hiring Partner
    status = db.Column(db.String(20))  # Active / Inactive
    contribution = db.Column(db.String(200))  # Money / Venue / Mentorship
    notes = db.Column(db.Text)


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    status = db.Column(db.String(20))  # Pending / Active / Completed

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    assigned_to = db.Column(db.String(50))
    status = db.Column(db.String(20))  # Pending / In Progress / Done

# ===================== ROUTES =====================
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    # KPIs
    total_contacts = Contact.query.count()
    total_programs = Program.query.count()
    total_tasks = Task.query.count()
    total_companies = Company.query.count()

    # Data for charts
    program_status = {}
    for p in Program.query.all():
        program_status[p.status] = program_status.get(p.status, 0) + 1

    task_status = {}
    for t in Task.query.all():
        task_status[t.status] = task_status.get(t.status, 0) + 1


    return render_template('dashboard.html', 
                           total_contacts=total_contacts,
                           total_programs=total_programs,
                           total_tasks=total_tasks,
                           total_companies=total_companies,
                           program_status=program_status,
                           task_status=task_status)

# ===================== CRUD PAGES =====================
@app.route('/contacts')
def contacts():
    if 'user' not in session:
        return redirect(url_for('login'))
    all_contacts = Contact.query.all()
    return render_template('contacts.html', contacts=all_contacts)

@app.route('/contacts/add', methods=['POST'])
def add_contact():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    role = request.form['role']
    program = request.form['program']
    new_contact = Contact(name=name, email=email, phone=phone, role=role, program=program)
    db.session.add(new_contact)
    db.session.commit()
    flash("Contact added!", "success")
    return redirect(url_for('contacts'))
@app.route('/contacts/delete/<int:id>', methods=['POST'])

def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash("Contact deleted!", "danger")
    return redirect(url_for('contacts'))



@app.route('/companies')
def companies():
    if 'user' not in session:
        return redirect(url_for('login'))
    all_companies = Company.query.all()
    return render_template('companies.html', companies=all_companies)


@app.route('/companies/add', methods=['POST'])
def add_company():
    new_company = Company(
        name=request.form['name'],
        type=request.form['type'],
        contact_person=request.form['contact_person'],
        email=request.form['email'],
        phone=request.form['phone'],
        location=request.form['location'],
        role=request.form['role'],
        status=request.form['status'],
        contribution=request.form['contribution'],
        notes=request.form['notes']
    )
    db.session.add(new_company)
    db.session.commit()
    flash("Company added!", "success")
    return redirect(url_for('companies'))


@app.route('/companies/delete/<int:id>')
def delete_company(id):
    company = Company.query.get_or_404(id)
    db.session.delete(company)
    db.session.commit()
    flash("Company deleted!", "danger")
    return redirect(url_for('companies'))


@app.route('/programs')
def programs():
    if 'user' not in session:
        return redirect(url_for('login'))
    all_programs = Program.query.all()
    return render_template('programs.html', programs=all_programs)
@app.route('/programs/add', methods=['POST'])
def add_program():
    name = request.form['name']
    status = request.form['status']
    new_program = Program(name=name, status=status)
    db.session.add(new_program)
    db.session.commit()
    flash("Program added!", "success")
    return redirect(url_for('programs'))

@app.route('/programs/delete/<int:id>', methods=['POST'])
def delete_program(id):
    program = Program.query.get_or_404(id)
    db.session.delete(program)
    db.session.commit()
    flash("Program deleted!", "danger")
    return redirect(url_for('programs'))


@app.route('/tasks')
def tasks():
    if 'user' not in session:
        return redirect(url_for('login'))
    all_tasks = Task.query.all()
    return render_template('tasks.html', tasks=all_tasks)
@app.route('/tasks/add', methods=['POST'])
def add_task():
    title = request.form['title']
    assigned_to = request.form['assigned_to']
    status = request.form['status']
    new_task = Task(title=title, assigned_to=assigned_to, status=status)
    db.session.add(new_task)
    db.session.commit()
    flash("Task added!", "success")
    return redirect(url_for('tasks'))

@app.route('/tasks/delete/<int:id>', methods=['POST'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted!", "danger")
    return redirect(url_for('tasks'))


# ===================== SEED DATA =====================
def seed_data():
    if not User.query.first():
        demo_user = User(username='admin', password='admin', role='Admin')
        db.session.add(demo_user)

    if not Contact.query.first():
        demo_contacts = [
            Contact(name='Alice Johnson', email='alice@example.com', phone='1234567890', role='Mentee', program='Mentorship 2025'),
            Contact(name='Priya Singh', email='priya@example.com', phone='9876543210', role='Mentor', program='Mentorship 2025')
        ]
        db.session.add_all(demo_contacts)

    if not Company.query.first():
        demo_companies = [
            Company(name='WomenTech Partners', type='NGO'),
            Company(name='Aspire Corp', type='Corporate')
        ]
        db.session.add_all(demo_companies)

    if not Program.query.first():
        demo_programs = [
            Program(name='Mentorship 2025', status='Active'),
            Program(name='Skill Workshop', status='Pending')
        ]
        db.session.add_all(demo_programs)

    if not Task.query.first():
        demo_tasks = [
            Task(title='Follow-up with Alice', assigned_to='Priya Singh', status='Pending'),
            Task(title='Prepare Workshop Material', assigned_to='Admin', status='In Progress')
        ]
        db.session.add_all(demo_tasks)

    db.session.commit()

# ===================== APP START =====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, host='0.0.0.0')
