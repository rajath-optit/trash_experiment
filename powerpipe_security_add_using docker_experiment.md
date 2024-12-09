# worked
Here’s a step-by-step **README** to help you replicate the process next time. It includes instructions for setting up Nginx with SSL, configuring a reverse proxy, enabling/disabling basic authentication, and testing the configuration.

---

## **README: Setting Up Nginx with SSL, Reverse Proxy, and Basic Authentication**

### **Prerequisites**
- Nginx installed on your server
- SSL certificate (self-signed or from a CA)
- Web application (e.g., Powerpipe) running on specific ports
- (Optional) `.htpasswd` file for basic authentication

---

### **1. Install Nginx**
If Nginx is not already installed, install it using:

```bash
sudo apt update
sudo apt install nginx
```

### **2. Create SSL Certificates (Self-Signed)**
If you don’t already have SSL certificates, you can create a self-signed certificate for testing purposes:

```bash
sudo mkdir /etc/nginx/ssl
sudo openssl req -x509 -newkey rsa:4096 -keyout /etc/nginx/ssl/selfsigned.key -out /etc/nginx/ssl/selfsigned.crt -days 365
```

This will generate a **self-signed** SSL certificate valid for one year.

### **3. Configure Nginx for SSL and Reverse Proxy**
1. Create a configuration file for your site in `/etc/nginx/sites-available/`. For example, create a file called `powerpipe`:

   ```bash
   sudo nano /etc/nginx/sites-available/powerpipe
   ```

2. Add the following configuration to the file:

   ```nginx
   # HTTPS Configuration (for port 443)
   server {
       listen 443 ssl;
       server_name 10.10.30.93;  # Or use localhost if needed

       # SSL Configuration
       ssl_certificate /etc/nginx/ssl/selfsigned.crt;
       ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
       
       # SSL Protocols & Ciphers for better security
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers 'HIGH:!aNULL:!MD5';

       # Optional Basic Authentication
       # auth_basic "Restricted Area";
       # auth_basic_user_file /etc/nginx/.htpasswd;

       # Proxy settings to forward traffic to your application
       location / {
           proxy_pass http://localhost:9102;  # Forward to your application (replace with correct port)
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

3. Enable the configuration by creating a symbolic link to `/etc/nginx/sites-enabled/`:

   ```bash
   sudo ln -s /etc/nginx/sites-available/powerpipe /etc/nginx/sites-enabled/
   ```

### **4. (Optional) Enable Basic Authentication**
1. Install `apache2-utils` to use the `htpasswd` utility:

   ```bash
   sudo apt install apache2-utils
   ```

2. Create the `.htpasswd` file to store the username and password:

   ```bash
   sudo htpasswd -c /etc/nginx/.htpasswd username
   ```

   Replace `username` with the desired username. You’ll be prompted to set a password.

3. Re-enable Basic Authentication by uncommenting the following lines in the configuration:

   ```nginx
   auth_basic "Restricted Area";
   auth_basic_user_file /etc/nginx/.htpasswd;
   ```

### **5. Test Nginx Configuration**
Before restarting Nginx, always test the configuration to make sure there are no syntax errors:

```bash
sudo nginx -t
```

You should see `syntax is ok` and `test is successful` if there are no errors.

### **6. Restart Nginx**
Once everything is correctly configured and tested, restart Nginx to apply the changes:

```bash
sudo systemctl restart nginx
```

### **7. (Optional) Disable Basic Authentication**
If you no longer want Basic Authentication enabled, simply:

1. Open the Nginx configuration file:

   ```bash
   sudo nano /etc/nginx/sites-available/powerpipe
   ```

2. Comment out or remove the `auth_basic` lines:

   ```nginx
   # auth_basic "Restricted Area";
   # auth_basic_user_file /etc/nginx/.htpasswd;
   ```

3. Reload Nginx:

   ```bash
   sudo systemctl reload nginx
   ```

### **8. Verify the Setup**
- Open a web browser and go to `https://<your-server-ip-or-domain>`.
- Ensure the page is served over HTTPS.
- If Basic Authentication is enabled, it will ask for a username and password.
- If everything works as expected, your reverse proxy should be functioning.

---

### **Troubleshooting**
1. **Nginx not restarting**:
   If Nginx fails to restart, check the error logs for more details:
   ```bash
   sudo journalctl -xeu nginx
   ```

2. **SSL errors**:
   If you encounter SSL issues, check the certificate file and paths. Ensure they are correctly specified in your configuration:
   ```nginx
   ssl_certificate /etc/nginx/ssl/selfsigned.crt;
   ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
   ```

3. **Basic Authentication issues**:
   If you're getting a 401 error or authentication prompt, ensure the `.htpasswd` file is correctly created and referenced in the Nginx config.

4. **Testing SSL**:
   You can check SSL connectivity and configuration using tools like [SSL Labs' SSL Test](https://www.ssllabs.com/ssltest/).

---

### **Summary of Key Nginx Commands**
- **Test Nginx configuration**: `sudo nginx -t`
- **Restart Nginx**: `sudo systemctl restart nginx`
- **Reload Nginx**: `sudo systemctl reload nginx`
- **Enable site configuration**: `sudo ln -s /etc/nginx/sites-available/powerpipe /etc/nginx/sites-enabled/`
- **Disable site configuration**: `sudo rm /etc/nginx/sites-enabled/powerpipe`
- **Start Nginx**: `sudo systemctl start nginx`
- **Stop Nginx**: `sudo systemctl stop nginx`

---

This guide should cover all the steps you need to set up SSL, reverse proxy, and basic authentication with Nginx, along with how to disable authentication when needed.

--------------------------------------------------------

------------------------------------------------------------------
Here's the requested guide organized with all steps and commands in one place, along with a folder structure suggestion for experimenting:

---

### **Folder Structure for Experimentation**

Create a dedicated folder to store all necessary files and configurations for this setup:

```plaintext
powerpipe-experiment/
│
├── Dockerfile          # The Dockerfile for building the image
├── README.md           # Documentation for setup (this guide)
├── scripts/
│   ├── init.sh         # Optional: Script for initializing mods
│   ├── start.sh        # Optional: Script for starting services
├── logs/               # Directory for log files (mount to container)
├── secrets/            # Directory for securely managing credentials
│   ├── aws_access_key_id  # File for AWS Access Key
│   ├── aws_secret_access_key  # File for AWS Secret Key
```

---

### **1. Dockerfile**
Place the following `Dockerfile` in the root of the `powerpipe-experiment/` folder:

```dockerfile
# Use Ubuntu as the base image
FROM ubuntu:latest

# Install dependencies
RUN apt-get update && \
    apt-get install -y curl tar && \
    groupadd -g 1001 powerpipe && \
    useradd -u 1001 --create-home --shell /bin/bash --gid powerpipe powerpipe

# Environment variables
ENV USER_NAME=powerpipe
ENV GROUP_NAME=powerpipe
ENV POWERPIPE_TELEMETRY=none

# Set working directory
WORKDIR /home/$USER_NAME

# Install Powerpipe
RUN curl -LO https://github.com/turbot/powerpipe/releases/download/v0.3.1/powerpipe.linux.amd64.tar.gz && \
    tar xvzf powerpipe.linux.amd64.tar.gz && \
    mv powerpipe /usr/local/bin/powerpipe && \
    rm -rf powerpipe.linux.amd64.tar.gz

# Install Steampipe
RUN curl -LO https://steampipe.io/install/steampipe.sh && \
    sh steampipe.sh && \
    rm -f steampipe.sh

# Switch to the non-root user
USER powerpipe

# Install AWS plugin for Steampipe as the non-root user
RUN steampipe plugin install aws

# Default command
ENTRYPOINT ["/bin/bash", "-c", "mkdir -p /home/powerpipe/mod && cd /home/powerpipe/mod && powerpipe mod init && powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance && steampipe service start && powerpipe server"]
```

---

### **2. Building the Docker Image**
Build the Docker image from the `Dockerfile`:

```bash
cd powerpipe-experiment/
sudo docker build -t pp-sp-img .
```

---

### **3. Create Docker Network**
Create a network to allow communication between containers if needed:

```bash
sudo docker network create vested-network
```

---

### **4. Create Secrets**
Store AWS credentials securely in the `secrets/` directory:

1. **Create the directory**:
   ```bash
   mkdir -p secrets
   ```

2. **Add credentials**:
   Save the AWS credentials in `aws_access_key_id` and `aws_secret_access_key`:
   ```bash
   echo "YOUR_AWS_ACCESS_KEY_ID" > secrets/aws_access_key_id
   echo "YOUR_AWS_SECRET_ACCESS_KEY" > secrets/aws_secret_access_key
   ```

---

### **5. Run the Container**
Run the container, mapping ports and using mounted volumes for logs and secrets:

```bash
sudo docker run -d --name vested-pp-sp-container-3 \
  --network vested-network \
  -p 9024:9024 \
  -p 9125:9125 \
  -e AWS_ACCESS_KEY_ID=$(cat secrets/aws_access_key_id) \
  -e AWS_SECRET_ACCESS_KEY=$(cat secrets/aws_secret_access_key) \
  -e AWS_REGION=ap-south-1 \
  -v $(pwd)/logs:/home/powerpipe/mod \
  pp-sp-img
```

---

### **6. Initialize and Install Mods**
Access the running container and execute commands to initialize and install mods:

```bash
sudo docker exec -it vested-pp-sp-container-3 /bin/bash

# Inside the container
mkdir -p /home/powerpipe/mod
cd /home/powerpipe/mod
powerpipe mod init
powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance
powerpipe mod install github.com/turbot/steampipe-mod-aws-insights
powerpipe mod install github.com/turbot/steampipe-mod-aws-well-architected
powerpipe mod install github.com/turbot/steampipe-mod-aws-top-10
powerpipe mod install github.com/turbot/steampipe-mod-aws-thrifty
```

---

### **7. Start Services**
Run the following commands inside the container to start the services:

```bash
nohup steampipe service start --port 9024 > /home/powerpipe/mod/steampipe.log 2>&1 &
nohup powerpipe server --port 9125 > /home/powerpipe/mod/powerpipe.log 2>&1 &
```

---

### **8. Monitor Logs**
View the logs using:

```bash
tail -f /home/powerpipe/mod/steampipe.log
tail -f /home/powerpipe/mod/powerpipe.log
```

---

### **9. Secure the Setup**

#### **Add NGINX Reverse Proxy**
Configure NGINX as a reverse proxy to protect the service with authentication. Use the steps provided earlier to set up basic auth and HTTPS.

---

### **10. Cleanup**
To stop and remove the container and network:

```bash
sudo docker stop vested-pp-sp-container-3
sudo docker rm vested-pp-sp-container-3
sudo docker network rm vested-network
```

To remove the image:

```bash
sudo docker rmi pp-sp-img
```

---

This setup provides a sandbox for experimentation while maintaining flexibility and security. You can now explore and test Powerpipe and Steampipe with an organized workflow!
