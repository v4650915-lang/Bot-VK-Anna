
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('109.73.198.248', username='root', password='gP#1Pz3yXU9FSr')

nginx_conf = '''server {
    server_name tehnologiya-nv.ru www.tehnologiya-nv.ru;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \;
        proxy_set_header Connection \
upgrade\;
        proxy_set_header Host \System.Management.Automation.Internal.Host.InternalHost;
        proxy_cache_bypass \;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/tehnologiya-nv.ru/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/tehnologiya-nv.ru/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if (\System.Management.Automation.Internal.Host.InternalHost = www.tehnologiya-nv.ru) {
        return 301 https://\System.Management.Automation.Internal.Host.InternalHost\;
    } # managed by Certbot

    if (\System.Management.Automation.Internal.Host.InternalHost = tehnologiya-nv.ru) {
        return 301 https://\System.Management.Automation.Internal.Host.InternalHost\;
    } # managed by Certbot

    listen 80;
    server_name tehnologiya-nv.ru www.tehnologiya-nv.ru;
    return 404; # managed by Certbot
}'''

try:
    print('Writing conf...')
    sftp = ssh.open_sftp()
    with sftp.file('/etc/nginx/sites-available/vkapp', 'w') as f:
        f.write(nginx_conf.replace('\', '').replace('\System.Management.Automation.Internal.Host.InternalHost', 'System.Management.Automation.Internal.Host.InternalHost').replace('\', ''))
    sftp.close()
    
    stdin, stdout, stderr = ssh.exec_command('nginx -t && systemctl restart nginx')
    print('Nginx:', stdout.read().decode(), stderr.read().decode())
    
    print('Testing HTTPs...')
    stdin, stdout, stderr = ssh.exec_command('curl -sI https://tehnologiya-nv.ru')
    print('cURL:', stdout.read().decode())
except Exception as e:
    print('Err:', e)
finally:
    ssh.close()

