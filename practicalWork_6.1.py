import sqlite3
# Creates simple table with id and name columns. I intended it for weekdays, domains and email hosts
def create_two_col_table(list, table_name):
    cur.execute('DROP TABLE IF EXISTS ' + table_name)
    cur.execute('CREATE TABLE ' + table_name + ' (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, Name TEXT UNIQUE)')
    for item in list.keys():
        cur.execute('INSERT INTO ' + table_name + ' (ID, Name) VALUES (?, ?)',
            (list[item], item))
        conn.commit()
# Sets values for keys in dictionaries in ascending order
def set_values(list):
    value = 1
    for item in list.keys():
        list[item] = value
        value += 1

file = "mbox-short.txt"
fileHandle = open(file)

emails = list()
spam_confidence = list()
domains = dict()
email_addresses = dict()
weekdays = dict()
dict_value = 0
# Finds the lines that starts with a 'From' and contains the necessary information. Then appends the 
# information in respective lists
for line in fileHandle:
    if line.startswith("From"):
        if line.startswith("From:"):
            continue
        emails.append(line)
        parts = line.split(" ")
        if parts[2] not in weekdays.keys():
            weekdays[parts[2]] = dict_value
        email_parts = parts[1].split("@")
        if email_parts[1] not in domains.keys():
            domains[email_parts[1]] = dict_value
        if email_parts[0] not in email_addresses.keys():
            email_addresses[email_parts[0]] = dict_value
    if line.startswith("X-DSPAM-Confidence"):
        index = line.split(" ")
        spam_confidence.append(index[1].strip())

set_values(domains)
set_values(weekdays)
set_values(email_addresses)

conn = sqlite3.connect('emails.sqlite')
cur = conn.cursor()

create_two_col_table(weekdays, "Weekdays")
create_two_col_table(domains, "Domains")
create_two_col_table(email_addresses, "Addresses")
# creates the 'emails' list with corresponding id values
cur.execute('DROP TABLE IF EXISTS Emails')
cur.execute('CREATE TABLE Emails (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, Domain_id INTEGER, Addresses_id INTEGER, Weekdays_id INTEGER, Spam_confidence_level INTEGER)')
emails_id = 1
spam_index = 0
for mail in emails:
    parts = mail.split(" ")
    email_parts = parts[1].split("@")
    cur.execute('INSERT INTO Emails (ID, Domain_id, Addresses_id, Weekdays_id, Spam_confidence_level) VALUES (?, ?, ?, ?, ?)',
            (emails_id, domains[email_parts[1]], email_addresses[email_parts[0]], weekdays[parts[2]], spam_confidence[spam_index]))
    conn.commit()
    emails_id += 1
    spam_index += 1

print("Domains:")
cur.execute('SELECT name FROM Domains')
for domain in cur:
    print(" - ", domain[0])

while True:
    chosen_domain = input("Enter a domain name from the latter list:")
    if chosen_domain in domains.keys():
        break
    else:
        print("There is no such domain! Try again!")

chosen_id = str(domains[chosen_domain])

print("")
print("Emails received from chosen domain name:")
cur.execute('''SELECT Addresses.Name, Domains.Name, Weekdays.Name, Emails.Spam_confidence_level
    FROM Emails
    JOIN Domains ON Emails.Domain_id = Domains.ID
    JOIN Weekdays ON Emails.Weekdays_id = Weekdays.ID
    JOIN Addresses ON Emails.Addresses_id = Addresses.ID
    WHERE Weekdays.Name IN ("Fri", "Sat") AND Domains.Name = ?''', (chosen_domain, ))
for email in cur:
    print(email)

cur.close()
conn.close()