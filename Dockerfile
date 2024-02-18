# Use the official Node.js 14 image as the base
FROM node:14

# Set the working directory inside the container to /workspace
WORKDIR /workspace

# Copy the script that will run the user code to the container
COPY run-code.sh /workspace/

# Make the script executable
RUN chmod +x /workspace/run-code.sh
