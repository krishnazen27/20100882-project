# 20100882-project
 PROGRAMMING FOR INFORMATION SYSTEMS Semester Repository

 This Project is all about a local Dublin Classified Market place application. This allow users to browse listing , post ads and manage the items listed.

1) ubuntu server configuration:

        GCP server configurations:

            Instance name: instance-2010xxxx-app
            instance type: 2 vCPU + 4 GB memory
            OS : Ubuntu 24.04 LTS Minimal
            Ports: allow HTTPS, HTTP, Custom port as needed by application
            External IP address
            custom ssh key to login to server 

2) Configuration to Run application in ubuntu server
        referance: https://medium.com/@mynameischandangupta1/how-to-install-flask-on-ubuntu-84bce8419dc0

                sudo apt update && apt upgrade -y
                sudo apt-get install python3-pip
                apt install python3.12-venv
                #enter in to project folder and execute below commands
                python3 -m venv venv
                source venv/bin/activate
                pip3 install Flask
                sudo apt install vim
                vi app.py  and then updaet sample code from the above url
                python3 app.py

                Open a web browser and go to http://ubuntu-externalIP:5000. You should see “Hello, World!” displayed.
                ![Hello World Page](images/sample-helloworld.png)