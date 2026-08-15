"""
=========================================================
UI HTML Components
LMS Attendance Automation System
=========================================================
"""


def section_header(
    title: str,
    icon: str,
    description: str = "",
) -> str:
    """Generate a standard section (card) header."""

    description_html = ""

    if description:
        description_html = f"""
            <div class="section-description">
                {description}
            </div>
        """

    return f"""
    <div class="section-header">

        <div class="section-decor" aria-hidden="true"></div>

        <div class="section-icon">
            {icon}
        </div>

        <div class="section-heading">

            <div class="section-title">
                {title}
            </div>

            {description_html}

        </div>

    </div>
    """


def field_header(
    title: str,
    icon: str,
    description: str = "",
) -> str:
    """
    Generate a small icon + title + description block used
    above an individual field inside a card body (e.g. "Select
    Course", "Status"). Same idea as section_header(), scaled
    down for in-card use.
    """

    description_html = ""

    if description:
        description_html = f"""
            <div class="field-description">
                {description}
            </div>
        """

    return f"""
    <div class="field-header">

        <div class="field-icon">
            {icon}
        </div>

        <div class="field-heading">

            <div class="field-title">
                {title}
            </div>

            {description_html}

        </div>

    </div>
    """


def app_footer(
    app_name: str,
    version: str,
    developer: str = "",
    copyright_text: str = "",
) -> str:
    """
    Generate the application footer shown at the bottom of the
    dashboard. Uses the .app-footer / .footer-brand /
    .footer-title / .footer-subtitle classes already defined in
    theme.css (they existed with no matching markup before).
    """

    developer_html = ""

    if developer:
        developer_html = f"""
            <span class="footer-brand">{developer}</span>
        """

    return f"""
    <div class="app-footer">

        <div class="footer-title">
            {app_name} &middot; v{version}
        </div>

        <div class="footer-subtitle">
            {developer_html}
            {copyright_text}
        </div>

    </div>
    """
