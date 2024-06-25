import datetime
import functools
import inspect

cache_data = {}


def get_func_key(func, *fn_args, **fn_kwargs):
    bound = inspect.signature(func).bind(*fn_args, **fn_kwargs)
    bound.apply_defaults()
    bound.arguments.pop("self", None)
    return hash(f"{func.__name__}@{bound.arguments}")


def cache_decorator(ttl=None, is_async=False):
    """
    example:
    @cache_decorator
    @cache_decorator(ttl=datetime.timedelta(hours=1))
    @cache_decorator(is_async=True)
    """

    def wrap(func):
        @functools.wraps(func)
        async def async_wrapper(*fn_args, **fn_kwargs):
            if fn_kwargs.get("no_cache", False):
                return await func(*fn_args, **fn_kwargs)

            ins_key = get_func_key(func, *fn_args, **fn_kwargs)
            now = datetime.datetime.now()
            default_data = {"time": None, "value": None}

            data = cache_data.get(ins_key, default_data)

            if ttl is None:
                if not data["value"]:
                    data["value"] = await func(*fn_args, **fn_kwargs)
                    cache_data[ins_key] = data
            else:
                if not data["time"] or now - data["time"] > ttl:
                    data["value"] = await func(*fn_args, **fn_kwargs)
                    data["time"] = now
                    cache_data[ins_key] = data

            return data["value"]

        @functools.wraps(func)
        def sync_wrapper(*fn_args, **fn_kwargs):
            if fn_kwargs.get("no_cache", False):
                return func(*fn_args, **fn_kwargs)

            ins_key = get_func_key(func, *fn_args, **fn_kwargs)
            now = datetime.datetime.now()
            default_data = {"time": None, "value": None}

            data = cache_data.get(ins_key, default_data)

            if ttl is None:
                if not data["value"]:
                    data["value"] = func(*fn_args, **fn_kwargs)
                    cache_data[ins_key] = data
            else:
                if not data["time"] or now - data["time"] > ttl:
                    data["value"] = func(*fn_args, **fn_kwargs)
                    data["time"] = now
                    cache_data[ins_key] = data

            return data["value"]

        return async_wrapper if is_async else sync_wrapper

    if callable(ttl):
        return wrap(ttl)
    return wrap


Cache = cache_decorator
AsyncCache = functools.partial(cache_decorator, is_async=True)
