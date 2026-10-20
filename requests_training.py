import functools
import logging
import time
import requests
 
log = logging.getLogger(__name__)

class FetchError(Exception):
    """Base class for all fetch errors."""
 
 
class FetchTimeout(FetchError):
    pass
 
 
class FetchConnectionError(FetchError):
    pass
 
 
class FetchHTTPError(FetchError):
    def __init__(self, status_code):
        super().__init__(f"HTTP {status_code}")
        self.status_code = status_code

def retry(retries=3, backoff=1):
    def decorator(func):
        @functools.wraps(func) 
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except (FetchTimeout, FetchConnectionError) as e:
                    last_error = e  
                except FetchHTTPError as e:
                    if e.status_code < 500:
                        raise  
                    last_error = e  
                log.warning("Attempt %d/%d failed: %s", attempt + 1, retries, last_error)
                if attempt < retries - 1:
                    time.sleep(backoff * 2 ** attempt)  
 
            raise last_error  
 
        return wrapper
 
    return decorator
 

@retry(retries=3, backoff=1)
def fetch(url, timeout=2):
    try:
        r = requests.get(url, timeout=timeout) 
        r.raise_for_status() 
    except requests.exceptions.Timeout as e:  
        raise FetchTimeout(str(e)) from e
    except requests.exceptions.ConnectionError as e:
        raise FetchConnectionError(str(e)) from e
    except requests.exceptions.HTTPError as e:
        raise FetchHTTPError(e.response.status_code) from e
    return r
 
 
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for path in ("get", "status/404", "status/500", "delay/3"):
        try:
            resp = fetch(f"https://httpbin.org/{path}")
            print(path, "->", resp.status_code)
        except FetchError as e:
            print(path, "-> failed:", type(e).__name__, e)
