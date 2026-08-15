
import gradio as gr


def create_authentication_screen(
    saved_username="",
    saved_password="",
    remember_default=False,
    logo_data="",
):
    """
    Create the dedicated authentication screen.

    Returns
    -------
    tuple
        Authentication screen and its components.
    """

    with gr.Column(
        visible=True,
        elem_classes=["screen", "authentication-screen"],
    ) as authentication_screen:

        # ==================================================
        # AUTHENTICATION LAYOUT WRAPPER
        # ==================================================

        with gr.Column(
            elem_classes=["authentication-wrapper"]
        ):

            # ==================================================
            # AUTHENTICATION CONTENT
            # ==================================================

            with gr.Column(
                elem_classes=["authentication-content"]
            ):

                # --------------------------------------------------
                # BRANDING
                # --------------------------------------------------

                gr.HTML(
                    f"""
                    <div class="authentication-brand">

                        <div class="authentication-logo">
                            <img
                                src="data:image/png;base64,{logo_data}"
                                alt="University of Agriculture Faisalabad"
                            >
                        </div>

                        <div class="authentication-title">
                            LMS Attendance Automation
                        </div>

                        <div class="authentication-subtitle">
                            Sign in to your LMS account to continue
                        </div>

                    </div>
                    """
                )

                # --------------------------------------------------
                # LOGIN CARD
                # --------------------------------------------------

                with gr.Column(
                    elem_classes=["authentication-card"]
                ):

                    gr.HTML(
                        """
                        <div class="authentication-card-header">

                            <div class="authentication-card-icon">
                                🔐
                            </div>

                            <div>
                                <div class="authentication-card-title">
                                    LMS Authentication
                                </div>

                                <div class="authentication-card-description">
                                    Enter your LMS credentials to continue.
                                </div>
                            </div>

                        </div>
                        """
                    )

                    auth_username = gr.Textbox(
                        label="Username",
                        placeholder="Enter LMS username",
                        value=saved_username,
                        elem_classes=["authentication-input"],
                    )

                    auth_password = gr.Textbox(
                        label="Password",
                        placeholder="Enter LMS password",
                        type="password",
                        value=saved_password,
                        elem_classes=["authentication-input"],
                    )

                    auth_remember_me = gr.Checkbox(
                        label="Remember Me",
                        value=remember_default,
                        elem_classes=["authentication-remember"],
                    )

                    login_button = gr.Button(
                        "Login",
                        variant="primary",
                        elem_classes=["authentication-login-button"],
                    )

                    authentication_status = gr.HTML(
                        "",
                        elem_classes=["authentication-status"],
                    )

    return (
        authentication_screen,
        auth_username,
        auth_password,
        auth_remember_me,
        login_button,
        authentication_status,
    )
