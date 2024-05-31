import click
import requests

# Replace with your API base URL
BASE_URL = "http://127.0.0.1:8000"
# Variable to store user ID after successful login
user_id = None


@click.group()
def cli():
    pass


def register():
    """Register a new user"""
    username = click.prompt("Enter username")
    password = click.prompt("Enter password", hide_input=True, confirmation_prompt=True)
    url = f"{BASE_URL}/register-user/"
    payload = {"username": username, "password": password}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        click.echo("Registration successful")
    elif response.status_code == 400:
        click.echo("User already registered")
    else:
        click.echo(f"Registration failed: {response.text}")


def login():
    """Login to the social network"""
    global user_id
    username = click.prompt("Enter username")
    password = click.prompt("Enter password", hide_input=True)
    url = f"{BASE_URL}/login/"
    payload = {"username": username, "password": password}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        click.echo("Login successful")
        user_id = response.json().get("user_id")  # Store user ID for future requests
    else:
        click.echo(f"Login failed: {response.text}")


def list_conversations():
    """List conversations for the logged-in user"""
    global user_id
    if user_id is None:
        click.echo("Please login first")
        return
    url = f"{BASE_URL}/conversations/{user_id}"
    response = requests.get(url)
    if response.status_code == 200:
        conversations = response.json()
        click.echo("Conversations:")
        for conversation in conversations:
            click.echo(f"- {conversation['conversation_id']}: {conversation['participant_name']}")
    else:
        click.echo(f"Failed to retrieve conversations: {response.text}")


def list_messages(conversation_id):
    """List messages for a conversation"""
    global user_id
    if user_id is None:
        click.echo("Please login first")
        return
    url = f"{BASE_URL}/get-messages/{conversation_id}"
    response = requests.get(url)
    if response.status_code == 200:
        messages = response.json()
        # print(messages)
        click.echo("Messages:")
        for message in messages:
            click.echo(f"- {message['timestamp']} | {message['sender_name']}: {message['content']}")
    else:
        click.echo(f"Failed to retrieve messages: {response.text}")


def send_message(participant_id, content):
    """Send a message to a user"""
    global user_id
    if user_id is None:
        click.echo("Please login first")
        return
    url = f"{BASE_URL}/send-message/"
    payload = {"user_id": user_id, "participant_id": participant_id, "content": content}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        click.echo("Message sent successfully")
        conversation_id = response.json().get("conversation_id")
        list_messages(conversation_id)  # Retrieve messages after sending a new message
    else:
        click.echo(f"Failed to send message: {response.text}")


def display_menu():
    click.echo("Select an option:")
    click.echo("1. Register")
    click.echo("2. Login")
    click.echo("3. List Conversations")
    click.echo("4. List Messages")
    click.echo("5. Send Message")
    click.echo("6. Exit")


def run_cli():
    while True:
        display_menu()
        choice = click.prompt("Enter your choice", type=int)
        if choice == 1:
            register()
        elif choice == 2:
            login()
        elif choice == 3:
            list_conversations()
        elif choice == 4:
            conversation_id = click.prompt("Enter Conversation ID")
            list_messages(conversation_id)
        elif choice == 5:
            participant_id = click.prompt("Enter Participant ID")
            content = click.prompt("Enter Message Content")
            send_message(participant_id, content)
        elif choice == 6:
            click.echo("Exiting...")
            break
        else:
            click.echo("Invalid choice. Please enter a valid option.")


if __name__ == "__main__":
    run_cli()

# TestUser7
# test12345
