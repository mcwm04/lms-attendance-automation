import gradio as gr


def create_dashboard_screen():
    """
    Create the main application screen.

    The dashboard is hidden until authentication succeeds.
    The actual dashboard UI is populated by the main application.
    """

    with gr.Column(
        visible=False,
        elem_classes=[
            "screen",
            "dashboard-screen",
        ],
    ) as dashboard_screen:

        # Dashboard content is created by app.py
        pass

    return dashboard_screen
