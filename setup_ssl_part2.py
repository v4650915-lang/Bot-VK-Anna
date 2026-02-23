
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('109.73.198.248', username='root', password='gP#1Pz3yXU9FSr')
try:
    print('Installing certbot...')
    stdin, stdout, stderr = ssh.exec_command('apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y certbot python3-certbot-nginx')
    print('wait for install..')
    stdout.channel.recv_exit_status() # wait finish
    print('Install OK')
    
    print('Running certbot...')
    cmd = 'certbot --nginx -d tehnologiya-nv.ru -d www.tehnologiya-nv.ru --non-interactive --agree-tos -m admin@tehnologiya-nv.ru --redirect'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    print('Certbot stdout:', stdout.read().decode())
    print('Certbot stderr:', stderr.read().decode())
finally:
    ssh.close()

