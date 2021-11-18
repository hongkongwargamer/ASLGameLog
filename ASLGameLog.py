import sqlite3
from datetime import datetime, timedelta
from prettytable import prettytable
from prettytable import from_db_cursor
import csv

#Advanced Squad Leader game logging program by HongKongWargamer
#Started 12 August 2021 Oxford UK
DATE_FORMAT='%Y-%m-%d'


class PlayRecord:
    """Class for each record, for flexibility."""
    def __init__(self,scen_id,scen_name,opponent_fn,opponent_ln,side_played,attack_defender,start_date,finish_date,result,format):
        self.scen_id=scen_id
        self.scen_name=scen_name
        self.opponent_fn=opponent_fn
        self.opponent_ln=opponent_ln
        self.side_played=side_played
        self.attack_defender=attack_defender
        self.start_date=start_date
        self.finish_date=finish_date
        self.result=result
        self.format=format

    def as_tuple(self):
        return (
            self.scen_id,
            self.scen_name,
            self.opponent_fn,
            self.opponent_ln,
            self.side_played,
            self.attack_defender,
            self.start_date,
            self.finish_date,
            self.result,
            self.format,
            )

    def as_table(self):
        x = prettytable.PrettyTable()
        x.field_names = ["scen_id", "scen_name", "opponent_fn", "opponent_ln", "side_played", "attack_defender", "start_date", "finish_date", "result", "format"]
        x.add_row(self.as_tuple())
        return x


def input_confirmation(prompt):
    """Prompt user to confirm Y/N."""
    valid_answers = ['y', 'n', 'yes', 'no']
    answer = None
    while answer not in valid_answers:
        answer = input("{} Y/N ".format(prompt)).lower()
    return answer in ['y', 'yes']


def input_date(prompt):
    """Prompt user to enter date."""
    answer = None
    while not answer:
        try:
            answer = datetime.strptime(input("{} YYYY-MM-DD ".format(prompt)), DATE_FORMAT).date()
        except ValueError:
            answer = None
    return answer


def input_multiple_choice(prompt, valid_answers):
    """Prompt user to select one of multiple choices."""
    text = "/".join(valid_answers)
    answer = None
    while answer not in valid_answers:
        answer = input("{} {}? ".format(prompt, text))
        if answer not in valid_answers:
            print("Sorry, answers are confined to {}.".format(text))
    return answer


def input_string(prompt):
    """Prompt user to enter text."""
    answer = None
    while not answer:
        answer = input("{} ".format(prompt))
    return answer


#Command Menu
def command_menu():
    print("\nAdvanced Squad Leader Game Log 1.0")
    print("==================================")
    print("Press 1: Show all records")
    print("Press 2: Input record")
    print("Press 3: Delete record")
    print("Press 4: Query by dates")
    print("Press 9: Export to CSV")
    print("Press *: See Credits")
    print("Type \"End\": Exit the system")
    command=input("Input command: ").lower()
    if command=="1":
        #Show all records
        report_all()
        return True
    elif command=="2":
        #Add record
        record=input_record()
        add_record(record)
        report_all()
        return True
    elif command=="3":
        #Delete record
        record=input_record()
        delete_record(record)
        report_all()
        return True
    elif command=="4":
        #Query by Year
        query_date_range()
        return True
    elif command=="9":
        #Export to CSV
        export_csv()
        return True
    elif command=="*":
        print_credits()
        return True
    elif command=="end":
        export_csv()
        return False
    else:
        return True
    return
    



#Create Table if needed
def create_table():
    #Check if a table exists, if not, creates 'gamelog' Table
    cur=con.cursor()
    cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='gamelog' ")
    if (cur.fetchone()[0])<1:
        print("Creating a gamelog table")
        cur.execute("""CREATE TABLE gamelog (
                scen_id text,
                scen_name text,
                opponent_fn text,
                opponent_ln text,
                side_played text,
                attack_defender text,
                start_date date,
                finish_date date,
                result text,
                format text
                )""")


def record_count():
    cur=con.cursor()
    cur.execute("SELECT count(*) FROM gamelog")
    return cur.fetchone()[0]


#Input PlayRecord
def input_record():
    cur=con.cursor()
    print("\n\nEntering Details of the Game .....")

    #Getting scenario ID and name
    scen_id = input_string("Enter Scenario ID:")
    scen_name = input_string("Enter Scenario Name:")

    #List existing first names & ask for input
    cur.execute("SELECT DISTINCT opponent_fn FROM gamelog")
    print("Existing opponent first names: {}".format("/".join(x[0] for x in cur.fetchall())))
    opponent_fn = input_string("Enter your Opponent's First Name:")

    #List existing last names & ask for input
    cur.execute("SELECT DISTINCT opponent_ln FROM gamelog")
    print("Existing opponent last names: {}".format("/".join(x[0] for x in cur.fetchall())))
    opponent_ln = input_string("Enter your Opponent's Last Name:")

    #List existing nationalities & ask for input
    cur.execute("SELECT DISTINCT side_played FROM gamelog")
    print("Existing nationalities in database: {}".format("/".join(x[0] for x in cur.fetchall())))
    side_played = input_string("Which nationality did you play?")

    attack_defender = input_multiple_choice("Were you the", ("Attacker", "Defender"))

    #Start date?
    start_date = input_date("Start date?")

    #Finish date? Finish date must be after start date.
    finish_date = datetime.strptime("1000-1-1", DATE_FORMAT).date()
    while (not finish_date) or finish_date < start_date:
        finish_date = input_date("Finish date?")
        if finish_date < start_date:
            finish_date = datetime.strptime("1000-1-1", DATE_FORMAT).date()

    #Win/Lost/Draw/Hold/Abandon?
    game_result = input_multiple_choice("Result", ("Won", "Lost", "Draw", "Hold", "Abdn", "PT"))

    #Live/VASL/PBeM?
    game_format = input_multiple_choice("Format", ("FtF","VASL","PBeM"))

    #Create and return instance of PlayRecord
    return PlayRecord(scen_id,scen_name,opponent_fn,opponent_ln,side_played,attack_defender,start_date,finish_date,game_result,game_format)


#Add PlayRecord after seeking user confirmation & looking for duplicates
def add_record(record):
    # Add a record to the table via an instance of PlayRecord
    cur=con.cursor()
    print("\n")
    print(record.as_table())
    # Check to see if there's a duplicate.
    cur.execute("SELECT * FROM gamelog WHERE scen_id=? AND opponent_ln=? AND attack_defender=? AND finish_date=?", (record.scen_id, record.opponent_ln, record.attack_defender,record.finish_date))
    if cur.fetchone():
        print("This play record already exists. Not saving it.")
        return
    if input_confirmation("Save to Log?"):
        cur.execute("INSERT INTO gamelog VALUES(?,?,?,?,?,?,?,?,?,?)", record.as_tuple())
        con.commit()
        print("Game record saved.")


# Delete PlayRecord after seeking user confirmation
def delete_record(record):
    cur=con.cursor()
    print("\n")
    print(record.as_table())
    cur.execute("SELECT * FROM gamelog WHERE scen_id=? AND scen_name=? AND opponent_fn=? AND opponent_ln=? AND side_played=? AND attack_defender=? AND result=? AND start_date=? AND finish_date=? AND result=? AND format=?", (record.scen_id, record.scen_name, record.opponent_fn, record.opponent_ln, record.side_played, record.attack_defender, record.result, record.start_date.date(), record.finish_date.date(), record.result, record.format))
    del_record=cur.fetchone()
    if not del_record:
        print("This record doesn't exist")
        return
    print("\nFound the above for deletion")

    if input_confirmation("Delete this record?"):
        cur.execute("DELETE FROM gamelog WHERE scen_id=? AND scen_name=? AND opponent_fn=? AND opponent_ln=? AND side_played=? AND attack_defender=? AND result=? AND start_date=? AND finish_date=? AND result=? AND format=?", (record.scen_id, record.scen_name, record.opponent_fn, record.opponent_ln, record.side_played, record.attack_defender, record.result, record.start_date.date(), record.finish_date.date(), record.result, record.format))
        con.commit()


# Query Data by Start Date Range
def query_table(field, search):
    cur=con.cursor()
    cur.execute("SELECT * FROM gamelog WHERE {}=?".format(field), (search, ))
    print(cur.fetchall())

# Export data to CSV
def export_csv():
    con=sqlite3.connect('ASLgamelog.db')
    cur=con.cursor()
    # Execute the query
    cur.execute("SELECT scen_id, scen_name, opponent_fn, opponent_ln, side_played, attack_defender, start_date, finish_date, result, format FROM gamelog")
    export_file=cur.fetchall()

    with open("ASLGameLogData.csv","w") as csv_file:
        csv_writer=csv.writer(csv_file, dialect='excel')
        
        for line in export_file:
            csv_writer.writerow(line)
        
    cur.close()
    con.close()

# Query Data by Date Range
def query_date_range():
    cur=con.cursor()
    print("\n\nQuery by Dates:")
    start_date = input_date("Start date?")
    #Finish date? Finish date must be after start date.
    finish_date = datetime.strptime("1000-1-1", DATE_FORMAT).date()
    while (not finish_date) or finish_date < start_date:
        finish_date = input_date("Finish date?")
        if finish_date < start_date:
            finish_date = datetime.strptime("1000-1-1", DATE_FORMAT).date()
    cur.execute("SELECT scen_id, scen_name, opponent_fn, opponent_ln, side_played, attack_defender, start_date, finish_date, result, format FROM gamelog WHERE finish_date BETWEEN ? AND ?",(start_date,finish_date))
    report_all(cur)



# Query Data by End Date Range



# Query Data by Opponent Name
 

# Query Data by Scenario ID


# Query Data by Scenario Name


# Update Play Record


# Commit changes & close



# REPORT ALL DATA
def report_all(cur=None):
    if cur is None:
        cur=con.cursor()
        cur.execute("SELECT scen_id, scen_name, opponent_fn, opponent_ln, side_played, attack_defender, start_date, finish_date, result, format FROM gamelog")
    mytable = from_db_cursor(cur)
    mytable.align["scen_id"]='l'
    mytable.align["scen_name"]='l'
    mytable.align["opponent_fn"]='l'
    mytable.align["opponent_ln"]='l'
    mytable.align["side_played"]='l'
    print(mytable.get_string(sortby="finish_date"))

# Report Games by Completed Date Range (W/L) (A/D) (Nationality) (Format)


# Report Games that are in Progress


# Report Games that are Playtesting

# Print credits
def print_credits():
    print("")
    print("")
    print("Created by Jackson CS Kwan, 12 Aug 2021, Oxford")
    print("Creator provides NO guarantees.  Use at your own risk.")
    print("hongkongwargamer@disroot.org")
    print("hongkongwargamer.com")
    print("@HWargamer")


#Main Program =====================================================

if __name__ == "__main__":
    con=sqlite3.connect("ASLgamelog.db")

    #Create Game Log db file if none exists
    create_table()

    print("{} existing records.\n".format(record_count()))

    #Calling up the Command Menu
    while command_menu():
        pass

    con.close()
