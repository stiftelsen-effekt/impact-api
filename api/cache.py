from google.cloud import datastore
from functools import wraps
import json
import hashlib
from datetime import datetime, timedelta

def datastore_cache(timeout_days=1):
    """
    Cache decorator that uses Google Cloud Datastore.
    Caches API responses for the specified number of days.
    
    Args:
        timeout_days (int): Number of days to cache the response (default: 1)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Initialize Datastore
            client = datastore.Client()
            
            # Create cache key from view name and query parameters
            query_items = sorted(request.GET.items())
            key_parts = [view_func.__name__] + [f"{k}:{v}" for k, v in query_items]
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Create key for Datastore
            key = client.key('APICache', cache_key)
            
            # Try to get from cache
            cache_entity = client.get(key)
            
            if cache_entity:
                # Check if cache is still valid
                expires = cache_entity.get('expires')
                if expires and datetime.now().timestamp() < expires:
                    return JsonResponse(json.loads(cache_entity['response']))
            
            # Generate new response if not cached or expired
            response = view_func(request, *args, **kwargs)
            
            # Prepare and save cache entity
            cache_entity = datastore.Entity(key)
            cache_entity.update({
                'response': response.content.decode(),
                'expires': (datetime.now() + timedelta(days=timeout_days)).timestamp(),
                'created_at': datetime.now().timestamp(),
                'view_name': view_func.__name__
            })
            client.put(cache_entity)
            
            return response
        return _wrapped_view
    return decorator

# Helper function to clear cache
def clear_cache(view_name=None):
    """
    Clear the cache for a specific view or all cached responses.
    
    Args:
        view_name (str, optional): Name of the view to clear cache for. 
                                 If None, clears all cache.
    """
    client = datastore.Client()
    
    # Create query
    query = client.query(kind='APICache')
    if view_name:
        query.add_filter('view_name', '=', view_name)
    
    # Delete matching entities
    entities = query.fetch()
    keys = [entity.key for entity in entities]
    if keys:
        client.delete_multi(keys)