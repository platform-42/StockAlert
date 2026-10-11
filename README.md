# StockAlert

So this is the project structure.
Unix converions
/etc -> config items
/ops -> operator procedures
/lib -> python program libraries
/cer -> certificates
/ -> main, here are the 2 main programs located


/etc
    /stocks.yml -> stocks that we monitor
    /prod
        /apns.yml -> config file for APNS
        /mongodb.yml -> config file for mongo
        /stock_api.yml -> config file for webserver
/ops/prod 
     /stock_alert.sh -> script to test stock-quote retrieval
     /stock_api.sh -> script to start webserver
/cer -> apple push notification certificate
/lib
    /core
        /utils.py -> utilities
        /tokens.py -> json tokens
        /endpoints.py -> endpoints for iOS application to use
    /mongo
        /payloads.py -> mongo payloads
        /persistence_factory.py -> mongo db connection
        /persistence.py -> mongo db primitives
    /alerts
        /alerts.py -> apns business logic
        /apns_pyapns.py -> apple APNS implementation
        /market.py -> quotes from yfinance package
        /rules.py -> busines rules for alert engine
    /validation
        /validation.py -> basic YAML input validation
/venv -> virtuele python environment
/stock_api.py -> the webserver
/stock_alert.py -> the event publishing software

## EXAMPLES for testing
curl \
-k \
-H "X-API-Key: <api-key>" \
-X GET "http://stockpitalert.com:8100/2026-01/alerts/sector?sector=AI"

# INSTALLATION
1. install python 3.10 or higher
2. install mongodb 7.0 or higher
3. install python packages 
    pip install --upgrade pip
    pip install -r requirements.txt
4. adjust startup scripts for hosting environment
5. add stock_alert to cron, every 5 mins, from 14:00 -> 21:00
6. add stock_api to system daemon for permanent monitoring and auto startup after server reboot