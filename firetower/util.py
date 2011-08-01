# Normalize json
try:
    import json
except ImportError:
    import simplejson as json

__all__ = ['json']
