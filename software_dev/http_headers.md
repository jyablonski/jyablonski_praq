# HTTP Headers

HTTP Headers are a list of strings sent & received by client requests and server responses.  They're hidden from end-users and only used by clients & servers.
- Content-Type - Tells the browser how to interpret results.  `text/html; charset=UTF-8` or `application/pdf` etc.
- Request - The Get/Put/Post Request, the URL used for it, and the HTTP Version.
- Cookies - Comma separated key value pairs.
- Referer - The webpage you were sent from if you clicked a URL on there.
- Accept-Language - Default language setting for the user.  If you're french a website might return french characters if it's been designed for that.
- Authorization - Used to provide credentials to authenticate with a server
- Encoding - gzip, deflate.  Most modern browsers support gzip so information will be sent over the internet in a compressed format to save bandwidth and time.
- Connection - `keep-alive` or `close` depending on whether the network connection should stay open after a transaction or close.
- Keep-Alive - Defines settings for the network connection, like how long an idle connection should remain open for or what the max number of requests should be.
- Host - Simple header specifying the host.  if no port is listed, it defaults to 80 or 443 depending on whether it's HTTP or HTTPS
- User Agent - Client Browser & Operating System information.
- Cache - Stuff like `max-age=3600` to specify how long to cache results for to reduce server load and improve load times in the browser.
  - Can also be set to `no-cache`.
- If-Modified-Since - If a web page is already cached in your browser it will compare against this timestamp field to see if you can use the cache again, or retrieve new results.