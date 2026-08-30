import os
import re
from dotenv import load_dotenv
load_dotenv()
from llm import ask_ai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.command("/metropolis-ask")
def handle_ask(ack, respond, command):
    ack()
    prompt = command.get("text", "").strip()
    if not prompt:
        respond(
            {
                "response_type": "ephemeral", "text": "Please provide a question. For example, try `/metropolis-ask How do the stars work?`"
            }
        )
        return
    respond({"response_type": "ephemeral", "text": f"*Thinking:* `{prompt}`"})
    try:
        ai_response = ask_ai(prompt)
        respond(
            {
                "response_type": "in_channel", "text": f"*Metropolis AI Response:*\n{ai_response}"
            }
        )
    except Exception as e:
        print(f"LLM Error: {e}")
        respond(
            {
                "response_type": "ephemeral", "text": "Failed to get response from LLM for the requested query"
            }
        )


@app.command("/metropolis-whoami")
def handle_whoami(ack, respond, command, client):
    ack()
    try:
        res = client.users_info(user=command["user_id"])
        user = res["user"]
        profile = user.get("profile", {})
        display_name = profile.get("display_name") or profile.get("real_name")

        respond({"response_type": "ephemeral", "text": f"Sup, {display_name}!"})
    except Exception as e:
        print(f"Error: {e}")


@app.command("/metropolis-scan")
def handle_scan(ack, respond, command, client):
    ack()

    try:
        channel_info = client.conversations_members(
            channel=command["channel_id"]
        )
        channel_members = channel_info.get("members", [])
        channel_count = len(channel_members)
        users_res = client.users_list()
        all_members = users_res.get("members", [])
        human_users = [
            u
            for u in all_members
            if not u.get("deleted")
            and not u.get("is_bot")
            and u.get("id") != "USLACKBOT"
        ]
        bot_users = [
            u
            for u in all_members
            if u.get("is_bot") or u.get("id") == "USLACKBOT"
        ]
        total_humans = len(human_users)
        total_bots = len(bot_users)
        report = (
            " *Metropolis Population Scan*\n"
            f"• *Current Channel:* `{channel_count}`\n"
            f"• *Total Humans:* `{total_humans}`\n"
            f"• *Automated Units (Bots):* `{total_bots}`\n"
            f"• *Total Registered Entities:* `{len(all_members)}`"
        )

        respond({"response_type": "in_channel", "text": report})

    except Exception as e:
        print(f"Scan error: {e}")
        respond(
            {
                "response_type": "in_channel",
                "text": "Scan failed!",
            }
        )


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    print("Metropolis bot is up and running!")
    handler.start()