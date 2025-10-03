# Environment Configuration

This project uses environment variables for configuration. Follow these steps to set up your environment:

## Quick Setup

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your actual values:
   ```bash
   # Open in your preferred editor
   code .env  # VS Code
   # or
   notepad .env  # Windows Notepad
   ```

3. **Update the variables** as needed for your setup.

## Environment Files

- **`.env.example`** - Template file with all available variables (committed to git)
- **`.env`** - Your local environment variables (ignored by git)
- **`.env.development`** - Development-specific variables (committed to git)
- **`.env.production`** - Production testing locally with localhost (committed to git)
- **`.env.production.deploy`** - Production deployment with 0.0.0.0 (committed to git)

## Available Scripts

- **`npm run dev`** - Start development server (uses `.env.development`)
- **`npm run start`** - Build and start production server locally (uses `.env.production`)
- **`npm run start:dev`** - Alternative development start command
- **`npm run start:prod`** - Start production server (requires build first)
- **`npm run start:deploy`** - Start server for actual deployment (uses `.env.production.deploy`)
- **`npm run build`** - Build the application for production
- **`npm run preview`** - Build and preview production version locally

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NODE_ENV` | Environment mode | `development` | No |
| `PORT` | Server port | `5000` | No |
| `HOST` | Server host | `localhost` | No |
| `SESSION_SECRET` | Session encryption key | - | Yes |
| `VITE_API_BASE_URL` | Frontend API URL | `http://localhost:5000` | No |
| `APP_NAME` | Application name | `NASA Weather Prediction Portal` | No |
| `DEBUG` | Enable debug logging | `true` | No |
| `LOG_LEVEL` | Logging level | `debug` | No |

## Security Notes

- **Never commit `.env` files** with sensitive data
- **Change `SESSION_SECRET`** in production
- **Update API URLs** for production deployment
- **Use strong secrets** for production environments

## Troubleshooting

If you get environment-related errors:

1. Make sure you have a `.env` file
2. Check that all required variables are set
3. Verify the syntax (no spaces around `=`)
4. Restart the server after changes

## Example `.env` file:
```bash
# Server Configuration
PORT=5000
HOST=localhost
NODE_ENV=development

# Application
APP_NAME="NASA Weather Prediction Portal"
SESSION_SECRET=your_secret_key_here

# Frontend
VITE_API_BASE_URL=http://localhost:5000

# Development
DEBUG=true
LOG_LEVEL=debug
```