from db_client import db
from datetime import datetime, timedelta
import shutil

def cleanup_old_caches():
    cutoff = datetime.utcnow() - timedelta(days=30)
    old_caches = db.dependencies_cache.find({"lastUsed": {"$lt": cutoff}})
    
    for cache in old_caches:
        shutil.rmtree(cache['cachePath'], ignore_errors=True)
        db.dependencies_cache.delete_one({"_id": cache['_id']})

if __name__ == '__main__':
    cleanup_old_caches()
