import dataclasses


@dataclasses.dataclass
class EditableField:
    model: object
    field_out: str
    session_field_name: str | None
    field_in: str | None
