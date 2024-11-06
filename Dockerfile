FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y && apt-get install -y emacs &&\
    apt-get autoremove -y
	
# Install software 
RUN apt-get install -y git

# Copy over private key, and set permissions
# Warning! Anyone who gets their hands on this image will be able
# to retrieve this private key file from the corresponding image layer
RUN echo "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUFNd0FBQUF0emMyZ3RaVwpReU5UVXhPUUFBQUNBeFFxWVBlbUJDVjkyK1R1Y2FoSGgzU3owaENSekVsUHkxayt3VkNWOForUUFBQUpobU9NQU5aampBCkRRQUFBQXR6YzJndFpXUXlOVFV4T1FBQUFDQXhRcVlQZW1CQ1Y5MitUdWNhaEhoM1N6MGhDUnpFbFB5MWsrd1ZDVjhaK1EKQUFBRUJCcEJXV3dadzdqeXlsQXczdUtwek9iSnVWM1AzWWI4Y3F1eGdsb21NLzR6RkNwZzk2WUVKWDNiNU81eHFFZUhkTApQU0VKSE1TVS9MV1Q3QlVKWHhuNUFBQUFGVzF5YVd4NVFFUkZVMHRVVDFBdFRGTlNURlpJVVE9PQotLS0tLUVORCBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0K" | openssl base64 -A -d > /root/.ssh/id_ed25519
RUN chmod 700 /root/.ssh/id_ed25519

# Create known_hosts
RUN touch /root/.ssh/known_hosts
# Add bitbuckets key
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

# Clone the conf files into the docker container
RUN git clone git@github.com:ilya12077/randomizer.git
	
	
RUN cp -a ./randomizer/. /etc/randomizer/
RUN rm -r -f ./randomizer/

RUN pip install python-dotenv Flask waitress requests pytz

ENV AM_I_IN_A_DOCKER_CONTAINER Yes
EXPOSE 8881/tcp
CMD ["python", "/etc/randomizer/main.py"]

