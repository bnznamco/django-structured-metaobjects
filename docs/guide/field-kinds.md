# Field Kinds

Each field in a MetaType schema is described by a `MetaTypeFieldDef` with a `kind` property. The compiler maps each kind to a Python type at runtime.

## Primitive Kinds

| Kind       | Python Type        | Notes            |
|------------|--------------------|------------------|
| `string`   | `str`              |                  |
| `text`     | `str`              | Multi-line       |
| `integer`  | `int`              |                  |
| `number`   | `float`            |                  |
| `boolean`  | `bool`             |                  |
| `date`     | `datetime.date`    |                  |
| `datetime` | `datetime.datetime`|                  |

## Relationship Kinds

| Kind       | Python Type              | Notes                                     |
|------------|--------------------------|-------------------------------------------|
| `ref`      | `<TargetModel>`          | Requires `target_model="app.Model"`       |
| `queryset` | `List[<TargetModel>]`    | Requires `target_model="app.Model"`       |

These resolve to real Django model instances via `django-structured-json-field`'s lazy caching.

## Composite Kinds

| Kind    | Python Type                      | Notes                          |
|---------|----------------------------------|--------------------------------|
| `group` | Nested Pydantic model            | Built from `children` field    |
| `list`  | `List[<nested Pydantic model>]`  | Built from `children` field    |

## Translated Fields

Setting `translated: true` on any field wraps its type in `Dict[str, T]`, turning the value into a per-language map:

```python
{"name": "title", "kind": "string", "translated": true}
# Compiled type: Dict[str, str]
# Example value: {"en": "Hello", "it": "Ciao"}
```

## Conditional Logic

The `MetaTypeFieldDef` schema includes conditional JSON Schema rules:

- `target_model` is shown (and required) only when `kind` is `ref` or `queryset`
- `children` is shown only when `kind` is `group` or `list`

These conditionals are enforced in the admin JSON editor via `django-structured-json-field`'s `When` / `conditional_schema` utilities.
