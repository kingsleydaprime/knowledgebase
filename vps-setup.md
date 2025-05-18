# VPS DEPLOYMENT (Using linux base system and linux vps)

## Steps

- Buy VPS (Contabo, Digital Ocean, Linode)
- Point your domain A record to the ip address (A | @ | vps-ip)
- Create an ssh key
```sh
ssh-keygen
```
### Add the public key to the **vps provider** (not the vps)

### Login to the vps 
```sh
ssh root@ip-address
# (root is usually the first and only user)
``` 
### Update the system 
```sh
apt update & apt upgrade -y
```
- Create a non-root user as it is not advisable to use root

```sh
adduser --gecos "" username
```
> (The –gecos is to bypass having to type more information)

- Make the user a sudo user
```bash
usermod -aG sudo username
``` 


Allow the user to be able to login with the same ssh key as root.
```
mkdir /home/username/.ssh
cp ~/.ssh/authorized_keys /home/username/.ssh/
chown -R username:username /home/username/.ssh
chmod 700 /home/username/.ssh
chmod 600 /home/username/.ssh/authorized_keys
```
OR on your local machine
```
ssh-copy-id username@ip-address
```

### Switch to this user using 
```sh
su - username
```

Test to see if the user is sudo 
```sh
sudo ls /
```

## Start SSH Hardening the VPS

### Install docker

Just follow the instructions to install docker

### Allow the running of docker commands without sudo

```sh
sudo usermod -aG docker username 
# (So you don’t have to type sudo docker all the time)
```

> You can harden VPS by doing the following:
Hardening from SSH Attacks (Especially password brute forces)

1. Remove password authentication on ssh (make sure you can login with ssh for the created user as seen above)
2. Open this file 
```sh
sudo nvim /etc/ssh/sshd_config
```
3. Look for this line 

```sshd_config
#PasswordAuthentication yes, 

uncomment it and change the yes to no
```
4. Change 
```
PermitRootLogin yes to no
```
5. Change 
```
UsePAM yes to no
```

## Setting up traefik as a reverse proxy

- Create a folder `/home/username/traefik`
- Make a `compose.yml` file (For docker compose)
- Add a network e.g. traefik-network and set external=true (Because of the other services you will connect)
- Make a traefik.yml file as well for configuring traefik
- Make an acme.json (we are using letsencrypt and acme for ssl encryption)
- Start traefik service docker compose up -d

## Setting up the CI/CD pipeline with github actions
Create SSH key-pair for vps access 

```sh
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions
```

Add the public key to the authorized_keys
```sh
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
```
Copy public key to vps Copy the private key 

```sh
cat ~/.ssh/github_actions | xclip -selection clipboard
```
> Add it as a secret and remember the name… Go to settings, secrets, actions …

Add the key to the repo secrets

Create a workflow `.github/workflows/deploy.yml` (for example)

The deploy should contain steps to build and deploy to the vps

## Setting up the firewall
- `sudo ufw status` should be inactive if doing it for the first time
- `sudo ufw allow 80`
- `sudo ufw allow 443`
- `sudo ufw allow 22` for openssh communication
- `sudo ufw default deny incoming`
- `sudo ufw default allow outgoing`
- `sudo ufw enable`
- `sudo ufw status`

> Just incase you want to allow only specific ips like the ip of your personal computer (do 10 and 11), 

> `sudo ufw allow from <your-ip> to any port 22`

> `sudo ufw delete allow 22`

- To add ratelimiting to the ssh to prevent brute force: `sudo ufw limit 22`

## Setting up monitoring and logging (Grafana, Prometheus, Loki)

- Create a monitoring directory
- On the vps server/terminal type `docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions` to install the loki plugin

- Loki for logs
- Prometheus for checking details
- Grafana for visualization

> In the monitoring directory, create a compose file and add it to the traefik-network since we will need a general network for everything

> Add the images to the compose file (grafana, prometheus, loki, redis-exporter, node-exporter, mongodb-exporter etc)

## Docker commands used
- docker ps to list containers
- docker images to list images
- docker network inspect network-name
- docker network create new-network-name
- docker compose up -d –build -d flag for detached –build to build it
- docker compose build
- docker compose -f compose.file.yml up to use a specific file with -f
- docker plugin ls to list plugins
