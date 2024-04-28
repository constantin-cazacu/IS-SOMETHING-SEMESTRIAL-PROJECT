import requests
import click
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GATEWAY_URL = os.environ.get('GATEWAY_URL')


@click.group()
def cli():
    pass


@cli.command()
def list_conversations():
    """List all conversations"""
    response = requests.get(f"{GATEWAY_URL}/conversations/")
    if response.status_code == 200:
        conversations = response.json()
        for conversation in conversations:
            click.echo(f"Conversation ID: {conversation['id']}")


@cli.command()
@click.argument('conversation_id', type=str)
def list_messages(conversation_id):
    """List messages in a conversation"""
    response = requests.get(f"{GATEWAY_URL}/conversations/{conversation_id}/messages/")
    if response.status_code == 200:
        messages = response.json()
        for message in messages:
            click.echo(f"From: {message['sender_id']}, To: {message['recipient_id']}, Content: {message['content']}")


@cli.command()
@click.argument('conversation_id', type=str)
@click.argument('sender_id', type=int)
@click.argument('recipient_id', type=int)
@click.argument('content', type=str)
def send_message(conversation_id, sender_id, recipient_id, content):
    """Send a message to a conversation"""
    payload = {
        "sender_id": sender_id,
        "recipient_id": recipient_id,
        "content": content
    }
    response = requests.post(f"{GATEWAY_URL}/conversations/{conversation_id}/messages/", json=payload)
    if response.status_code == 200:
        click.echo("Message sent successfully.")
    else:
        click.echo("Failed to send message.")


if __name__ == "__main__":
    cli()