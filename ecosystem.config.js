module.exports = {
  apps: [
    {
      name: "dsc-backend",
      script: "./start_backend.sh",
      interpreter: "bash",
      env: {
        FLASK_ENV: "production",
        FLASK_APP: "run.py",
        PORT: 5051
      }
    },
    {
      name: "cloudflared-dsc-backend",
      script: "cloudflared",
      args: "tunnel --url localhost:5051",
      interpreter: "none",
      env: {
        NODE_ENV: "production"
      }
    }
  ]
} 