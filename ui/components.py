import gradio as gr

from .html import section_header, field_header

def section_card(
    title: str,
    icon: str,
    *,
    description: str = "",
    elem_classes=None,
):
    """
    Create a standard section card.

    Returns
    -------
    gr.Group
        The card container.

    Example
    -------
    with section_card("Authentication", "🔐"):
        ...
    """

    classes = ["section-card"]

    if elem_classes:
        if isinstance(elem_classes, str):
            classes.append(elem_classes)
        else:
            classes.extend(elem_classes)

    group = gr.Group(elem_classes=classes)

    # Create the header immediately
    with group:
        gr.HTML(
            section_header(
                title,
                icon,
                description,
            )
        )

    return group


def section_body(*, elem_classes=None):
    """
    Create a standard section body.
    """

    classes = ["section-body"]

    if elem_classes:
        if isinstance(elem_classes, str):
            classes.append(elem_classes)
        else:
            classes.extend(elem_classes)

    return gr.Column(elem_classes=classes)


def field_group(
    title: str,
    icon: str,
    *,
    description: str = "",
    elem_classes=None,
):
    """
    Wrap a single field (dropdown, textbox, etc.) with a small
    icon + title + description header, matching the look of the
    card-level section_card() header but scaled down for use
    inside a card body.

    Example
    -------
    with field_group("Select Course", "🎓", description="Choose the course you want to manage"):
        course_dropdown = app_dropdown(...)
    """

    classes = ["field-group"]

    if elem_classes:
        if isinstance(elem_classes, str):
            classes.append(elem_classes)
        else:
            classes.extend(elem_classes)

    group = gr.Column(elem_classes=classes)

    with group:
        gr.HTML(
            field_header(
                title,
                icon,
                description,
            )
        )

    return group
