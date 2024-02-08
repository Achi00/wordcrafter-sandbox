# Use the official Node.js 14 image as the base
FROM node:14

# Set the working directory inside the container to /workspace
WORKDIR /workspace

# (Optional) Install any commonly used packages globally; this step can be skipped if not needed
# RUN npm install -g some-common-package

# Copy the script that will run the user code to the container
COPY run-code.sh /workspace/run-code.sh

# Make the script executable
RUN chmod +x /workspace/run-code.sh

# The script `run-code.sh` will be executed when the container starts (details below)
CMD ["/workspace/run-code.sh"]
