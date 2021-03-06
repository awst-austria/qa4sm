export class CacheItem<T> {
  constructor(public createdOn: Date, public data: T) {
  }
}

export class DataCache<T> {
  cacheLifeTime: number;
  cache: Map<string, CacheItem<T>> = new Map<string, CacheItem<T>>();

  constructor(lifeTimeMinutes = 5) {
    this.cacheLifeTime = lifeTimeMinutes * 60 * 1000;
  }

  public push(key: any, value: T) {
    this.cache.set(key, new CacheItem<T>(new Date(), value));
  }

  public get(key: any): T {
    if (this.isCached(key)) {
      return this.cache.get(key).data;
    }
    return null;
  }

  public isCached(key: any): boolean {
    if (this.cache.has(key)) {
      let cacheItem = this.cache.get(key);
      if (((new Date()).getTime() - cacheItem.createdOn.getTime()) < this.cacheLifeTime) {
        return true;
      } else {
        this.cache.delete(key);
      }
    }
    return false;
  }
}
