import bs4
import requests
import smtplib
import time
import getpass

from collections import deque

# Base url of item listings on blocket
base_url = 'https://www.blocket.se/annonser/stockholm/fritid_hobby/sport_fritidsutrustning/traning_halsa?cg=6185&r=11'

# Enter email address to send & receive notifacations to
email = input("Email: ")

# And password to your email
password = getpass.getpass("Password: ")

# Deque to keep track of previous items found
items = deque(maxlen=40)


def scrape():

    def conditions(title, price):
        # Looking for keywords is listing title (i.e: 'cykel' and 'bike')
        # Also checking that listing is within my price range (i.e: < 1000kr)
        return 'cykel' in title.lower() or 'bike' in title.lower() and int(price) <= 1000

    res = requests.get(base_url)
    soup = bs4.BeautifulSoup(res.text, 'lxml')

    ads = soup.select('article')

    for item in ads:

        # Current listing
        title = item.select('.jzzuDW')[0].getText()
        price = item.select('.jkvRCw')[0].getText()

        # Stops loop when looking at old listings
        if (title, price) in items:
            break

        elif conditions(title, price[:-2].replace(' ', '')):

            info = {
                'title': title,
                'price': price,
                'location': item.select('.dxqCwo')[1].getText(),
                'timestamp': item.select('.bCcYiq')[0].getText()[5:],
                'link': 'https://www.blocket.se' + item.select('.enigRj')[0]['href']
            }

            if info in items:
                break
            else:
                items.appendleft(info)

                print('Item found: Email sent!')
                send_email(info)


def send_email(info):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()

    server.login(email, password)

    # Notification and message to be sent to email
    subject = 'Cheap stationary bike found'
    body = f'Title: {info["title"]} \n\nPrice: {info["price"]} \nLocation: {info["location"]} \nTime Posted: {info["timestamp"]} \n\nLink to original ad: {info["link"]}'

    msg = f'Subject: {subject}\n\n{body}'.encode()

    server.sendmail(
        email,
        email,
        msg
    )


# Check for new adds every 120 seconds
while True:
    scrape()
    time.sleep(120)
