from flask import Flask, render_template, request
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
conn_str = "mysql://root:sister@localhost/boatdb"
engine = create_engine(conn_str, echo=True)

# Define Boat model
metadata = MetaData()
boats = Table('boats', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    # Define other columns as needed
)

# Create a session
Session = sessionmaker(bind=engine)

# Render index.html
@app.route('/')
def index():
    return render_template('index.html')

# Render user.html with name parameter
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
            boat_name = boat[1]  # Assuming the 'name' column is the second column in the query result
            return render_template('search.html', boat_id=boat_id, boat_name=boat_name)
        else:
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
