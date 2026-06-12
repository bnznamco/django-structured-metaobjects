# CHANGELOG

<!-- version list -->

## v1.1.0 (2026-06-12)

### Bug Fixes

- **models**: Stop MetaInstance.obj from mutating stored data in place
  ([`2984571`](https://github.com/bnznamco/django-structured-metaobjects/commit/29845712ac3b3009199fa2cf75754530374bfe2b))

- **serializers**: Serialize MetaType.schema as objects instead of key/value pair arrays
  ([`f228ce2`](https://github.com/bnznamco/django-structured-metaobjects/commit/f228ce28e1c8c0d1b39a9a677fcb381606d9dc23))

### Continuous Integration

- Gate PyPI publishing on an actual release, with a force_publish recovery path
  ([`0806d76`](https://github.com/bnznamco/django-structured-metaobjects/commit/0806d76ff45a2384435023f08992e282220bbda7))

### Documentation

- Update field kinds and descriptions in README and index
  ([`f697296`](https://github.com/bnznamco/django-structured-metaobjects/commit/f697296c022d52e5d82974d991935c7c81714a72))

- **changelog**: Add version-list anchor for semantic-release update mode
  ([`a31ec07`](https://github.com/bnznamco/django-structured-metaobjects/commit/a31ec07f67049d70fb582316e9ee942aff7412a7))

### Features

- **api**: Require staff users for the metaobjects API by default
  ([`e207604`](https://github.com/bnznamco/django-structured-metaobjects/commit/e207604138f4713318831c296ba3a6366a355a98))

- **compiler**: Enforce select choices and string/number constraints server-side
  ([`98d06e6`](https://github.com/bnznamco/django-structured-metaobjects/commit/98d06e6668057f7f1bd64e27547246b5805de0c7))
