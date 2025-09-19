# ADK Program

This program is a tool for finding and updating API calls on GitHub. It can be used to find all instances where an API is used on GitHub and create PRs to make changes to those calls.

## Installation

To install the program, you will need to have Python 3 and pip installed. You can then install the required libraries by running the following command:

```
pip install -r requirements.txt
```

## Usage

To use the program, you will need to have a GitHub personal access token. You can create a personal access token by following the instructions here:

https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

Once you have a personal access token, you will need to add it to the `GITHUB_TOKEN` variable in the `main.py` file.

You can then run the program by running the following command:

```
python main.py "old_api_call" "new_api_call"
```

For example, to replace all instances of the `requests.get()` API call with the `httpx.get()` API call, you would run the following command:

```
python main.py "requests.get" "httpx.get"
```

The program will then search for all instances of the `requests.get()` API call on GitHub and create a pull request to replace it with the `httpx.get()` API call.

## Contributing

Contributions are welcome! Please feel free to submit a pull request with any changes or improvements.
