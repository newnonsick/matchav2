# Matcha Bot

Matcha Bot is a versatile Discord bot designed to streamline daily stand-up processes and manage leave requests for teams. It integrates with Supabase for data storage, Google Gemini for natural language processing, and provides robust reporting capabilities, including email delivery of reports.

## Features

### Stand-Up Management

*   **Automated Tracking:** Automatically tracks stand-up messages in designated channels, extracting relevant information.
*   **Daily Summaries:** Sends daily stand-up summaries to team channels, showing who has submitted their stand-up and who hasn't.
*   **Team Overview:** Provides detailed team overviews for specific dates, including stand-up status and leave information.
*   **Member Management:** Allows adding and removing members from stand-up tracking within a specific channel.
*   **Stand-Up Reports:** Generates comprehensive Excel reports of user stand-ups for a given month, with options to specify users or channels, and send via email or Discord DM.
*   **Personal Stand-Up Check:** Allows users to check their own monthly stand-up submission status, including days they were on leave.

### Leave Management

*   **Automated Tracking:** Automatically identifies and records leave requests from messages using natural language processing (Google Gemini AI).
*   **Leave Confirmation:** Sends private confirmation messages to users upon successful leave request submission or edit.
*   **Leave Deletion Handling:** Automatically removes leave records when the original request message is deleted.
*   **Daily Leave Summaries:** Sends daily summaries of all recorded leaves to a designated channel and updates it in real-time as new leaves are tracked or deleted for the current day.

### General Utilities

*   **Announcements:** Allows privileged users to send announcements to multiple stand-up channels with optional attachments.
*   **Command Syncing:** Automatically syncs slash commands to Discord upon bot readiness.

## Project Structure

```
.github/
├── config.py             # Configuration variables (API keys, channel IDs, etc.)
├── datacache.py          # Caches dynamic data like stand-up channels to reduce DB calls
├── main.py               # Main bot entry point and cog loader
├── requirements.txt      # Python dependencies
├── cogs/
│   ├── client_event/     # Discord gateway event listeners
│   │   ├── gateway_event.py
│   │   ├── members_events.py
│   │   └── messages_events.py
│   ├── cronjob/          # Scheduled tasks
│   │   └── daily_summary.py
│   ├── prefix_commands/  # Old style prefix commands
│   │   └── announce.py
│   └── slash_commands/   # Discord slash commands
│       ├── add_member.py
│       ├── check_standup.py
│       ├── help.py
│       ├── leave_summary.py
│       ├── register.py
│       ├── remove_user.py
│       ├── standup_report.py
│       ├── team.py
│       └── track.py
├── core/
│   └── custom_bot.py     # Custom Bot class extending discord.ext.commands.Bot with services/repositories
├── db/
│   ├── migations/        # SQL migration scripts for Supabase
│   │   ├── 0.sql         # Initial schema setup
│   │   ├── 1.sql         # Function to get attendance by date and channel
│   │   └── 2.sql         # Function to get attendance by date across teams
│   └── supabase.py       # Supabase client initialization and connection
├── repositories/         # Data access layer for Supabase
│   ├── leave_repository.py
│   ├── member_repository.py
│   └── standup_repository.py
├── services/             # Business logic and external API interactions
│   ├── email_service.py
│   ├── gemini_service.py
│   ├── leave_service.py
│   ├── member_service.py
│   ├── standup_report_generator.py
│   └── standup_service.py
├── utils/                # Utility functions
│   ├── datetime_utils.py
│   ├── email_utils.py
│   ├── file_utils.py
│   ├── message_utils.py
│   ├── standup_utils.py
│   └── string_utils.py
└── views/                # Discord UI views for interactive components
    ├── announce_confirmation_view.py
    ├── delete_message_view.py
    └── help_view.py
```

## Setup

### Prerequisites

*   Python 3.13+
*   Discord Bot Token
*   Supabase Project URL and Key
*   Google Gemini API Key
*   SMTP Server details for email functionality

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/newnonsick/matchav2.git
    cd matchav2
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    Create a `.env` file in the root directory of your project and populate it with your credentials. Refer to `.env.example` for required variables.

    ```env
    BOT_TOKEN="YOUR_DISCORD_BOT_TOKEN"
    SUPABASE_URL="YOUR_SUPABASE_URL"
    SUPABASE_KEY="YOUR_SUPABASE_SERVICE_ROLE_KEY"
    ATTENDANCE_TRAINEE_CHANNEL_ID="YOUR_TRAINEE_ATTENDANCE_CHANNEL_ID"
    ATTENDANCE_EMPLOYEE_CHANNEL_ID="YOUR_EMPLOYEE_ATTENDANCE_CHANNEL_ID"
    LEAVE_SUMMARY_CHANNEL_ID="YOUR_LEAVE_SUMMARY_CHANNEL_ID"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

    SMTP_SERVER="YOUR_SMTP_SERVER_ADDRESS"
    SMTP_PORT="YOUR_SMTP_PORT" # e.g., 465 for SSL (Suport only 465)
    SMTP_USERNAME="YOUR_SMTP_USERNAME"
    SMTP_PASSWORD="YOUR_SMTP_PASSWORD"
    ```

5.  **Supabase Database Setup:**
    Execute the SQL migration scripts located in `db/migations/` in your Supabase project to set up the necessary tables and functions (`0.sql`, `1.sql`, `2.sql`).

### Running the Bot

```bash
python main.py
```

## Usage

### Stand-Up Commands

*   `/register`: Registers the current channel as a stand-up channel.
*   `/add_member <user>`: Adds a member to the current stand-up channel.
*   `/remove_user <user|user_id>`: Removes a member from the current stand-up channel.
*   `/team [date]`: Displays the stand-up status for the team in the current channel for a specified date (defaults to today).
*   `/track <message_id>`: Manually tracks a stand-up message if it was missed by the automatic tracking.
*   `/standup_report <month> [to_email] [user] [team_channel]`: Generates a stand-up report for a given month. Can specify a user or a team channel, and send the report via email or DM.
*   `/check_standup [month]`: Allows a user to check their own monthly stand-up submission status, including days they were on leave.

### Leave Commands

*   Leave requests are automatically tracked when messages are sent in designated attendance channels. The bot will analyze the message content using Google Gemini AI to extract leave details.
*   `/leave_summary [date]`: Displays a summary of all leaves recorded for a specific date (defaults to today).

### Admin Commands

*   `!announce [message] [attachments]`: Sends an announcement to all registered stand-up channels. (Prefix command)

## Development

### Adding New Cogs

To add new commands or event listeners:

1.  Create a new `.py` file in the appropriate `cogs/` subfolder (e.g., `cogs/slash_commands/` or `cogs/client_event/`).
2.  Define your `commands.Cog` subclass.
3.  Implement the `setup` function at the end of the file:
    ```python
    async def setup(client: CustomBot):
        await client.add_cog(YourCogName(client))
    ```
    The `main.py` will automatically load new cogs from these folders.

### Database Migrations

When making changes to the database schema, create new `.sql` files in `db/migations/` with incremental numbering (e.g., `3.sql`, `4.sql`).

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
