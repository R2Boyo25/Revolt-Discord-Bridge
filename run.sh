if [ "$(dpkg-query -W -f='${Version}' python3-venv)" == "" ]; then
    echo "python3-venv not found - installing it with apt"
    sudo apt install python3-venv
fi
if [ ! -f requirements.txt ]; then
    echo "Cd to dir containing project files!"
else
    if [ ! -f .env ]; then
        echo ".env does not exist - making it with unfilled values"
        echo "discord=TOKEN" > .env
        echo "revolt=TOKEN" >> .env
        echo "revoltserver=ID" >> .env
        echo "discordguild=ID" >> .env
    else
        if [ ! -f map.json ]; then
            echo "map.json does not exist - making it blank"
            echo "{}" > map.json
        else
            if [ ! -d venv ]; then
                python3 -m venv venv
            fi
            source venv/bin/activate
            if [ ! -d venv/lib/python3.9/site-packages/discord ]; then
                pip3 install -r requirements.txt
            fi
            python3 main.py
        fi
    fi
fi
