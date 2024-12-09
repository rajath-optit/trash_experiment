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
