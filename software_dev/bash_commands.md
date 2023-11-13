# Bash

### Examples
``` log
2023-03-27T07:07:57Z	167.114.103.255 - - [27/Mar/2023:07:07:57 +0000] "GET /id/491206950/usa-hits-usa%E3%83%81%E3%83%A3%E3%83%BC%E3%83%88%E3%82%92%E3%82%B2%E3%83%83%E3%83%88.html HTTP/1.1" 200 5228 "-" "Mozilla/5.0 (compatible; MJ12bot/v1.4.8; http://mj12bot.com/)" 0.006 CA
2023-03-27T07:07:55Z	167.114.103.255 - - [27/Mar/2023:07:07:55 +0000] "GET /id/489403218/%E3%83%B6.html HTTP/1.1" 200 5864 "-" "Mozilla/5.0 (compatible; MJ12bot/v1.4.8; http://mj12bot.com/)" 0.005 CA
2023-03-27T07:07:55Z	185.191.171.255 - - [27/Mar/2023:07:07:55 +0000] "GET /a/299749412/alternative-to-electrical-formulator.html HTTP/1.1" 200 9956 "-" "Mozilla/5.0 (compatible; SemrushBot/7~bl; +http://www.semrush.com/bot.html)" 0.080 NL
2023-03-27T07:07:54Z	185.191.171.255 - - [27/Mar/2023:07:07:54 +0000] "GET /a/1455330949/alternative-to-closca-waterrefill-everywhere.html HTTP/1.1" 200 11431 "-" "Mozilla/5.0 (compatible; SemrushBot/7~bl; +http://www.semrush.com/bot.html)" 0.119 NL
2023-03-27T07:07:53Z	167.114.103.255 - - [27/Mar/2023:07:07:53 +0000] "GET /id/1059320420/%E3%81%B5%E3%81%96%E3%81%91%E3%81%9F%E3%81%A4%E3%81%91%E3%82%84%E3%81%8C%E3%81%A3%E3%81%A6.html HTTP/1.1" 200 5372 "-" "Mozilla/5.0 (compatible; MJ12bot/v1.4.8; http://mj12bot.com/)" 0.006 CA

```

``` sh
# wc normally counts the number of lines, number of words, and number of bytes in a file.
# `wc -l logfile.log` will spit out how many lines are in a file and the file itself
# `<` is a redirection operator that only returns how many lines are in the filed
total_rows=$(wc -l < logfile.log)

# `grep " 5[0-9][0-9] " ` searches for lines that contain that specfic pattern
# `|` is a pipe operator so it takes the output of the command on the left
# and uses it as an input for the `wc -l` command on the right
error_rows=$(grep " 5[0-9][0-9] " logfile.log | wc -l)
```