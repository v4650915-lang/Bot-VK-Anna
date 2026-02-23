
import paramiko
import sys

nginx_conf = '''server {
    listen 80;
    server_name tehnologiya-nv.ru www.tehnologiya-nv.ru;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade ;
        proxy_set_header Connection \
upgrade\;
        proxy_set_header Host System.Management.Automation.Internal.Host.InternalHost;
        proxy_cache_bypass ;
    }
}'''

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('109.73.198.248', username='root', password='gP#1Pz3yXU9FSr')
    
    sftp = ssh.open_sftp()
    with sftp.file('/etc/nginx/sites-available/vkapp', 'w') as f:
        f.write(nginx_conf)
    sftp.close()

    ssh.exec_command('ln -sf /etc/nginx/sites-available/vkapp /etc/nginx/sites-enabled/')
    ssh.exec_command('rm -f /etc/nginx/sites-enabled/default')
    
    stdin, stdout, stderr = ssh.exec_command('nginx -t && systemctl restart nginx')
    print('Nginx restart stdout:', stdout.read().decode())
    print('Nginx restart stderr:', stderr.read().decode())
    
    print('Installing certbot...')
    stdin, stdout, stderr = ssh.exec_command('apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y certbot python3-certbot-nginx')
    stdout.read()
    
    print('Running certbot...')
    cmd = 'certbot --nginx -d tehnologiya-nv.ru -d www.tehnologiya-nv.ru --non-interactive --agree-tos -m admin@tehnologiya-nv.ru --redirect'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print('Certbot stdout:', stdout.read().decode())
    print('Certbot stderr:', stderr.read().decode())
    
    ssh.close()
except Exception as e:
    print('Error:', e)

