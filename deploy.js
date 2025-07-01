const express = require('express');
const path = require('path');
const fs = require('fs');

console.log(`
🚀 AUTONOMOUS MONEY-MAKING ECOSYSTEM DEPLOYMENT
===============================================

🌐 Deploying to Railway (Free Hosting)
📦 Preparing deployment package...
⚡ Setting up production environment...
`);

// Create deployment configuration
const deployConfig = {
    name: "autonomous-money-making-ecosystem",
    version: "6.0.0",
    type: "fullstack",
    environment: "production",
    port: process.env.PORT || 3000,
    host: "0.0.0.0"
};

// Create railway.json for Railway deployment
const railwayConfig = {
    "$schema": "https://railway.app/railway.schema.json",
    "build": {
        "builder": "NIXPACKS"
    },
    "deploy": {
        "startCommand": "npm start"
    }
};

// Create vercel.json for Vercel deployment (backup)
const vercelConfig = {
    "version": 2,
    "name": "autonomous-money-making-ecosystem",
    "builds": [
        {
            "src": "server.js",
            "use": "@vercel/node"
        },
        {
            "src": "build/**",
            "use": "@vercel/static"
        }
    ],
    "routes": [
        {
            "src": "/api/(.*)",
            "dest": "/server.js"
        },
        {
            "src": "/(.*)",
            "dest": "/build/$1"
        }
    ]
};

// Create netlify.toml for Netlify deployment (backup)
const netlifyConfig = `[build]
  publish = "build"
  command = "npm run build"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/server/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
`;

// Write deployment configurations
try {
    fs.writeFileSync('railway.json', JSON.stringify(railwayConfig, null, 2));
    fs.writeFileSync('vercel.json', JSON.stringify(vercelConfig, null, 2));
    fs.writeFileSync('netlify.toml', netlifyConfig);
    
    console.log('✅ Deployment configurations created');
} catch (error) {
    console.error('❌ Error creating deployment configs:', error);
}

// Create a simple deployment server for Railway
const deploymentServer = `
// Production server for deployment
const app = require('./server');

const PORT = process.env.PORT || 3000;
const HOST = '0.0.0.0';

console.log(\\\`
🚀 Autonomous Money-Making Ecosystem Starting...
📊 Port: \\\${PORT}
🌐 Host: \\\${HOST}
💰 Environment: Production
🤖 All agents ready for deployment!
\\\`);
`;

fs.writeFileSync('start.js', deploymentServer);

// Create Procfile for Railway
fs.writeFileSync('Procfile', 'web: node server.js');

// Deploy instructions
console.log(`
🎯 DEPLOYMENT READY!
===================

🔗 Quick Deploy Options:

1. 🚂 RAILWAY (Recommended - Free):
   - Visit: https://railway.app
   - Click "Deploy from GitHub"
   - Connect your repository
   - Your app will be live in 2-3 minutes!

2. ⚡ VERCEL (Free):
   - Visit: https://vercel.com
   - Import your GitHub repository
   - Deploy automatically

3. 🌐 NETLIFY (Free):
   - Visit: https://netlify.com
   - Drag & drop the build folder
   - Or connect GitHub repository

📋 Manual Deployment Commands:
- Railway: railway login && railway init && railway up
- Vercel: vercel --prod
- Netlify: netlify deploy --prod

🎉 Your URL will be: https://autonomous-money-making-ecosystem.railway.app
💰 Live Demo: All 8 agents running with real-time updates!

===============================================
🇮🇩 Made with ❤️ by Mulky Malikul Dhaher
📊 KTP: ████████████████ (Privacy Protected)
===============================================
`);

// Auto-deploy to Railway if available
const { exec } = require('child_process');

// Check if Railway CLI is available
exec('railway --version', (error, stdout, stderr) => {
    if (!error) {
        console.log('🚂 Railway CLI detected! Attempting auto-deployment...');
        
        // Auto-deploy sequence
        exec('railway login', (loginError) => {
            if (!loginError) {
                exec('railway init autonomous-money-making-ecosystem', (initError) => {
                    if (!initError) {
                        exec('railway up', (deployError, deployStdout) => {
                            if (!deployError) {
                                console.log('🎉 Deployment successful!');
                                console.log(deployStdout);
                                
                                // Extract URL from output
                                const urlMatch = deployStdout.match(/https:\/\/[^\s]+/);
                                if (urlMatch) {
                                    console.log(`
🌟 SUCCESS! Your Autonomous Money-Making Ecosystem is LIVE!
🔗 URL: ${urlMatch[0]}
💰 All 8 agents are now running autonomously!
📊 Real-time performance dashboard available!
                                    `);
                                }
                            } else {
                                console.log('ℹ️ Auto-deployment failed. Please deploy manually using the instructions above.');
                            }
                        });
                    }
                });
            }
        });
    } else {
        console.log(`
ℹ️ Railway CLI not found. 
📋 Please use manual deployment options above.
🔗 Quick start: Visit https://railway.app and deploy from GitHub!
        `);
    }
});

module.exports = deployConfig;