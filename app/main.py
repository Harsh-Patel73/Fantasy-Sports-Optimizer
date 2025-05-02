from scrapers import pinnacle

def run_all_scrapers():
    data = []
    print("Running all scrapers")

    try: 
        print('trying')
        data.append(pinnacle.scrape())
    except Exception as e:
        print(f"Pinnacle scrape failed: {e}")

    return data

run_all_scrapers()