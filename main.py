from drafter import *
from dataclasses import dataclass

@dataclass
class InspectionReport:
    project_name: str
    safety_score: int
    issue_description: str
    resolved: bool

@dataclass
class State:
    reports: list[InspectionReport]
    current_project: str
    total_inspections: int
    safety_alerts: int
    manager_notes: str
    
@route
def index(state: State)-> Page:
    """Shows the min dashboard of the Site Inspection Manager website
    Args:
        state: the current website state
    Returns:
        A page containing project information, safety alerts,
        inspection totals, and navigation buttons.
    """
    return Page(state, [
        "Site Inspection Manager",
        "Current Project: " + state.current_project,
        "Total Inspections: " + str(state.total_inspections),
        "Open Alerts: " + str(state.safety_alerts),

        Button("New Inspection", new_inspection),
        Button("View Reports", view_reports),
        Button("Safety Alerts", safety_alerts_page),
        Button("Project Status", project_status),
        Button("Manager Notes", manager_notes_page),
        Button("Statistics", statistics),
        Button("Resolve Issue", "resolve_issue_page")
    ])

@route
def new_inspection(state: State):
    """Displays a form that allows the user to enter information
    for a new site inspection report.
    Args:
        state: The current website state
    Returns:
        A page containng inspection input fields and a submit button.
    """
    return Page(state, [
        "Create Inspection",

        "Project Name",
        TextBox("project"),

        "Safety Score",
        TextBox("score"),

        "Issue Description",
        TextArea("issue"),

        "Hazard Present",
        CheckBox("hazard"),

        Button("Submit", "submit_inspection")
    ])

@route
def submit_inspection(state: State, project: str, score: str, issue: str, hazard: bool):
    """Creates a new inspetion report using user input and updates
       inspection statistics stored in the website state.
    Args:
        state: The current website state.
        project: The name of the inspected project.
        score: The safety score entered by the user.
        issue: The description of the inspection issue.
        hazard: Whether a safety hazard was reported.
    Return:
        The updated home page after the inspection has been saved
    """
    if score == "":
        return Page(state, [
            Header("Invalid Safety Score"),
            "Safety score cannot be blank.",
            Button("Back", "new_inspection")
        ])

    if not score.isdigit():
        return Page(state, [
            Header("Invalid Safety Score"),
            "Safety score must contain only numbers.",
            Button("Back", "new_inspection")
        ])
    
    safety_score = int(score)

    if safety_score < 0 or safety_score > 100:
        return Page(state, [
            Header("Invalid Safety Score"),
            "Safety scores must be between 0 and 100.",
            Button("Back", "new_inspection")
        ])

    report = InspectionReport(project, safety_score, issue, False)

    state.reports.append(report)
    state.current_project = project
    state.total_inspections += 1

    if hazard:
        state.safety_alerts += 1

    return index(state)

@route
def view_reports(state: State):
    """Displays all inspection reports currently stored in the
       website state.
    Args:
        state: The current website state.
    Returns:
        A page listing all submitted inspection reports.
    """
    content = [
        "Inspection Reports"
    ]

    for report in state.reports:
        if report.resolved:
            status = "Resolved"
    else:
        status = "Open"

    content.append(
        report.project_name +
        " | Score: " +
        str(report.safety_score) +
        " | Status: " +
        status
    )

    content.append(Button("Home", "index"))

    return Page(state, content)

@route
def safety_alerts_page(state: State):
    """Reviews all inspection reports and displays safety warnings
       for projects with low safety scores or unresolved issues.
    Args:
        state: The current website state.
    Returns:
        A page containing active safety alerts and warnings.
    """
    content = ["Safety Alerts"]

    for report in state.reports:

        if report.safety_score < 70:
            content.append("WARNING: " + report.project_name)

        if not report.resolved:
            content.append("Open Issue: " + report.issue_description)

    content.append(Button("Home", "index"))

    return Page(state, content)

@route
def project_status(state: State):
    """Displays the current project and an overall project status
        based on the number of active safety alerts.
    Args:
        state: The current website state.
    Returns:
        A page showing project status information.
    """
    status = "On Schedule"

    if state.safety_alerts > 3:
        status = "Needs Attention"

    return Page(state, ["Project Status", "Current Project: " + state.current_project, "Status: " + status,
        Button("Home", "index")
    ])

@route
def manager_notes_page(state: State):
    """Displays a page where the manager can enter notes and
        observations about the project.
    Args:
        state: The current website state.
    Returns:
        A page containing a text area for entering manager notes.
    """
    return Page(state, [
        "Manager Notes",
        TextArea("notes"),
        Button("Save", save_notes),
        Button("Home", "index")
    ])

@route
def save_notes(state: State, notes: str):
    """Saves manager notes into the website state.
    Args:
        state: The current website state.
        notes: The text entered by the manager.
    Returns:
        A page displaying the saved notes.
    """
    state.manager_notes = notes

    return Page(state, [
        "Notes Saved",
        state.manager_notes,
        Button("Home", "index")])

@route
def statistics(state: State):
    """Calculates and displays inspection statistics such as
        total inspections, average safety score, and active alerts.
    Args:
        state: The current website state.
    Returns:
        A page displaying inspection statistics.
    """
    average = 0.0

    if len(state.reports) > 0:
        total = 0
        for report in state.reports:
            total += report.safety_score
        average = total / len(state.reports)

    return Page(state, [
        "Statistics",
        "Inspections: " + str(state.total_inspections),
        "Average Score: " + str(round(average, 1)),
        "Alerts: " + str(state.safety_alerts),
        Button("Home", "index")
    ])

@route
def resolve_issue_page(state: State) -> Page:
    """Displays a page where the manager can enter the name of a project
       whose issue has been resolved.
    Args:
        state: The current website state.
    Return:
        A page containing a textbox and resolve button.
    """
    return Page(state, [
        Header("Resolve Safety Issue"),

        "Enter Project Name:",

        TextBox("project_to_resolve", ""),

        Button("Resolve", "resolve_issue"),

        Button("Home", "index")
    ])

@route
def resolve_issue(state: State,
                  project_to_resolve: str) -> Page:
    """
    Description:
        Searches for a project and marks its issue as resolved.

    Args:
        state: The current website state.
        project_to_resolve: The project name entered by the user.

    Returns:
        The updated home page.
    """

    for report in state.reports:

        if report.project_name == project_to_resolve:
            if report.resolved == False:
                report.resolved = True
                if state.safety_alerts > 0:
                    state.safety_alerts -= 1

    return index(state)

start_server(State([], "", 0, 0, ""))


