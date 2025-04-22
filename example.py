from agents import Agent, Runner, set_default_openai_key, gen_trace_id, trace, WebSearchTool
from agents.mcp import MCPServer, MCPServerStdio
from agents.model_settings import ModelSettings
import asyncio
import shutil
import json
import os
from dotenv import load_dotenv

load_dotenv()

set_default_openai_key(
    os.getenv("OPENAI_KEY")
)

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

instructions="""
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


async def run(mcp_server: MCPServer):

    await mcp_server.connect()
    # Define the agent
    agent = Agent(
        name="RestaurantLinkFinder",
        instructions=instructions,
        model="gpt-4o-mini",
        tools=[WebSearchTool()],
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
        cache_tools_list=True
    )


                # Format input into a string prompt
    prompt = f"collect restaurant menu and reservation links for {restaurant_input["name"]}, {restaurant_input["website"]}, {restaurant_input["location"]} " 
    result = await Runner.run(agent, prompt)

    print("Model Output:\n", result.final_output)

    await mcp_server.cleanup()


async def main():
    async with MCPServerStdio(
        name="Playwright MCP Server",
        params={"command": "npx", "args": ["@playwright/mcp@latest", "--headless"]},
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="Exodus Restaurant Scraper", trace_id=trace_id):
            print(
                f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n"
            )

            await run(server)

            # OPTIONAL: If you want to call the MCP scraping instructions here, parse result.final_output and act on it


if not shutil.which("npx"):
    print(
        "Please install npx to run this example. You can do this by running 'npm install -g npx'."
    )
else:
    asyncio.run(main())
