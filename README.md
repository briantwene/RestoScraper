# RestoScraper

RestoScraper is a powerful web scraping API for extracting menu and reservation links from restaurant websites. Built with FastAPI and Model Context Protocol (MCP) for intelligent content extraction.

## Features

- Extract reservation links from restaurants (via OpenTable or direct website)
- Find menu links on restaurant websites
- Fast API endpoints for easy integration
- Intelligent scraping using MCP and Playwright
- JSON response format for easy data processing

## Setup

### Prerequisites

- Python 3.10 or higher (ideally 3.12+)
- Git (for cloning the repo)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/restoscraper.git
   cd restoscraper
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv env
   env\Scripts\activate

   # macOS/Linux
   python -m venv env
   source env/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a .env file in the project root:
   ```
   OPENAI_KEY=your_openai_api_key
   ```

## Running the Server

Start the server with:

```bash
python main.py
```

The server will run on http://localhost:9000 by default.

## API Usage

### Scrape Restaurant Links

```bash
curl -X POST "http://localhost:9000/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Restaurant Name",
    "website": "https://restaurant-website.com",
    "location": "City, Country"
  }'
```

Example response:

```json
{
  "reservationUrl": "https://www.opentable.com/restaurant-name",
  "menuUrl": "https://restaurant-website.com/menu",
  "source": {
    "reservation": "OpenTable",
    "menu": "Website"
  },
  "debug": {
    "opentableQuery": "Restaurant Name opentable",
    "menuKeywordsMatched": ["menu", "our food"],
    "reservationKeywordsMatched": ["book", "reserve"],
    "sitemapChecked": true
  }
}
```

## License

MIT
