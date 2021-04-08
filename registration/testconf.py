import configparser 

config = configparser.ConfigParser()
config.read("config.ini")


EMAIL_HOST_USER = config['email_host_server']['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = config['email_host_server']['EMAIL_HOST_PASSWORD']