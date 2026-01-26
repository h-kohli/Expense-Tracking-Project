from flask import Flask, render_template, request, url_for, make_response, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

app = Flask(__name__) #instance

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my-secret-key'
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)



#creates data base
with app.app_context():
    db.create_all()





@app.route("/")
def index():

    expenses = Expense.query.order_by(Expense.date.desc(), Expense.id.desc()).all()
    return render_template("index.html", expenses=expenses)



@app.route("/add", methods=['POST'])
def add():

    description = (request.form.get("description") or "").strip()
    amount_str = (request.form.get("amount") or "").strip()
    category = (request.form.get("category") or "").strip()
    date_str = (request.form.get("date") or "").strip()

    #ensures description, amount and category are listed.
    if not description or not amount_str or not category:
        flash("Please fill desciption, amount, and category", "error")
        return redirect(url_for("index"))

    #converts the amount input string into an actual number
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError

    except ValueError:
        flash("Amount must be a positive number", "error")
        return redirect(url_for("index"))
    

    #converts the date into storable format
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()

    except ValueError:
        d = date.today()


    #saving to the database
    e = Expense(description=description, amount=amount, category=category, date=d)
    db.session.add(e)
    db.session.commit()

    flash("Expense added", "success")
    return redirect(url_for("index"))




    print("Form received:", dict(request.form))
    return make_response("Form received check the console")

if __name__ == "__main__":
    app.run(debug=True)

