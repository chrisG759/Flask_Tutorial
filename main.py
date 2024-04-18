from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
conn_str = "mysql://root:sister@localhost/boatdb"
engine = create_engine(conn_str, echo=True)

# Define Boat model
metadata = MetaData()
boats = Table('boats', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('type', String(20)),
    Column('21', Integer),
    Column('111_136', Float)
)

# Handle boat deletion
@app.route('/delete/<int:boat_id>', methods=['POST'])
def delete_boat(boat_id):
    try:
        conn = engine.connect()
        conn.execute(
            text("DELETE FROM boats WHERE id = :id"),
            {'id': boat_id}
        )
        conn.close()
        return redirect(url_for('index'))
    except Exception as e:
        error = e.orig.args[1]
        return render_template('search.html', error=error, success=None)

# Handle boat update
@app.route('/update/<int:boat_id>', methods=['POST'])
def update_boat(boat_id):
    try:
        name = request.form['name']
        type = request.form['type']
        owner_id = request.form['owner_id']
        price = request.form['price']

        conn = engine.connect()
        conn.execute(
            text("UPDATE boats SET name=:name, type=:type, 21=:owner_id, 111_136=:price WHERE id=:id"),
            {'name': name, 'type': type, 'owner_id': owner_id, 'price': price, 'id': boat_id}
        )
        conn.close()
        return redirect(url_for('index'))
    except Exception as e:
        error = e.orig.args[1]
        return render_template('search.html', error=error, success=None)

# Create a session
Session = sessionmaker(bind=engine)

# Render index.html
@app.route('/')
def index():
    return render_template('index.html')

# Render user.html
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

# Handle search requests
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        boat_id = request.form['boat_id']
        conn = engine.connect()
        result = conn.execute(text("SELECT * FROM boats WHERE id = :id"), {'id': boat_id})
        boat = result.fetchone()
        conn.close()

        if boat:
            print("Boat found:", boat)  # Print debug information
            return render_template('search.html', boat=boat)  # Pass the boat object to the template
        else:
            print("Boat not found for ID:", boat_id)  # Print debug information
            return render_template('search.html', error="Boat ID not found")

    return render_template('search.html')

# Handle requests to get boats
@app.route('/boats/')
@app.route('/boats/<page>')
def get_boats(page=1):
    page = int(page)
    per_page = 10
    conn = engine.connect()
    boats = conn.execute(text(f"SELECT * FROM boats LIMIT {per_page} OFFSET {(page - 1) * per_page}")).all()
    conn.close()
    return render_template('boats.html', boats=boats, page=page, per_page=per_page)

# Render form to create a boat
@app.route('/create', methods=['GET'])
def create_get_request():
    return render_template('boats_create.html')

# Handle boat creation form submission
@app.route('/create', methods=['POST'])
def create_boat():
    try:
        conn = engine.connect()
        conn.execute(
            text("INSERT INTO boats (name, ...) VALUES (:name, ...)"),
            request.form
        )
        conn.close()
        return render_template('boats_create.html', error=None, success="Data inserted successfully!")
    except Exception as e:
        error = e.orig.args[1]
        return render_template('boats_create.html', error=error, success=None)

if __name__ == '__main__':
    app.run(debug=True)
