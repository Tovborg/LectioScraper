import lectioscraper

client = lectioscraper.Lectio("emil763x", "yApsCj@?8rQ&jMec", "59")

print(client.getUnreadMessages(to_json=True, get_content=True))