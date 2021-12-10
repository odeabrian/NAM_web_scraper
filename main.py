import smtplib
from email.message import EmailMessage
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from requests_html import HTMLSession

config = dotenv_values(".env")

# Send an email with the list of identified parts
def sendMail(message):
    to = config["TO_EMAIL"]
    # Check if the scraper found any matches, if not change the body of the email
    if message:
        body = f"Here's what I found for you today: \n\n{message}"
    else:
        body = "Sorry, I couldn't find anything for you today."

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = "North American Motoring - Parts Alert"
    msg['From'] = f"{config['NAME']} {config['FROM_EMAIL']}"
    msg['To'] = to

    with smtplib.SMTP(config["SMTP"], port=config["PORT"]) as mail:
        mail.starttls()
        mail.login(user=config["FROM_EMAIL"], password=config["PASSWORD"])
        mail.send_message(msg)


def searchData():
    # Setting the URL to the North American Motoring parts market
    session = HTMLSession()
    url = 'https://www.northamericanmotoring.com/forums/market'
    # Scrape the website
    result = session.get(url)
    # Store the resulting data as text
    soup = BeautifulSoup(result.text, 'html.parser')

    # Get the keywords from the user to apply to the search
    print("Enter keywords or car code you want to be alerted for (separate keywords with commas): ")
    keywords = input('>')
    print(f"You are searching for {keywords} parts")
    keywords = keywords.replace(' ', '').strip()
    keywords = list(keywords.split(","))
    # keywords = ['R53']

    # Find all listings
    # Check if listing is for sale or parting out
    # If true then check if listing title contains any keywords
    # Return data

    listings = soup.find_all('div', class_='shelf-item')

    founditems = []

    # Iterate through all the tags with the class of "shelf-item"
    for i in listings:

        # This tag can be used to identify whether or not the item is for sale. There are 3 different cases: FOR
        # SALE, WANT TO BUY (WTB), and PART OUT We want to look at all items currently marked as for sale and parting
        # out
        if i.find('div', class_='listing-banner sale') or i.find('div', class_='listing-banner part'):

            # Get the listing title, link, and price
            title = i.find('h3', class_='title').a.text
            link = i.find('h3', class_='title').a['href']
            price = i.find('div', class_='price').text.replace(' ', '')

            for key in keywords:
                if key.casefold() in title.casefold():
                    founditem = {

                        'title': title,
                        'link': link,
                        'price': price.strip()

                    }

                    founditems.append(founditem)

    return founditems


# Reformat the dictionary items into a readable email format
def reformat():
    formatted = ""

    if searchData():
        for i in searchData():
            formatted += f"Item: {i['title']}\n{i['link']}\nPrice: {i['price']}\n\n"

    return formatted


message = reformat()

sendMail(message)
