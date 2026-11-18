from datetime import datetime
import json
import os
import random


class BankAccount:

  def __init__(
      self, account_number, name, pin, balance=0.0, transactions=None
  ):
    self.account_number = account_number
    self.name = name
    self.pin = pin
    self.balance = float(balance)
    self.transactions = transactions if transactions is not None else []

  def add_transaction(self, action, amount):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    self.transactions.append(
        f"[{timestamp}] {action}: ${amount:.2f} | Balance: ${self.balance:.2f}"
    )

  def deposit(self, amount):
    if amount <= 0:
      print("Error: Deposit amount must be greater than zero.")
      return False
    self.balance += amount
    self.add_transaction("Deposited", amount)
    print(
        f"Success! Deposited ${amount:.2f}. New Balance: ${self.balance:.2f}"
    )
    return True

  def withdraw(self, amount):
    if amount <= 0:
      print("Error: Withdrawal amount must be greater than zero.")
      return False
    if amount > self.balance:
      print("Error: Insufficient funds.")
      return False
    self.balance -= amount
    self.add_transaction("Withdrew", amount)
    print(f"Success! Withdrew ${amount:.2f}. New Balance: ${self.balance:.2f}")
    return True

  def to_dict(self):
    return {
        "account_number": self.account_number,
        "name": self.name,
        "pin": self.pin,
        "balance": self.balance,
        "transactions": self.transactions,
    }


class BankSystem:

  def __init__(self, data_file="bank_data.json"):
    self.data_file = data_file
    self.accounts = {}
    self.load_data()

  def load_data(self):
    if os.path.exists(self.data_file):
      try:
        with open(self.data_file, "r") as file:
          data = json.load(file)
          for acc_num, details in data.items():
            self.accounts[acc_num] = BankAccount(
                details["account_number"],
                details["name"],
                details["pin"],
                details["balance"],
                details["transactions"],
            )
      except (json.JSONDecodeError, KeyError):
        print("Warning: Data file corrupted. Starting with empty records.")

  def save_data(self):
    data = {
        acc_num: account.to_dict() for acc_num, account in self.accounts.items()
    }
    with open(self.data_file, "w") as file:
      json.dump(data, file, indent=4)

  def generate_account_number(self):
    while True:
      acc_num = str(random.randint(100000, 999999))
      if acc_num not in self.accounts:
        return acc_num

  def create_account(self):
    print("\n--- Create New Bank Account ---")
    name = input("Enter full name: ").strip()
    if not name:
      print("Error: Name cannot be empty.")
      return

    pin = input("Create a 4-digit PIN: ").strip()
    if not (pin.isdigit() and len(pin) == 4):
      print("Error: PIN must be exactly 4 digits.")
      return

    try:
      initial_deposit = float(input("Enter initial deposit amount ($): "))
      if initial_deposit < 0:
        print("Error: Initial deposit cannot be negative.")
        return
    except ValueError:
      print("Error: Invalid amount entered.")
      return

    acc_num = self.generate_account_number()
    new_account = BankAccount(acc_num, name, pin, initial_deposit)
    if initial_deposit > 0:
      new_account.add_transaction("Initial Deposit", initial_deposit)

    self.accounts[acc_num] = new_account
    self.save_data()

    print("\nAccount created successfully!")
    print(f"Account Holder : {name}")
    print(f"Account Number : {acc_num} (Please save this number to log in)")

  def authenticate(self):
    acc_num = input("Enter Account Number: ").strip()
    pin = input("Enter 4-digit PIN: ").strip()

    account = self.accounts.get(acc_num)
    if account and account.pin == pin:
      return account
    print("Error: Invalid Account Number or PIN.")
    return None

  def transfer_money(self, sender_account):
    recipient_num = input("Enter Recipient Account Number: ").strip()
    if recipient_num == sender_account.account_number:
      print("Error: Cannot transfer money to the same account.")
      return

    recipient_account = self.accounts.get(recipient_num)
    if not recipient_account:
      print("Error: Recipient account not found.")
      return

    try:
      amount = float(input("Enter amount to transfer ($): "))
    except ValueError:
      print("Error: Invalid amount.")
      return

    if amount <= 0:
      print("Error: Transfer amount must be greater than zero.")
      return
    if amount > sender_account.balance:
      print("Error: Insufficient funds.")
      return

    sender_account.balance -= amount
    recipient_account.balance += amount

    sender_account.add_transaction(
        f"Transferred to {recipient_account.name} ({recipient_num})", amount
    )
    recipient_account.add_transaction(
        f"Received from {sender_account.name} ({sender_account.account_number})",
        amount,
    )

    self.save_data()
    print(
        f"Success! Transferred ${amount:.2f} to {recipient_account.name}."
    )

  def account_menu(self, account):
    while True:
      print(
          f"\n--- Welcome, {account.name} (Acc: {account.account_number}) ---"
      )
      print("1. Check Balance")
      print("2. Deposit Money")
      print("3. Withdraw Money")
      print("4. Transfer Money")
      print("5. View Transaction History")
      print("6. Logout")

      choice = input("Select an option (1-6): ").strip()

      if choice == "1":
        print(f"\nCurrent Balance: ${account.balance:.2f}")

      elif choice == "2":
        try:
          amount = float(input("Enter deposit amount ($): "))
          if account.deposit(amount):
            self.save_data()
        except ValueError:
          print("Error: Please enter a valid number.")

      elif choice == "3":
        try:
          amount = float(input("Enter withdrawal amount ($): "))
          if account.withdraw(amount):
            self.save_data()
        except ValueError:
          print("Error: Please enter a valid number.")

      elif choice == "4":
        self.transfer_money(account)

      elif choice == "5":
        print("\n--- Transaction History ---")
        if not account.transactions:
          print("No transactions recorded yet.")
        else:
          for record in account.transactions:
            print(record)

      elif choice == "6":
        print("Logged out successfully.")
        break

      else:
        print("Invalid option. Please try again.")

  def run(self):
    while True:
      print("\n==================================")
      print("   PYTHON BANK MANAGEMENT SYSTEM")
      print("==================================")
      print("1. Create New Account")
      print("2. Login to Existing Account")
      print("3. Exit")

      choice = input("Select an option (1-3): ").strip()

      if choice == "1":
        self.create_account()
      elif choice == "2":
        account = self.authenticate()
        if account:
          self.account_menu(account)
      elif choice == "3":
        print("Thank you for using Python Bank. Goodbye!")
        break
      else:
        print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
  bank = BankSystem()
  bank.run()
