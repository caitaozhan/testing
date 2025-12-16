import redis

if __name__ == '__main__':
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    r.keys('*')
    r.dbsize()
    r.set('key', 'value-caitao')
    value = r.get('key')
    ret = r.exists('key')

    r.delete('key')
    value = r.get('key')

    ret = r.exists('key')

    r.set('key', 'value-caitao')
    value = r.get('key')
    expire_in_seconds = 10
    r.expire('key', expire_in_seconds)
    value = r.get('key')
    ret = r.ttl('key')
    value = r.get('key')

    r.set('key', 10)
    r.incr('key')
    value = r.get('key')
    r.decr('key')
    value = r.get('key')
    
    r.execute_command('SET', 'key', 'value-caitao')
    value = r.get('key')

    pass

    