"""
=========================================================
UI Widget Helpers
LMS Attendance Automation System
=========================================================

Thin wrappers around Gradio components.

Purpose:
- Centralize default styling
- Reduce duplicated code
- Preserve the full Gradio API
"""

import gradio as gr

__all__ = [
    "app_textbox",
    "output_box",
    "app_dropdown",
    "primary_button",
    "secondary_button",
    "upload_box",
    "app_dataframe",
    "app_checkbox",
]

# ==========================================================
# Internal Helper
# ==========================================================

def _merge_classes(default_classes, extra_classes=None):
    """
    Merge default CSS classes with additional classes.

    Parameters
    ----------
    default_classes : list[str]
        Default classes applied by the widget.

    extra_classes : str | list[str] | tuple[str] | None
        Additional classes supplied by the caller.

    Returns
    -------
    list[str]
    """

    classes = list(default_classes)

    if extra_classes is None:
        return classes

    if isinstance(extra_classes, str):
        classes.append(extra_classes)

    elif isinstance(extra_classes, (list, tuple)):
        classes.extend(extra_classes)

    else:
        raise TypeError(
            "elem_classes must be a string, list, tuple, or None."
        )

    return classes


# ==========================================================
# Textbox
# ==========================================================

def app_textbox(**kwargs):
    return gr.Textbox(
        elem_classes=_merge_classes(
            ["pro-input"],
            kwargs.pop("elem_classes", None)
        ),
        **kwargs,
    )


# ==========================================================
# Output Textbox
# ==========================================================

def output_box(**kwargs):
    return gr.Textbox(
        interactive=False,
        elem_classes=_merge_classes(
            ["pro-output"],
            kwargs.pop("elem_classes", None)
        ),
        **kwargs,
    )


# ==========================================================
# Dropdown
# ==========================================================

def app_dropdown(**kwargs):
    return gr.Dropdown(
        elem_classes=_merge_classes(
            ["pro-dropdown"],
            kwargs.pop("elem_classes", None)
        ),
        **kwargs,
    )


# ==========================================================
# Primary Button
# ==========================================================

def primary_button(value, **kwargs):
    return gr.Button(
        value=value,
        variant="primary",
        elem_classes=_merge_classes(
            ["pro-btn", "pro-btn-primary"],
            kwargs.pop("elem_classes", None)
        ),
        **kwargs,
    )


# ==========================================================
# Secondary Button
# ==========================================================

def secondary_button(value, **kwargs):
    return gr.Button(
        value=value,
        variant="secondary",
        elem_classes=_merge_classes(
            ["pro-btn", "pro-btn-secondary"],
            kwargs.pop("elem_classes", None)
        ),
        **kwargs,
    )


# ==========================================================
# File Upload
# ==========================================================

def upload_box(**kwargs):
    return gr.File(
        elem_classes=_merge_classes(
            ["pro-upload"],
            kwargs.pop("elem_classes", None)
        ),
        **kwargs,
    )


# ==========================================================
# Dataframe
# ==========================================================

def app_dataframe(**kwargs):
    return gr.Dataframe(
        elem_classes=_merge_classes(
            ["pro-table"],
            kwargs.pop("elem_classes", None)
        ),
        **kwargs,
    )


# ==========================================================
# Checkbox
# ==========================================================

def app_checkbox(**kwargs):
    return gr.Checkbox(
        elem_classes=_merge_classes(
            ["pro-checkbox"],
            kwargs.pop("elem_classes", None)
        ),
        **kwargs,
    )
