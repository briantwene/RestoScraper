# scraper.py
from agents import Agent, Runner, set_default_openai_key, WebSearchTool
from agents.mcp import MCPServerStdio, MCPServer
from agents.model_settings import ModelSettings
import os
import json
from dotenv import load_dotenv
from model import RestaurantInfo

load_dotenv()
set_default_openai_key(os.getenv("OPENAI_KEY"))


# Define your restaurant input here
# restaurant_input = {
#     "name": "Dishoom Shoreditch",
#     "website": "https://www.dishoom.com/shoreditch",
#     "location": "London, UK",
# }

restaurant_input = {
    "name": "Colonel Saab High Holborn",
    "website": "https://colonelsaab.co.uk/",
    "location": "London, UK",
}

instructions = """
You are a web assistant that extracts the reservation and menu links for a restaurant.

You are given:
- The restaurant's name
- Its website URL

Follow this scenario. You have freedom to search the web or website, but you must follow these steps:

1. **Check OpenTable using Bing Search**:
   - Perform a Bing search with the query: "<restaurant name> opentable"
   - If the search returns results, check if the restaurant is listed.
   - If a valid OpenTable page is found, enter the page and see if a reservation can be made there.
   - If so, extract the URL and use it as the reservation URL.

2. **Then check the restaurant website**:
   - Always attempt to find a menu link. Look for anchors or buttons containing terms like:
     "menu", "our food", "see dishes", "view menu", "food menu", "order".
   - If no reservation was found on OpenTable, look for a reservation link containing terms like:
     "reserve", "book", "find a table", "make a reservation", "table".
   - If the menu or reservation content is inside a modal (not a separate page), try and get the link for this as it may be an iframe. if there is no link available in this scenario, you may return the current page’s URL instead.
   - **If the page has a sitemap or `robots.txt` entry pointing to one, check it.**
   - If not, try visiting `/sitemap.xml` and extract relevant links from there if accessible.

Return your response as a **JSON object** in the following format:

{
  "reservationUrl": "<url or null>",
  "menuUrl": "<url or null>",
  "source": {
    "reservation": "OpenTable" | "Website" | "Sitemap" | null,
    "menu": "Website" | "Sitemap" | null
  },
  "debug": {
    "opentableQuery": "<your Google search query here>",
    "menuKeywordsMatched": ["menu", "our food"],
    "reservationKeywordsMatched": ["book", "reserve"],
    "sitemapChecked": true
  }
}

Only return the JSON. Do not include any explanation or commentary.
"""


async def setup_agent_environment(app):
    # Start MCP Server once
    server = MCPServerStdio(
        name="Playwright MCP Server",
        params={"command": "npx", "args": ["@playwright/mcp@latest", "--headless"]},
        cache_tools_list=True,
    )
    await server.connect()

    agent = Agent(
        name="RestaurantLinkFinder",
        instructions=instructions,
        model="gpt-4.1-mini",
        #tools=[WebSearchTool()],
        mcp_servers=[server],
        model_settings=ModelSettings(tool_choice="required"),

    )

    app.state.server = server
    app.state.agent = agent

async def get_menu_reservation(agent: Agent, restaurant_info: RestaurantInfo):

    try:
      prompt = f"collect restaurant menu and reservation links for {restaurant_info.name}, {restaurant_info.website}, {restaurant_info.location}"
      result = await Runner.run(agent, prompt)
      return json.loads(result.final_output) if result.final_output else {}
    except Exception as e:
        print(f"Error in get_menu_reservation: {e}")
        return {}


