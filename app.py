from flask import Flask, render_template, request, url_for, make_response, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from sqlalchemy import func

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


CATEGORIES = ["Food", "Transport", "Events", "Other"]



def parse_date_or_none(s: str):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None



@app.route("/")
def index():

    # reading the query strings
    start_str = (request.args.get("start") or "").strip()
    end_str = (request.args.get("end") or "").strip()
    selected_category = (request.args.get("category") or "").strip()


    # parsing 
    start_date = parse_date_or_none(start_str)
    end_date = parse_date_or_none(end_str)

    if start_date and end_date and end_date < start_date:
        flash("End Date cannot be before Start Date", "error")
        start_date = end_date = None
        start_str = end_str = ""

    q = Expense.query
    if start_date:
        q = q.filter(Expense.date >= start_date)
    if end_date:
        q = q.filter(Expense.date <= end_date)    

    if selected_category:
        q = q.filter(Expense.category == selected_category)



    expenses = q.order_by(Expense.date.desc(), Expense.id.desc()).all()
    total = round(sum(e.amount for e in expenses), 2)


    #pie chart
    cat_q = db.session.query(Expense.category, func.sum(Expense.amount))

    if start_date:
        cat_q = cat_q.filter(Expense.date >= start_date)

    if end_date:
        cat_q = cat_q.filter(Expense.date <= end_date)

    if selected_category:
        cat_q = cat_q.filter(Expense.category == selected_category)

    cat_rows = cat_q.group_by(Expense.category).all()
    cat_labels = [c for c, _ in cat_rows]
    cat_values = [round(float(s or 0), 2) for _, s in cat_rows]





    #day chart
    day_q = db.session.query(Expense.date, func.sum(Expense.amount))
    print(day_q)
    if start_date:
        day_q = day_q.filter(Expense.date >= start_date)

    if end_date:
        day_q = day_q.filter(Expense.date <= end_date)

    if selected_category:
        day_q = day_q.filter(Expense.category == selected_category)

    day_rows = day_q.group_by(Expense.category).order_by(Expense.date).all()
    print(day_rows)    
    day_labels = [d.isoformat() for d, _ in day_rows]
    print(day_labels)
    day_values = [round(float(s or 0), 2) for _, s in day_rows]
    print(day_values)
    


    return render_template(

        "index.html",

        expenses=expenses,
        categories=CATEGORIES,
        today=date.today().isoformat(),
        total=total,
        start_str=start_str,
        end_str=end_str,
        selected_category=selected_category,
        cat_labels=cat_labels,
        cat_values=cat_values,
        day_labels=day_labels,
        day_values=day_values

        )



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



@app.route("/delete/<int:expense_id>" ,methods=['POST'])
def delete(expense_id):
    e = Expense.query.get_or_404(expense_id)
    db.session.delete(e)
    db.session.commit()
    flash("Expense deleted", "success")
    return redirect(url_for("index"))




if __name__ == "__main__":
    app.run(debug=True)

