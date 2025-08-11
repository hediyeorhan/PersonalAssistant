import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.reminder_agent import ReminderAgent

agent = ReminderAgent()
agent.check_and_notify()
