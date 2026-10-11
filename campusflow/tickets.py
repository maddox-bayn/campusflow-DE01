import json
import os


allowed_categories= ["Network", "Hardware", "Software", "Others"]
allowed_urgency = ["low", "medium", "high"]

class CampusFlow:

    def __init__(self, file_name ="store_tickets.json"):
        self.file_name = file_name
        self.tickets = {}
        self.num_id = 1
        self.load_data()
    # function to calculate the priority 
    def calculate_priority(self, urgency, affected_users):
        # Validating for the critical
        if urgency == "high" and affected_users >= 10:
            return "Critical"
        # Validating for the high
        if urgency == "high" or affected_users >= 10:
            return "High"
        # Validating for medium
        if urgency == "medium" or affected_users >= 3:
            return "Medium"
        return "Low"
    # function that write to a file in json format
    def save_record(self):
        saved_data ={"num_id": self.num_id, "tickets": self.tickets}
        try:
            with open(self.file_name,"w") as file:
                json.dump(saved_data, file, indent=4)
        except Exception as err:
            print(f"An error occured, state error as {err}")
    # function that read file from json to python
    def load_data(self):
        # check if the file exist 
        if not os.path.exists(self.file_name):
            print(f"this file {self.file_name} does not exist")
            return
        try:
            with open(self.file_name, "r") as infile:
                saved_data = json.load(infile)
                self.tickets = saved_data.get("tickets", {})
                self.num_id = saved_data.get("num_id", 1)
        except json.JSONDecodeError as e:
            print(f"this file {self.file_name} is empty {e}, entering first data")
            return
    # function for ticket creation
    def create_ticket(self):
        title = input("Enter title: ").strip()
        if not title:
            print("Title can't be empty")
            return
        # Validating category
        category = input("Enter Category: ").strip()
        if category not in allowed_categories:
            print(f"invalid category, category must be in {allowed_categories}")
            return
        # Validating urgency
        urgency = input("Enter Urgency: ").strip().lower()
        
        if urgency not in allowed_urgency:
            print("Invalid urgency level: {urgency}")
            return
        # validating the affected users
        raw_users = input("Enter affected user: ").strip()
        try:
            affected_users = int(raw_users)
            if affected_users <=0 or str(affected_users) != raw_users:
                raise ValueError
        except ValueError:
            print("invalid affected users")
            return
        priority= self.calculate_priority(urgency, affected_users)
        user_id = f"F-{self.num_id:03d}"
        self.num_id += 1
        self.tickets[user_id]={
            "id": user_id,
            "title": title,
            "category": category,
            "urgency": urgency,
            "affected_users": affected_users,
            "priority": priority,
            "status": "open",
            "assigned_to":None
        }
        self.save_record()
        print(f"Success! Ticket id {user_id} logged with {priority} priority")
    # function to list and view ticket
    def list_view_tickets(self):
        if not self.tickets:
            print(f"This ticket found in the tickets")
            return
        print(f"{'ID':<6} | {'Category':<10} | {'Priority':<9} | {'Status':<12} | {'Assigned Agent'}")
        print("-" * 65)
        for tid, t in self.tickets.items():
            agent = t["assigned_to"] if t["assigned_to"] else "unassigned"
            print(f"{tid:<6} | {t['category']:<10} | {t['priority']:<9} | {t['status']:<12} | {agent}")
        enter_id = input("\nEnter Ticket id: or hit enter to skip").strip().upper()
        if enter_id not in self.tickets:
            print(f"this Id {enter_id}can't be fond in tickets")
            return
        t = self.tickets[enter_id]
        print(f"\n================ [{t['id']}] DETAIL METRICS ================")
        print(f" Title:          {t['title']}")
        print(f" Category:       {t['category']}")
        print(f" Urgency Level:  {t['urgency'].upper()}")
        print(f" Affected Users: {t['affected_users']}")
        print(f" Priority Tier:  {t['priority'].upper()}")
        print(f" Workflow State: {t['status'].upper()}")
        print(f" Assigned Staff: {t['assigned_to'] if t['assigned_to'] else 'None'}")
        print("=====================================================")
if __name__ == "__main__":
    app = CampusFlow()
    while True:
        action = input("Enter execution command index (1-7): ").strip()
        print("\n--- CAMPUSFLOW INTERFACE ---")
        print("1. Create Ticket (F1)")
        print("2. List / View Tickets (F2)")
        print("3. Exit")
       
        if action in ["1", "2"]:
            app.load_data()
        if action == "1":
            app.create_ticket()
        elif action == "2":
            app.list_view_tickets()
        elif action == "3":
            print("\nShutting down cleanly.")
            break
        else:
            print("[Error] Invalid selection.")
