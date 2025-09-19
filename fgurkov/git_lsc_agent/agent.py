from google.adk.agents import Agent
import os
from github import Github

# Get your GitHub Personal Access Token from an environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("Please set the GITHUB_TOKEN environment variable.")

def list_repositories()->dict:
    """
    Retrieves the list of GitHub repositories accessible to the authenticated user.

    Returns:
        dict: A dictionary containing the list of repositories with a 'status' key ('success' or 'error') and a 'repositories' key with the list of repositories if successful, or an 'error_message' if an error occurred.
    """
    try:
        g = Github(GITHUB_TOKEN)
        user = g.get_user()
        repos = user.get_repos()
        repo_names = [repo.name for repo in repos]
        return {
            "status": "success",
            "repositories": repo_names
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)}

# In your main ADK agent file, you would register this tool
# from google.generativeai.adk.main import Agent
# my_agent = Agent(tools=[list_repositories])

# The agent's prompt would then instruct it to use the tool
# "Please list my GitHub repositories."
# When the agent receives this prompt, it will call the list_repositories tool.

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Returns:
        dict: A dictionary containing the weather information with a 'status' key ('success' or 'error') and a 'report' key with the weather details if successful, or an 'error_message' if an error occurred.
    """
    if city.lower() == "new york":
        return {"status": "success",
                "report": "The weather in New York is sunny with a temperature of 25 degrees Celsius (77 degrees Fahrenheit)."}
    else:
        return {"status": "error",
                "error_message": f"Weather information for '{city}' is not available."}

def get_current_time(city:str) -> dict:
    """Returns the current time in a specified city.

    Args:
        dict: A dictionary containing the current time for a specified city information with a 'status' key ('success' or 'error') and a 'report' key with the current time details in a city if successful, or an 'error_message' if an error occurred.
    """
    import datetime
    from zoneinfo import ZoneInfo

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {"status": "error",
                "error_message": f"Sorry, I don't have timezone information for {city}."}

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return {"status": "success",
            "report": f"""The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}"""}

root_agent = Agent(
    name="git_lsc_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions about the time and weather in a city.",
    instruction="I can answer your questions about the time and weather in a city.",
    tools=[get_weather, get_current_time, list_repositories]
)