2026-07-24T01:13:10.201Z django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
2026-07-24T01:13:10.217Z WARNING 2026-07-24 01:13:10,217 log Bad Request: /api/health/
2026-07-24T01:13:10.218Z 127.0.0.1 - - [24/Jul/2026:01:13:10 +0000] "GET /api/health/ HTTP/1.0" 400 143 "-" "curl/8.14.1"
2026-07-24T01:13:15.311Z ERROR 2026-07-24 01:13:15,310 exception Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
2026-07-24T01:13:15.311Z Traceback (most recent call last):
2026-07-24T01:13:15.311Z File "/usr/local/lib/python3.11/site-packages/django/core/handlers/exception.py", line 55, in inner
2026-07-24T01:13:15.311Z response = get_response(request)
2026-07-24T01:13:15.311Z ^^^^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:15.311Z File "/usr/local/lib/python3.11/site-packages/django/utils/deprecation.py", line 133, in __call__
2026-07-24T01:13:15.311Z response = self.process_request(request)
2026-07-24T01:13:15.311Z ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:15.311Z File "/usr/local/lib/python3.11/site-packages/django/middleware/security.py", line 28, in process_request
2026-07-24T01:13:15.311Z host = self.redirect_host or request.get_host()
2026-07-24T01:13:15.311Z ^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:15.311Z File "/usr/local/lib/python3.11/site-packages/django/http/request.py", line 151, in get_host
2026-07-24T01:13:15.311Z raise DisallowedHost(msg)
2026-07-24T01:13:15.311Z django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
2026-07-24T01:13:15.311Z WARNING 2026-07-24 01:13:15,311 log Bad Request: /api/health/
2026-07-24T01:13:15.312Z 127.0.0.1 - - [24/Jul/2026:01:13:15 +0000] "GET /api/health/ HTTP/1.0" 400 143 "-" "curl/8.14.1"
2026-07-24T01:13:20.383Z ERROR 2026-07-24 01:13:20,382 exception Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
2026-07-24T01:13:20.383Z Traceback (most recent call last):
2026-07-24T01:13:20.383Z File "/usr/local/lib/python3.11/site-packages/django/core/handlers/exception.py", line 55, in inner
2026-07-24T01:13:20.383Z response = get_response(request)
2026-07-24T01:13:20.383Z ^^^^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:20.383Z File "/usr/local/lib/python3.11/site-packages/django/utils/deprecation.py", line 133, in __call__
2026-07-24T01:13:20.383Z response = self.process_request(request)
2026-07-24T01:13:20.383Z ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:20.383Z File "/usr/local/lib/python3.11/site-packages/django/middleware/security.py", line 28, in process_request
2026-07-24T01:13:20.383Z host = self.redirect_host or request.get_host()
2026-07-24T01:13:20.383Z ^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:20.383Z File "/usr/local/lib/python3.11/site-packages/django/http/request.py", line 151, in get_host
2026-07-24T01:13:20.383Z raise DisallowedHost(msg)
2026-07-24T01:13:20.383Z django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
2026-07-24T01:13:20.384Z WARNING 2026-07-24 01:13:20,383 log Bad Request: /api/health/
2026-07-24T01:13:20.384Z 127.0.0.1 - - [24/Jul/2026:01:13:20 +0000] "GET /api/health/ HTTP/1.0" 400 143 "-" "curl/8.14.1"
2026-07-24T01:13:25.457Z ERROR 2026-07-24 01:13:25,457 exception Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
2026-07-24T01:13:25.457Z Traceback (most recent call last):
2026-07-24T01:13:25.457Z File "/usr/local/lib/python3.11/site-packages/django/core/handlers/exception.py", line 55, in inner
2026-07-24T01:13:25.457Z response = get_response(request)
2026-07-24T01:13:25.457Z ^^^^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:25.457Z File "/usr/local/lib/python3.11/site-packages/django/utils/deprecation.py", line 133, in __call__
2026-07-24T01:13:25.457Z response = self.process_request(request)
2026-07-24T01:13:25.457Z ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:25.457Z File "/usr/local/lib/python3.11/site-packages/django/middleware/security.py", line 28, in process_request
2026-07-24T01:13:25.457Z host = self.redirect_host or request.get_host()
2026-07-24T01:13:25.457Z ^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:25.457Z File "/usr/local/lib/python3.11/site-packages/django/http/request.py", line 151, in get_host
2026-07-24T01:13:25.457Z raise DisallowedHost(msg)
2026-07-24T01:13:25.457Z django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
2026-07-24T01:13:25.458Z WARNING 2026-07-24 01:13:25,458 log Bad Request: /api/health/
2026-07-24T01:13:25.458Z 127.0.0.1 - - [24/Jul/2026:01:13:25 +0000] "GET /api/health/ HTTP/1.0" 400 143 "-" "curl/8.14.1"
2026-07-24T01:13:30.547Z ERROR 2026-07-24 01:13:30,546 exception Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
2026-07-24T01:13:30.547Z Traceback (most recent call last):
2026-07-24T01:13:30.547Z File "/usr/local/lib/python3.11/site-packages/django/core/handlers/exception.py", line 55, in inner
2026-07-24T01:13:30.547Z response = get_response(request)
2026-07-24T01:13:30.547Z ^^^^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:30.547Z File "/usr/local/lib/python3.11/site-packages/django/utils/deprecation.py", line 133, in __call__
2026-07-24T01:13:30.547Z response = self.process_request(request)
2026-07-24T01:13:30.547Z ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:30.547Z File "/usr/local/lib/python3.11/site-packages/django/middleware/security.py", line 28, in process_request
2026-07-24T01:13:30.547Z host = self.redirect_host or request.get_host()
2026-07-24T01:13:30.547Z ^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:30.547Z File "/usr/local/lib/python3.11/site-packages/django/http/request.py", line 151, in get_host
2026-07-24T01:13:30.547Z raise DisallowedHost(msg)
2026-07-24T01:13:30.547Z django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
2026-07-24T01:13:30.548Z 127.0.0.1 - - [24/Jul/2026:01:13:30 +0000] "GET /api/health/ HTTP/1.0" 400 143 "-" "curl/8.14.1"
2026-07-24T01:13:30.549Z WARNING 2026-07-24 01:13:30,548 log Bad Request: /api/health/
2026-07-24T01:13:35.621Z ERROR 2026-07-24 01:13:35,620 exception Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
2026-07-24T01:13:35.622Z Traceback (most recent call last):
2026-07-24T01:13:35.622Z File "/usr/local/lib/python3.11/site-packages/django/core/handlers/exception.py", line 55, in inner
2026-07-24T01:13:35.622Z response = get_response(request)
2026-07-24T01:13:35.622Z ^^^^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:35.622Z File "/usr/local/lib/python3.11/site-packages/django/utils/deprecation.py", line 133, in __call__
2026-07-24T01:13:35.622Z response = self.process_request(request)
2026-07-24T01:13:35.622Z ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:35.622Z File "/usr/local/lib/python3.11/site-packages/django/middleware/security.py", line 28, in process_request
2026-07-24T01:13:35.622Z host = self.redirect_host or request.get_host()
2026-07-24T01:13:35.622Z ^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:35.622Z File "/usr/local/lib/python3.11/site-packages/django/http/request.py", line 151, in get_host
2026-07-24T01:13:35.622Z raise DisallowedHost(msg)
2026-07-24T01:13:35.622Z django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
2026-07-24T01:13:35.622Z WARNING 2026-07-24 01:13:35,621 log Bad Request: /api/health/
2026-07-24T01:13:35.623Z 127.0.0.1 - - [24/Jul/2026:01:13:35 +0000] "GET /api/health/ HTTP/1.0" 400 143 "-" "curl/8.14.1"
2026-07-24T01:13:40.706Z ERROR 2026-07-24 01:13:40,706 exception Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
2026-07-24T01:13:40.706Z Traceback (most recent call last):
2026-07-24T01:13:40.706Z File "/usr/local/lib/python3.11/site-packages/django/core/handlers/exception.py", line 55, in inner
2026-07-24T01:13:40.706Z response = get_response(request)
2026-07-24T01:13:40.706Z ^^^^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:40.706Z File "/usr/local/lib/python3.11/site-packages/django/utils/deprecation.py", line 133, in __call__
2026-07-24T01:13:40.706Z response = self.process_request(request)
2026-07-24T01:13:40.706Z ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:40.706Z File "/usr/local/lib/python3.11/site-packages/django/middleware/security.py", line 28, in process_request
2026-07-24T01:13:40.706Z host = self.redirect_host or request.get_host()
2026-07-24T01:13:40.706Z ^^^^^^^^^^^^^^^^^^
2026-07-24T01:13:40.706Z File "/usr/local/lib/python3.11/site-packages/django/http/request.py", line 151, in get_host
2026-07-24T01:13:40.706Z raise DisallowedHost(msg)
2026-07-24T01:13:40.706Z django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: 'localhost'. You may need to add 'localhost' to ALLOWED_HOSTS.
2026-07-24T01:13:40.708Z WARNING 2026-07-24 01:13:40,707 log Bad Request: /api/health/
2026-07-24T01:13:40.708Z 127.0.0.1 - - [24/Jul/2026:01:13:40 +0000] "GET /api/health/ HTTP/1.0" 400 143 "-" "curl/8.14.1"