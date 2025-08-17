# SB Moderation Bot

## Overview
SB Moderation is a feature-rich Discord bot built using Python 3.11+ and discord.py 2.3+. It provides a variety of moderation tools, automated moderation features, ticket management, leveling systems, YouTube notifications, and more. The bot is designed to enhance community management and engagement on Discord servers.

## Features
- **Moderation Commands**: Ban, kick, timeout, mute, warn, and manage messages.
- **Automod**: Automatically detects and handles links, invites, and bad words in messages.
- **Ticket Management**: GUI-driven ticket panels for user support and inquiries.
- **ModMail**: Allows users to DM the bot and receive responses from staff.
- **Leveling System**: Tracks user activity and rewards XP and levels.
- **YouTube Notifier**: Subscribes to YouTube channels and posts updates in designated channels.
- **Temporary Voice Channels**: Creates and manages temporary voice channels for users.
- **Music Commands**: Basic scaffolding for music playback commands (Lavalink optional).
- **Utility and Fun Commands**: Includes commands like ping, user info, memes, and more.

## Installation

### Prerequisites
- Python 3.11+
- MongoDB
- Discord Bot Token

### Setup
1. Clone the repository:
   ```
   git clone <repository-url>
   cd sb_moderation
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file from the example:
   ```
   cp .env.example .env
   ```

4. Fill in the `.env` file with your bot token and MongoDB URI.

5. Run the bot:
   ```
   python main.py
   ```

## Usage
- Use the default prefix `&` or slash commands for bot interactions.
- Admin commands are restricted to users with appropriate permissions.
- Users can open tickets through the ticket panel and receive support.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License.

## Acknowledgments
Powered By SB Moderation™