import sqlite3
from datetime import datetime, timedelta
from prettytable import prettytable
from prettytable import from_db_cursor
import csv

#Advanced Squad Leader game logging program by HongKongWargamer
#Started 12 August 2021 Oxford UK
date_format='%Y-%m-%d'

#Class for each record, for flexibility
class PlayRecord:
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

#Command Menu
def command_menu():
    #Showing a count of the # of records
    cur.execute("SELECT COUNT(*) FROM gamelog")
    print("\n\nWe have {} records".format(cur.fetchone()))
    #The Menu
    print("\nAdvanced Squad Leader Game Log 1.0")
    print("==================================")
    print("Press 1: Show all records")
    print("Press 2: Input record")
    print("Press 3: Delete record")
    print("Press 4: Query by dates")
    print("Press 9: Export to CSV")
    print("Press *: See Credits")
    print("Type \"End\": Exit the system")
    command=input("\nInput command: ")
    if command=="1":
        #Show all records
        report_all()
        return True
    elif command=="2":
        #Add record
        Record=input_record()
        add_record(Record)
        report_all()
        return True
    elif command=="3":
        #Delete record
        Record=input_record()
        delete_record(Record)
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
    elif command.lower()=="end":
        export_csv()
        return False
    else:
        return True
    return
    



#Create table
def create_table():
    cur.execute("""CREATE TABLE gamelog (
                scen_id text,
                scen_name text,
                opponent_fn text,
                opponent_ln text,
                side_played text,
                attack_defender text,
                start_date text,
                finish_date text,
                result text,
                format text
                )""")

#Input Records
def input_record():

    #Date Validation
    def validate_date(d):
        try:
            datetime.strptime(d, date_format)
            return True
        except ValueError:
            return False

    #Getting scenario ID and name
    print("\n\nEntering Details of the Game .....")
    scen_id=""
    scen_name=""
    while scen_id=="":
        scen_id=input("Enter Scenario ID: ")
        if len(scen_id) > 8:
            print("Your Scenario ID seems to be too long?")
            scen_id=""
        else:
            pass
    while scen_name=="":
        scen_name=input("Enter Scenario Name: ")

    #List existing first names & ask for input
    cur.execute("SELECT DISTINCT opponent_fn FROM gamelog")
    print("Existing opponent first names: {}".format(cur.fetchall()))
    opponent_fn=""
    while opponent_fn=="":
        opponent_fn=input("Enter your Opponent's First Name: ")

    
    #List existing last names & ask for input
    cur.execute("SELECT DISTINCT opponent_ln FROM gamelog")
    print("Existing opponent last names: {}".format(cur.fetchall()))
    opponent_ln=""
    while opponent_ln=="":
        opponent_ln=input("Enter your Opponent's Last Name: ")
        opponent_ln=opponent_ln.capitalize()
    
    #List existing nationalities & ask for input
    cur.execute("SELECT DISTINCT side_played FROM gamelog")
    print("Existing nationalities in database: {}".format(cur.fetchall()))
    side_played=""
    while side_played=="":
        side_played=input("Which nationality did you play? ")

    # this 'input' command works for Python 3
    # if you're using Python 2, use 'raw_input' instead of 'input'
    while True:
        attack_defender = input("Were you the Attacker/ Defender? ")
        if attack_defender.lower() in ["attacker", "defender"]:
            attack_defender=attack_defender.capitalize()
            # we've got valid input! Break out of our 'while True' loop.
            break
        else:
            # invalid input. Loops back and asks again.
            print("Sorry, you must enter either Attacker or Defender.")
            continue

    #Start date?  Date validation
    valid=False
    while valid==False:
        start_date=input("Start date? YYYY-MM-DD ")
        valid=validate_date(start_date)
    start_date=datetime.strptime(start_date,date_format)

    #End date?  Date validation
    finish_date=datetime.strptime("1990-01-01",date_format)
        #Finish date should be after start date
    while finish_date<start_date:
        valid=False
        while valid==False:
            finish_date=input("Finish date? YYYY-MM-DD ")
            valid=validate_date(finish_date)
            if valid:
                finish_date=datetime.strptime(finish_date,date_format)

    #Win/Lost/Draw/Hold/Abandon?  Check input
    while True:
        result=input("Won/Lost/Draw/Hold/Abdn/PT ")
        if result.lower() in ["won","lost","draw","hold","abdn","pt"]:
            result=result.capitalize()
            if result == "Pt":
                result = result.upper()
            else:
                break
            break
        else:
            print("Sorry, results are confined to Won/Lost/Draw/Hold/Abdn/PT.")
            continue

    #Live/VASL/PBeM?  Check input
    while True:
        format=input("FtF/VASL/PBeM ")
        if format.lower() in ["ftf","vasl","pbem"]:
            if format.lower() == "ftf":
                format="FtF"
            elif format.lower() == "vasl":
                format="VASL"
            elif format.lower() == "pbem":
                format="PBeM"
            
            break
        else:
            print("Sorry, formats are confined to FtF, VASL or PBeM.")
            continue

    #Create an instance of PlayRecord
    Record = PlayRecord(scen_id,scen_name,opponent_fn,opponent_ln,side_played,attack_defender,start_date,finish_date,result,format)
    return Record

#Add Record after seeking user confirmation & looking for duplicates
def add_record(Record):
    # Add a record to the table via an instance of PlayRecord
    print("\n\n")
    col_names=["scen_id", "scen_name", "opponent_fn", "opponent_ln", "side_played", "attack_defender", "start_date", "finish_date", "result", "format"]
    x=prettytable.PrettyTable()
    x.field_names=col_names
    # add_data=[Record.scen_id,Record.scen_name,Record.opponent_fn,Record.opponent_ln,Record.side_played,Record.attack_defender,Record.start_date.strftime(date_format),Record.finish_date.strftime(date_format),Record.result, Record.format]
    # pretty_table(add_data)
    x.add_row([Record.scen_id,Record.scen_name,Record.opponent_fn,Record.opponent_ln,Record.side_played,Record.attack_defender,Record.start_date.strftime(date_format),Record.finish_date.strftime(date_format),Record.result, Record.format])
    print(x)

    user_okay=input("Save to Log? (Y/N) ")
    if user_okay.lower()=="y":
            # Check to see if there's a duplicate, if not, commit 
        cur.execute("SELECT * FROM gamelog WHERE scen_id=? AND opponent_ln=? AND attack_defender=? AND finish_date=?", (Record.scen_id, Record.opponent_ln, Record.attack_defender,Record.finish_date.date()))
        if len(str(cur.fetchone())) >5:
            print("This play record already exists. Not saving it.")
            return
        else:
            cur.execute("INSERT INTO gamelog VALUES(?,?,?,?,?,?,?,?,?,?)",(Record.scen_id,Record.scen_name,Record.opponent_fn,Record.opponent_ln,Record.side_played,Record.attack_defender,Record.start_date.strftime(date_format),Record.finish_date.strftime(date_format),Record.result,Record.format))
            con.commit()
            print("Game record saved")
            print("")
            # con.close
            return
    else:
        return
    return

# Delete Record after seeking user confirmation
def delete_record(Record):
    print(" ")
    print(" ")
    cur.execute("SELECT * FROM gamelog WHERE scen_id=? AND scen_name=? AND opponent_fn=? AND opponent_ln=? AND side_played=? AND attack_defender=? AND result=? AND start_date=? AND finish_date=? AND result=? AND format=?", (Record.scen_id, Record.scen_name, Record.opponent_fn, Record.opponent_ln, Record.side_played, Record.attack_defender, Record.result, Record.start_date.date(), Record.finish_date.date(), Record.result, Record.format))
    del_record=cur.fetchall()
    if del_record:
        pretty_table(del_record)
        print("Found the above for deletion")
    else:
        print("This record doesn't exist")
        return

    user_okay=input("Delete this Record? (Y/N) ")
    if user_okay.lower()=='y':
        cur.execute("DELETE FROM gamelog WHERE scen_id=? AND scen_name=? AND opponent_fn=? AND opponent_ln=? AND side_played=? AND attack_defender=? AND result=? AND start_date=? AND finish_date=? AND result=? AND format=?", (Record.scen_id, Record.scen_name, Record.opponent_fn, Record.opponent_ln, Record.side_played, Record.attack_defender, Record.result, Record.start_date.date(), Record.finish_date.date(), Record.result, Record.format))
        con.commit()
        report_all()
        print("Record(s) deleted")
    else:
        print("Nothing deleted")
        return
    return

# Query Data by Start Date Range
def query_table(Search_Field, Search_String):
    Field=Search_Field
    String=Search_String
    cur.execute("SELECT * FROM gamelog WHERE Field=String")
    print(cur.fetchall())

# Export data to CSV
def export_csv():
    # con=sqlite3.connect('ASLgamelog.db')
    # cur=con.cursor()
    # Execute the query
    cur.execute("SELECT scen_id, scen_name, opponent_fn, opponent_ln, side_played, attack_defender, start_date, finish_date, result, format FROM gamelog")
    export_file=cur.fetchall()

    with open("ASLGameLogData.csv","w") as csv_file:
        csv_writer=csv.writer(csv_file, dialect='excel')
        
        for line in export_file:
            csv_writer.writerow(line)
        
    # cur.close()
    # con.close()

# Query Data by Date Range
def query_date_range():

    #date validation
    def validate_date(d):
        try:
            datetime.strptime(d, date_format)
            return True
        except ValueError:
            return False

    print("\n\nQuery by Dates:")
    #Start date?  Date validation
    valid=False
    while valid==False:
        query_start_date=input("Start date? YYYY-MM-DD ")
        valid=validate_date(query_start_date)
    query_start_date=datetime.strptime(query_start_date,date_format)

    #End date?  Date validation
    query_finish_date=datetime.strptime("1990-01-01",date_format)
        #Finish date should be after start date
    while query_finish_date<query_start_date:
        valid=False
        while valid==False:
            query_finish_date=input("Finish date? YYYY-MM-DD ")
            valid=validate_date(query_finish_date)
            if valid:
                query_finish_date=datetime.strptime(query_finish_date,date_format)
    cur.execute("SELECT scen_id, scen_name, opponent_fn, opponent_ln, side_played, attack_defender, start_date, finish_date, result, format FROM gamelog WHERE finish_date BETWEEN ? AND ?",(query_start_date,query_finish_date))
    query_results=cur.fetchall()
    pretty_table(query_results)

def pretty_table(show_records):
    col_names=["scen_id", "scen_name", "opponent_fn", "opponent_ln", "side_played", "attack_defender", "start_date", "finish_date", "result", "format"]
    x=prettytable.PrettyTable()
    x.field_names=col_names
    for show_record in show_records:
        x.add_row(show_record)
    print(x)
    print("\n")


# Query Data by End Date Range



# Query Data by Opponent Name
 

# Query Data by Scenario ID


# Query Data by Scenario Name


# Update Play Record


# Commit changes & close





# REPORT ALL DATA
def report_all():
    # con=sqlite3.connect('ASLgamelog.db')
    # cur=con.cursor()
    cur.execute("SELECT scen_id, scen_name, opponent_fn, opponent_ln, side_played, attack_defender, start_date, finish_date, result, format FROM gamelog")
    mytable = from_db_cursor(cur)
    mytable.align["scen_id"]='l'
    mytable.align["scen_name"]='l'
    mytable.align["opponent_fn"]='l'
    mytable.align["opponent_ln"]='l'
    mytable.align["side_played"]='l'
    print("")
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
#Create Game Log db file if none exists
con=sqlite3.connect('ASLgamelog.db')
cur=con.cursor()

#Create Table if needed 
#Check if a table exists, if not, creates 'gamelog' Table
cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='gamelog' ")
if (cur.fetchone()[0])<1:
    print("Creating a gamelog table")
    create_table()

#Calling up the Command Menu
while command_menu():
    command_menu()

con.close()


