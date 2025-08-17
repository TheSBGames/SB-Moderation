# MongoDB Collection Schemas for SB Moderation Bot

## 1. guild_configs
This collection stores configuration settings for each guild.

```json
{
  "_id": 123456789012345678,
  "prefix": "&",
  "log_channel": null,
  "enabled_features": {
     "automod": true,
     "tickets": true,
     "leveling": true
  }
}
```

## 2. automod_settings
This collection contains settings for the auto-moderation features.

```json
{
  "_id": 123456789012345678,
  "enabled": true,
  "anti_links": true,
  "anti_invites": true,
  "anti_badwords": true,
  "badwords": ["badword1", "badword2"],
  "bypass_roles": [9876543210],
  "action": { "type": "timeout", "duration_minutes": 30 },
  "log_channel": null
}
```

## 3. ticket_configs
This collection manages ticket panel configurations for each guild.

```json
{
  "_id": 123456789012345678,
  "ticketPanel": {
    "title": "Support",
    "description": "Open a ticket",
    "button_label": "Create Ticket",
    "button_style": 1,
    "categories": [98765, 87654],
    "manager_roles": [12345]
  },
  "panel_channel": 111222333444,
  "panel_message": 555666777888,
  "log_channel": null
}
```

## 4. noprefix_users
This collection tracks users who have access to no-prefix commands.

```json
{
  "_id": 777888999000111222,
  "added_by": 1186506712040099850,
  "added_at": "2025-08-17T12:00:00Z",
  "expires_at": null
}
```

## 5. levels
This collection stores leveling information for users.

```json
{
  "_id": 444555666777888999,
  "xp": 1234,
  "level": 10,
  "last_message": "2025-08-17T12:00:00Z"
}
```

## 6. yt_subscriptions
This collection manages YouTube feed subscriptions for each guild.

```json
{
  "_id": 123456789012345678,
  "feeds": [
    {"channel_id": "UCxxx", "webhook_channel": 111222333, "last": "2025-08-10T12:00:00Z"}
  ]
}
```

## 7. modmail_threads
This optional collection tracks modmail threads.

```json
{
  "_id": "dm-userid-guildid",
  "user_id": 9876543210,
  "guild_id": 1234567890,
  "thread_channel_id": 111222333,
  "status": "open",
  "created_at": "2025-08-17T12:00:00Z"
}
```