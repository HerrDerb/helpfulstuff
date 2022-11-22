
import datetime
from io import BytesIO
from operator import concat
import re
from imap_tools import MailBox, A
from PyPDF2 import PdfReader
import sys
from price_parser import Price
from decimal import Decimal

username = "YOUR_EMAIL"
password = "YOUR_PASSWORD"
imap_server = "YOUR_IMAP_SERVER"
emailfolder = "YOUR_EMAIL_FOLDER_WITH_ALL_SBB_EMAILS"

def getAsFloat(chfBetrag):
    betrag = chfBetrag.replace('CHF','').strip()
    price = Price(amount=Decimal(betrag),amount_text=betrag, currency='CHF')
    return price.amount_float

def calculate():
    totalEasyRide = 0.0
    countEasyRide = 0
    totalOnlineKauf = 0.0
    countOnlineKauf = 0
    with MailBox(imap_server).login(username, password, emailfolder) as mailbox:
     for msg in mailbox.fetch(A(date_gte=datetime.date(2022, 6, 1))):
        if msg.subject.startswith('EasyRide Quittung'):
            sys.stdout.write("Processing Easyride from: %s   \r" % (msg.date) )
            sys.stdout.flush()
            for attachement in msg.attachments:
                countEasyRide+=1
                totalEasyRide+=getEasyRideBetrag(attachement)
        elif msg.subject.startswith('Ihr Online-Kauf bei der SBB'):
            sys.stdout.write("Processing Online Kauf from: %s   \r" % (msg.date) )
            sys.stdout.flush()
            countOnlineKauf+=1
            totalOnlineKauf+=getOnlineKaufBetrag(msg)
    return (totalEasyRide, countEasyRide,totalOnlineKauf,countOnlineKauf)

def getEasyRideBetrag(attachement):
    bytes = BytesIO(attachement.payload)
    reader = PdfReader(bytes)
    for page in reader.pages:
        text = page.extract_text()
        match = re.search('(?<=Gesamtbetrag).*\d*\.\d\d', text)
        if match and match.group:
            return getAsFloat(match.group(0))
    print(concat('Not price foundfound in: ', attachement.filename))

def getOnlineKaufBetrag(msg):
    match = re.search('(?<=CHF).*\d*\.\d\d', msg.text)
    if match and match.group:
        return getAsFloat(match.group(0))
    print('Not price found in Mail with subject {} on date {} ',msg.subject, str(msg.date))

halbtaxPrice=180.0
total = 0.0
easyRideTotal, easyRideCount, onlineKaufTotal, onlineKaufCount=calculate()
other = halbtaxPrice + 50.0
totalGesamt = onlineKaufTotal + easyRideTotal + other

sys.stdout.write("\n\n")
sys.stdout.flush()
print('Total from {} EasyRide invoices: {} CHF'.format(str(easyRideCount), str(float(f'{easyRideTotal:.2f}'))))
print('Total from {} Online Kauf invoices: {} CHF'.format(str(onlineKaufCount), str(float(f'{onlineKaufTotal:.2f}'))))
print('Total other: {} CHF'.format(str(float(f'{other:.2f}'))))
print('Total: {} CHF'.format(str(float(f'{totalGesamt:.2f}'))))
