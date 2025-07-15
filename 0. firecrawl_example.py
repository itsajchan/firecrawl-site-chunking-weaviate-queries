from firecrawl import FirecrawlApp, ScrapeOptions

app = FirecrawlApp(api_key="fc-XXXXX")

# Scrape a website:
scrape_status = app.scrape_url(
  'https://www.tripadvisor.co.nz/ShowUserReviews-g55711-d19346260-r944394581-SIXT_Rental_Car-Dallas_Texas.html', 
  formats=['markdown', 'html']
)
print(scrape_status)

