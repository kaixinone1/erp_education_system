module.exports = {
  apps: [
    {
      name: 'education-backend',
      script: 'D:/erp_thirteen/venv/Scripts/python.exe',
      args: '-m uvicorn main:app --port 8000 --host 127.0.0.1',
      cwd: 'D:/erp_thirteen/tp_education_system/backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'education-frontend',
      script: 'D:/Program Files/nodejs/npm.cmd',
      args: 'run dev',
      cwd: 'D:/erp_thirteen/tp_education_system/frontend',
      instances: 1,
      autorestart: true,
      watch: false
    }
  ]
}
