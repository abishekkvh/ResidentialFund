import json
from datetime import datetime

class Person:
    def __init__(self, name, contact):
        self.name = name
        self.contact = contact

class Member(Person):
    def __init__(self, name, contact):
        super().__init__(name, contact)

class Payment:
    def __init__(self, member_name, amount, payment_type, date=None):
        self.member_name = member_name
        self.amount = amount
        self.payment_type = payment_type
        self.date = date or datetime.now().strftime("%Y-%m-%d")

class Expense:
    def __init__(self, amount, reason, date=None):
        self.amount = amount
        self.reason = reason
        self.date = date or datetime.now().strftime("%Y-%m-%d")

class FundManager:
    def __init__(self, filename="fund_data.json"):
        self.filename = filename
        self.members = []
        self.payments = []
        self.expenses = []
        self.load_data()

    def load_data(self):
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                self.members = [Member(**m) for m in data.get("members", [])]
                self.payments = [Payment(**p) for p in data.get("payments", [])]
                self.expenses = [Expense(**e) for e in data.get("expenses", [])]
        except (FileNotFoundError, json.JSONDecodeError):
            self.members = []
            self.payments = []
            self.expenses = []

    def save_data(self):
        data = {
            "members": [vars(m) for m in self.members],
            "payments": [vars(p) for p in self.payments],
            "expenses": [vars(e) for e in self.expenses]
        }
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=2)

    def add_member(self, name, contact):
        if any(m.name.lower() == name.lower() for m in self.members):
            return False, "Member already exists!"
        self.members.append(Member(name, contact))
        self.save_data()
        return True, f"Member '{name}' added."

    def find_member(self, name):
        for m in self.members:
            if m.name.lower() == name.lower():
                return m
        return None

    def record_payment(self, member_name, payment_type):
        member = self.find_member(member_name)
        if not member:
            return False, "Member not found!"
        amount = 100 if payment_type == 'monthly' else 1000
        self.payments.append(Payment(member.name, amount, payment_type))
        self.save_data()
        return True, f"Payment of ₹{amount} recorded for {member.name} as {payment_type}."

    def record_expense(self, amount, reason):
        try:
            amount = float(amount)
        except ValueError:
            return False, "Invalid amount."
        self.expenses.append(Expense(amount, reason))
        self.save_data()
        return True, f"Expense of ₹{amount} recorded for: {reason}"

    def total_collected(self):
        return sum(p.amount for p in self.payments)

    def total_spent(self):
        return sum(e.amount for e in self.expenses)

    def get_summary(self):
        collected = self.total_collected()
        spent = self.total_spent()
        return {
            "collected": collected,
            "spent": spent,
            "balance": collected - spent
        }

    def get_data(self):
        return {
            "members": self.members,
            "payments": self.payments,
            "expenses": self.expenses
        }

    def get_unpaid_members(self, ym, ptype):
        if not self.validate_ym(ym):
            return False, "Invalid date format. Use YYYY-MM", []

        if ptype not in ["monthly", "festival"]:
            return False, "Invalid payment type.", []

        paid_names = {
            p.member_name.lower()
            for p in self.payments
            if p.payment_type == ptype and p.date.startswith(ym)
        }
        unpaid = [m.name for m in self.members if m.name.lower() not in paid_names]
        return True, "Success", unpaid

    def export_month_report(self, ym):
        if not self.validate_ym(ym):
            return False, "Invalid format"

        filename = f"Neighbourhood_Report_{ym.replace('-', '')}.txt"
        with open(filename, "w") as f:
            f.write(f"{'='*60}\nNEIGHBOURHOOD REPORT - {ym}\n{'='*60}\n\n")
            f.write("Members:\n")
            for m in self.members:
                f.write(f"- {m.name} ({m.contact})\n")

            f.write("\nPayments:\n")
            for p in self.payments:
                if p.date.startswith(ym):
                    f.write(f"- {p.date}: {p.member_name} paid ₹{p.amount} ({p.payment_type})\n")

            f.write("\nExpenses:\n")
            for e in self.expenses:
                if e.date.startswith(ym):
                    f.write(f"- {e.date}: ₹{e.amount} for {e.reason}\n")

            total_collected = sum(p.amount for p in self.payments if p.date.startswith(ym))
            total_spent = sum(e.amount for e in self.expenses if e.date.startswith(ym))
            balance = total_collected - total_spent

            f.write("\nSummary:\n")
            f.write(f"- Total Collected: ₹{total_collected}\n")
            f.write(f"- Total Spent    : ₹{total_spent}\n")
            f.write(f"- Balance        : ₹{balance}\n")

        return True, filename

    def validate_ym(self, ym):
        return len(ym) == 7 and ym[4] == '-' and ym[:4].isdigit() and ym[5:].isdigit()
