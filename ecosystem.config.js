module.exports = {
  apps: [{
    name: 'safety-companion-api',
    script: 'python3',
    args: 'safety_api_server.py',
    cwd: '/Users/burtonstuff/Desktop/medical-mcp-server',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PORT: 8001  // Different port from TrailMedic to avoid conflicts
    }
  }]
};
