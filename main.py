"""
Main entry point for the expense tracker application.
"""
from cli import ExpenseTrackerCLI

if __name__ == "__main__":
    cli = ExpenseTrackerCLI()
    cli.run()
