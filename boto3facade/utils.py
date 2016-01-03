#!/usr/bin/env python
# -*- coding: utf-8 -*-


import inflection


class Stub():
    """Stub methods, keep track of calls."""

    def __init__(self, monkeypatch):
        self.monkeypatch = monkeypatch
        self.stubbed = {}

    def stub(self, obj, **kwargs):
        """Stub obj.method to return whatever parameter was passed for method.
        Usage: stub(datetime.date, today='today')
        It's possible to stub several methods on the same object at once.
        """
        self.stubbed.setdefault(obj, {})
        for method, val in kwargs.items():
            self._stub(obj, method, val)
        return self.stubbed[obj]

    def _stub(self, obj, method, value):
        """Wrap the value to be returned, to check for its calls."""

        def call(*args, **kwargs):
            """Return the value monkeypatched for this method, track call."""
            self.stubbed[obj][method].append({'args': args, 'kwargs': kwargs})
            return value(*args, **kwargs)

        self.stubbed[obj][method] = []  # new stub: reset calls, if any
        self.monkeypatch.setattr(obj, method, call)


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
