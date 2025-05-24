from flask import Flask, render_template, request, redirect, url_for, flash
from fund_manager import FundManager
import os

app = Flask(__name__)
app.secret_key = "secret123"  # Needed for flashing messages

# Initialize fund manager
fm = FundManager()

@app.route('/')
def home():
    return render_template('home.html', members=fm.members, payments=fm.payments, expenses=fm.expenses,
                           collected=fm.total_collected(), spent=fm.total_spent(),
                           balance=fm.total_collected() - fm.total_spent())

@app.route('/add_member', methods=['POST'])
def add_member():
    name = request.form['name'].strip()
    contact = request.form['contact'].strip()
    if name and contact:
        if fm.add_member(name, contact):
            flash("Member added successfully.", "success")
        else:
            flash("Member already exists.", "warning")
        fm.save_data()
    return redirect(url_for('home'))

@app.route('/record_payment', methods=['POST'])
def record_payment():
    name = request.form['name'].strip()
    ptype = request.form['payment_type']
    if fm.record_payment(name, ptype):
        flash("Payment recorded.", "success")
    else:
        flash("Member not found.", "danger")
    fm.save_data()
    return redirect(url_for('home'))

@app.route('/record_expense', methods=['POST'])
def record_expense():
    try:
        amount = float(request.form['amount'])
        reason = request.form['reason'].strip()
        fm.record_expense(amount, reason)
        flash("Expense recorded.", "success")
        fm.save_data()
    except ValueError:
        flash("Invalid amount.", "danger")
    return redirect(url_for('home'))

@app.route('/unpaid')
def unpaid():
    ym = request.args.get('ym', '')
    ptype = request.args.get('ptype', '')
    if len(ym) == 7 and ptype in ['monthly', 'festival']:
        unpaid_members = fm.get_unpaid_members(ym, ptype)
        return render_template('unpaid.html', ym=ym, ptype=ptype, unpaid_members=unpaid_members)
    flash("Invalid input.", "danger")
    return redirect(url_for('home'))

@app.route('/export')
def export():
    ym = request.args.get('ym', '')
    if len(ym) == 7:
        filename = fm.export_month_report(ym)
        flash(f"Report exported to {filename}", "info")
    else:
        flash("Invalid year-month format.", "danger")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
