import scrapy

class BooksToScrape(scrapy.Spider):
    # change this limit to limit scraping
    CRAWL_LIMIT = 1000
    name = "book_spider"
    start_urls = ["https://books.toscrape.com/"]
    unique_books = set()

    def parse(self, response):
        element = response.css('ul.nav.nav-list li')
        categories = element.css('a::attr("href")').getall()
        for category in categories:
            if category == "index.html":
                continue
            category = category.replace("../","/")
            url = f"https://books.toscrape.com/{category}"
            yield scrapy.Request(url, callback=self.scrape_category)

    def scrape_category(self, response):
        books = response.xpath('//*[contains(@class,"product_pod")]')
        print(len(books))
        for book in books:
            print("Book ", book.xpath('.//h3/a/@title').get())
            book_url = response.urljoin(book.xpath('.//h3/a/@href').get())
            if (book_url in self.unique_books) or len(self.unique_books) > self.CRAWL_LIMIT:
                continue
            self.unique_books.add(book_url)
            yield {
                "book_title": book.xpath('.//h3/a/@title').get(),
                "book_price": book.xpath('.//p[contains(@class,"price_color")]/text()').get(),
                "book_details_url": book_url,
                "book_image_url": response.urljoin(book.xpath('.//div[contains(@class,"image_container")]/@src').get())
            }
        next_page = response.xpath('//li[contains(@class,"next")]/a/@href').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url,callback=self.scrape_category)
