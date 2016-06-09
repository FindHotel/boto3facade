"""Common utilities."""

import inflection


def log_exception(exception):
    def log_exception_decorator(func):
        def func_wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except exception:
                self.config.logger.error(exception)
                raise
        return func_wrapper
    return log_exception_decorator


def roll_tags(tags):
    """Rolls a dictionary of tags into a list of tags Key/Value dicts"""
    return [{'Key': k, 'Value': v} for k, v in tags.items()]


def unroll_tags(tags):
    """Unrolls the tag list of a resource into a dictionary"""
    return {tag['Key']: tag['Value'] for tag in tags}


def has_tag(tags, key, value):
    """Returns true if a resource tag has a given value"""
    return unroll_tags(tags).get(key, None) == value


def tag_filter(key, value):
    """Returns true if a resource tags match the provided tags"""
    def filtfunc(r):
        if isinstance(r, dict):
            return unroll_tags(r.get('Tags', {})).get(key, None) == value
        else:
            return unroll_tags(r.tags or {}).get(key, None) == value
    return filtfunc


def property_filter(key, value):
    """Returns true if a resource property matches the provided value"""
    def filtfunc(r):
        if isinstance(r, dict):
            return r.get(inflection.camelize(key)) == value
        else:
            return getattr(r, inflection.underscore(key)) == value
    return filtfunc
