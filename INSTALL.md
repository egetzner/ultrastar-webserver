# UltraStar Web Server
## Run at starup

1. `sudo nano /etc/systemd/system/ultrastar-webserver.service`
2. In the editor, add the following content:

    ```
    [Unit]
    Description=UltraStar Webserver
    
    [Service]
    WorkingDirectory=/path/to/ultrastardx/ultrastar-webserver
    ExecStart=/path/to/poetry run flask run
    Restart=always
    User=your_username
    Environment=HOME=/home/your_username
    
    [Install]
    WantedBy=default.target
    ```

3. enable and start the service:

    ```
    sudo systemctl enable ultrastar-webserver.service
    sudo systemctl start ultrastar-webserver.service
    ```