import json

class MarketData:
    def __init__(self, filename='/media/tb/linux/txts/marketData.json'):
        self.filename = filename
        self.data = []

    def load_data(self):
        try:
            with open(self.filename, 'r') as file:
                self.data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = []

    def save_data(self):
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

    def find_item(self, title):
        for item in self.data:
            if item['title'] == title:
                return item
        return None

    def updateBook(self, title, bidAskSharesBook):
        item = self.find_item(title)
        if item:
            item['bidShares'] = bidAskSharesBook.get('bidShares', item['bidShares'])
            item['askShares'] = bidAskSharesBook.get('askShares', item['askShares'])
            self.save_data()

    def updateBidAskPrices(self, title, bidAskArrays):
        item = self.find_item(title)
        if item:
            item['bid'] = bidAskArrays.get('bid', item['bid'])
            item['ask'] = bidAskArrays.get('ask', item['ask'])
            self.save_data()

    def addText(self, title, sentence):
        item = self.find_item(title)
        if item:
            item['sentences'].insert(0, sentence)
            self.save_data()

    def addNewTitle(self, title):
        if not self.find_item(title):
            new_item = {
                'title': title,
                'bid': [],
                'ask': [],
                'bidShares': [],
                'askShares': [],
                'sentences': []
            }
            self.data.append(new_item)
            self.save_data()

# Example usage
market_data = MarketData()
market_data.load_data()

# Update book
market_data.updateBook('New Stock Analysis', {'bidShares': [{'price': 50, 'shares': 100}], 'askShares': [{'price': 55, 'shares': 80}]})

# Update bid/ask prices
market_data.updateBidAskPrices('New Stock Analysis', {'bid': [{'epoch': 1633036800, 'price': 50}], 'ask': [{'epoch': 1633036800, 'price': 55}]})

# Add text
market_data.addText('New Stock Analysis', 'This is a new analysis sentence.')

# Add text
market_data.addText('Stock Analysis for XYZ Corp', 'This is a new analysis sentence.')





