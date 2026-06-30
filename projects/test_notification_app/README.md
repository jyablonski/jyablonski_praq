# Test notification App

Built in both Python & Go to compare each

```sh
go build -o jyablonski_tray_app
sudo mv jyablonski_tray_app /usr/local/bin/

sudo nano /etc/systemd/system/jyablonski_tray_app.service

sudo systemctl daemon-reload
sudo systemctl enable jyablonski_tray_app.service
sudo systemctl start jyablonski_tray_app.service

sudo systemctl status jyablonski_tray_app.service

journalctl -xe
```

[Unit]
Description=jyablonski Tray Application
After=network.target

[Service]
ExecStart=/usr/local/bin/jyablonski_tray_app
Restart=always
User=jacob
Group=jacob
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/jacob/.Xauthority

[Install]
WantedBy=multi-user.target
