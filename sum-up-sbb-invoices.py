
import datetime
from io import BytesIO
from operator import concat
import re
from imap_tools import MailBox, A
from PyPDF2 import PdfReader
import sys

username = "YOUR_EMAIL"
password = "YOUR_PASSWORD"
imap_server = "YOUR_IMAP_SERVER"
emailfolder = "YOUR_EMAIL_FOLDER_WITH_ALL_SBB_EMAILS"
price_dict = {}
highest_price = 0.0
highest_price_attachment = None
highest_price_email = None

def get_as_float(chfBetrag):
    betrag = chfBetrag.replace('CHF', '').strip()
    return float(betrag)

def calculate():
    totalEasyRide = 0.0
    countEasyRide = 0
    totalOnlineKauf = 0.0
    countOnlineKauf = 0
    with MailBox(imap_server).login(username, password, emailfolder) as mailbox:
        for msg in mailbox.fetch(A(date_gte=datetime.date(2022, 6, 1))):
            if msg.subject.startswith('EasyRide Quittung'):
                sys.stdout.write("Processing Easyride from: %s   \r" % (msg.date))
                sys.stdout.flush()
                for attachement in msg.attachments:
                    countEasyRide += 1
                    totalEasyRide += get_easy_ride_betrag(attachement)
            elif msg.subject.startswith('Ihr Online-Kauf bei der SBB'):
                sys.stdout.write("Processing Online Kauf from: %s   \r" % (msg.date))
                sys.stdout.flush()
                countOnlineKauf += 1
                totalOnlineKauf += get_online_kauf_betrag(msg)
    return (totalEasyRide, countEasyRide, totalOnlineKauf, countOnlineKauf)

def get_easy_ride_betrag(attachement):
    global highest_price
    global highest_price_attachment
    global highest_price_email
    bytesIo = BytesIO(attachement.payload)
    reader = PdfReader(bytesIo)
    for page in reader.pages:
        text = page.extract_text()
        match = re.search('(?<=Gesamtbetrag).*\d*\.\d\d', text)
        if match and match.group:
            price = get_as_float(match.group(0))
            if price > highest_price:
                highest_price = price
                highest_price_attachment = attachement
                highest_price_email = None
            return price
    print(concat('No price found in: ', attachement.filename))

def get_online_kauf_betrag(msg):
    global highest_price
    global highest_price_email
    global highest_price_attachment
    match = re.search('(?<=CHF).*\d*\.\d\d', msg.text)
    if match and match.group:
        price = get_as_float(match.group(0))
        if price > highest_price:
            highest_price = price
            highest_price_email = msg
            highest_price_attachment = None
        return price
    print('No price found in Mail with subject {} on date {}'.format(msg.subject, str(msg.date)))

halbtaxPrice = 180.0
total = 0.0
easyRideTotal, easyRideCount, onlineKaufTotal, onlineKaufCount = calculate()
other = halbtaxPrice + 50.0
totalGesamt = onlineKaufTotal + easyRideTotal + other

sys.stdout.write("\n\n")
sys.stdout.flush()
print('Total from {} EasyRide invoices: {} CHF'.format(str(easyRideCount), str(float(f'{easyRideTotal:.2f}'))))
print('Total from {} Online Kauf invoices: {} CHF'.format(str(onlineKaufCount), str(float(f'{onlineKaufTotal:.2f}'))))
print('Total other: {} CHF'.format(str(float(f'{other:.2f}'))))
print('Total: {} CHF'.format(str(float(f'{totalGesamt:.2f}'))))

# Sort the price_dict by prices in descending order
sorted_prices = sorted(price_dict.items(), key=lambda x: x[0], reverse=True)

# Print the highest prices and their corresponding dates
print('Dates with the Highest Prices:')
for price, date in sorted_prices[:20]:
    print('Price: CHF {}, Date: {}'.format(price, date))

# Check if the highest_price_attachment is not None and save the attachment
if highest_price_attachment:
    with open('highest_price_attachment.pdf', 'wb') as file:
        file.write(highest_price_attachment.payload)
    print('Attachment with the highest price saved.')
else:
    with open('highest_price_email.html', 'w') as file:
        file.write(highest_price_email.html)
    print('Email with the highest price saved.')