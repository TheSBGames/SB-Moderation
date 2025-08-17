# SB Moderation Bot - Production Deployment Guide

## Prerequisites
- Docker and Docker Compose installed
- Domain name (for SSL/TLS)
- At least 2GB RAM
- 20GB storage

## Deployment Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd sb_moderation
```

2. Create and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- DISCORD_TOKEN: Your bot's token
- MONGODB_URI: MongoDB connection string
- SHARD_COUNT: Number of shards (1 per 1000-1500 guilds)

3. Build and start the containers:
```bash
docker-compose up -d
```

4. Monitor the logs:
```bash
docker-compose logs -f bot
```

## Scaling

### Horizontal Scaling
1. Adjust SHARD_COUNT in .env based on guild count
2. Update docker-compose.yml resources as needed
3. Use MongoDB replica set for database scaling

### Vertical Scaling
1. Increase container resources in docker-compose.yml
2. Tune cache settings in .env
3. Optimize MongoDB indexes

## Monitoring

### Metrics Dashboard
1. Access Grafana: http://your-server:3000
2. Default login: admin/admin
3. View bot metrics dashboard

### Logging
- Logs are stored in ./logs/bot.log
- JSON formatted for easy parsing
- Configurable log level in .env

## Backup Procedures

### Database Backup
1. Automated daily backups:
```bash
docker-compose exec mongodb mongodump --out /data/backup/
```

2. Copy backups locally:
```bash
docker cp $(docker-compose ps -q mongodb):/data/backup ./backups
```

### Configuration Backup
1. Regular backups of:
   - .env file
   - docker-compose.yml
   - Custom configurations

## Security

1. Ensure proper permissions:
   - Run bot as non-root user
   - Secure MongoDB access
   - Use strong passwords

2. Network security:
   - Use reverse proxy
   - Enable SSL/TLS
   - Restrict port access

## Maintenance

### Updates
1. Pull latest changes:
```bash
git pull
```

2. Rebuild containers:
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Monitoring
1. Check system resources
2. Monitor error rates
3. Review logs regularly

### Recovery
1. Database restore:
```bash
docker-compose exec mongodb mongorestore /data/backup/
```

2. Bot restart:
```bash
docker-compose restart bot
```

## Troubleshooting

### Common Issues
1. Connection errors:
   - Check MongoDB connection
   - Verify network settings

2. Performance issues:
   - Monitor resource usage
   - Check cache hit rates
   - Review database indexes

3. High memory usage:
   - Adjust cache settings
   - Check for memory leaks
   - Scale resources if needed

## Support
- GitHub Issues: [Repository Issues]
- Discord Support Server: [Invite Link]
