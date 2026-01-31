# Use the stable alpine version for a small footprint
FROM nginx:stable-alpine

# COPY [source on laptop] [destination in image]
# The '.' means "copy everything in the current folder"
COPY . /usr/share/nginx/html

# Document that the service listens on port 80
EXPOSE 80