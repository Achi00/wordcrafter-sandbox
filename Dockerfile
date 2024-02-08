# Use an official Node.js runtime as a base image
FROM node:14

# Set the working directory in the container
WORKDIR /sandbox

# No need to install dependencies unless your JS code requires them
# RUN npm install some-package

# No CMD needed as we will use this container dynamically
