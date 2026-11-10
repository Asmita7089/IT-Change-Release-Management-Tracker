import streamlit as st
import pandas as pd
from datetime import date

from database import (
    create_tables,
    add_change,
    get_all_changes,
    get_change_by_id,
    update_change_status,
    update_readiness,
    add_review,
    get_reviews
)

from risk_engine import calculate_risk
from readiness_checker import check_readiness


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="IT Change & Release Management Tracker",
    page_icon="🔄",
    layout="wide"
)

create_tables()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("Change Management")

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Change Requests",
        "Risk & Approval",
        "Release Readiness",
        "Post-Release Review"
    ]
)


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

if page == "Dashboard":

    st.title("IT Change & Release Management Tracker")

    st.write(
        "Monitor change requests, risk levels, approvals, "
        "release readiness, and post-release activities."
    )

    changes = get_all_changes()

    if changes:

        df = pd.DataFrame(
            changes,
            columns=[
                "ID",
                "Title",
                "Requester",
                "Change Type",
                "Impact",
                "Likelihood",
                "Risk Score",
                "Risk Level",
                "Status",
                "Planned Date",
                "Created At"
            ]
        )

        # -------------------------------------------------
        # KPI METRICS
        # -------------------------------------------------

        total_changes = len(df)

        pending = len(
            df[df["Status"] == "Pending Approval"]
        )

        high_risk = len(
            df[df["Risk Level"] == "High"]
        )

        scheduled = len(
            df[df["Status"] == "Scheduled"]
        )

        completed = len(
            df[df["Status"] == "Completed"]
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            "Total Changes",
            total_changes
        )

        col2.metric(
            "Pending Approval",
            pending
        )

        col3.metric(
            "High Risk",
            high_risk
        )

        col4.metric(
            "Scheduled",
            scheduled
        )

        col5.metric(
            "Completed",
            completed
        )

        st.divider()

        # -------------------------------------------------
        # STATUS + RISK OVERVIEW
        # -------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Change Status")

            status_counts = (
                df["Status"]
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Count")
            )

            st.bar_chart(
                status_counts.set_index("Status")
            )

        with col2:

            st.subheader("Risk Distribution")

            risk_counts = (
                df["Risk Level"]
                .value_counts()
                .rename_axis("Risk Level")
                .reset_index(name="Count")
            )

            st.bar_chart(
                risk_counts.set_index("Risk Level")
            )

        st.divider()

        # -------------------------------------------------
        # UPCOMING RELEASES
        # -------------------------------------------------

        st.subheader("Upcoming Releases")

        upcoming = df[
            df["Planned Date"].notna()
            & (df["Status"] != "Completed")
        ].copy()

        if not upcoming.empty:

            upcoming = upcoming[
                [
                    "ID",
                    "Title",
                    "Change Type",
                    "Risk Level",
                    "Status",
                    "Planned Date"
                ]
            ]

            upcoming = upcoming.sort_values(
                by="Planned Date"
            )

            st.dataframe(
                upcoming,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No upcoming releases available."
            )

        st.divider()

        # -------------------------------------------------
        # HIGH-RISK CHANGES
        # -------------------------------------------------

        st.subheader("High-Risk Changes")

        high_risk_df = df[
            df["Risk Level"] == "High"
        ]

        if not high_risk_df.empty:

            high_risk_df = high_risk_df[
                [
                    "ID",
                    "Title",
                    "Requester",
                    "Risk Score",
                    "Status",
                    "Planned Date"
                ]
            ]

            st.dataframe(
                high_risk_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "No high-risk changes currently identified."
            )

        st.divider()

        # -------------------------------------------------
        # ALL CHANGE REQUESTS
        # -------------------------------------------------

        st.subheader("All Change Requests")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No change requests have been created yet."
        )
# ---------------------------------------------------------
# CHANGE REQUESTS
# ---------------------------------------------------------

elif page == "Change Requests":

    st.title("Change Requests")

    st.subheader("Create New Change Request")

    with st.form("change_request_form"):

        title = st.text_input(
            "Change Title"
        )

        description = st.text_area(
            "Change Description"
        )

        requester = st.text_input(
            "Requester"
        )

        change_type = st.selectbox(
            "Change Type",
            [
                "Standard",
                "Normal",
                "Emergency"
            ]
        )

        col1, col2 = st.columns(2)

        with col1:
            impact = st.slider(
                "Business / System Impact",
                1,
                5,
                1
            )

        with col2:
            likelihood = st.slider(
                "Likelihood of Failure",
                1,
                5,
                1
            )

        planned_date = st.date_input(
            "Planned Implementation Date",
            value=date.today()
        )

        implementation_plan = st.text_area(
            "Implementation Plan"
        )

        rollback_plan = st.text_area(
            "Rollback Plan"
        )

        submitted = st.form_submit_button(
            "Submit Change Request"
        )

        if submitted:

            if (
                not title
                or not description
                or not requester
            ):
                st.error(
                    "Please fill in all required fields."
                )

            else:

                risk_score, risk_level = calculate_risk(
                    impact,
                    likelihood
                )

                add_change(
                    title,
                    description,
                    requester,
                    change_type,
                    impact,
                    likelihood,
                    risk_score,
                    risk_level,
                    "Pending Approval",
                    planned_date.strftime("%Y-%m-%d"),
                    implementation_plan,
                    rollback_plan
                )

                st.success(
                    "Change request submitted successfully."
                )

                st.info(
                    f"Risk Score: {risk_score} | "
                    f"Risk Level: {risk_level}"
                )

    st.divider()

    st.subheader("Existing Change Requests")

    changes = get_all_changes()

    if changes:

        df = pd.DataFrame(
            changes,
            columns=[
                "ID",
                "Title",
                "Requester",
                "Change Type",
                "Impact",
                "Likelihood",
                "Risk Score",
                "Risk Level",
                "Status",
                "Planned Date",
                "Created At"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No change requests available.")


# ---------------------------------------------------------
# RISK & APPROVAL
# ---------------------------------------------------------

elif page == "Risk & Approval":

    st.title("Risk Assessment & Approval")

    changes = get_all_changes()

    if not changes:

        st.info(
            "No change requests available."
        )

    else:

        change_options = {
            f"{row[0]} - {row[1]}": row[0]
            for row in changes
        }

        selected = st.selectbox(
            "Select Change Request",
            list(change_options.keys())
        )

        change_id = change_options[selected]

        change = get_change_by_id(change_id)

        st.subheader(
            f"Change #{change[0]} - {change[1]}"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Impact",
            change[5]
        )

        col2.metric(
            "Likelihood",
            change[6]
        )

        col3.metric(
            "Risk Score",
            change[7]
        )

        st.write(
            f"**Risk Level:** {change[8]}"
        )

        st.write(
            f"**Requester:** {change[3]}"
        )

        st.write(
            f"**Change Type:** {change[4]}"
        )

        st.write(
            f"**Description:** {change[2]}"
        )

        st.divider()

        st.subheader("Approval Status")

        current_status = change[9]

        status_options = [
            "Pending Approval",
            "Approved",
            "Rejected",
            "Scheduled",
            "Completed"
        ]

        selected_status = st.selectbox(
            "Update Status",
            status_options,
            index=status_options.index(current_status)
            if current_status in status_options
            else 0
        )

        if st.button("Update Approval / Status"):

            update_change_status(
                change_id,
                selected_status
            )

            st.success(
                "Change status updated successfully."
            )


# ---------------------------------------------------------
# RELEASE READINESS
# ---------------------------------------------------------

elif page == "Release Readiness":

    st.title("Release Readiness")

    changes = get_all_changes()

    if not changes:

        st.info(
            "No change requests available."
        )

    else:

        change_options = {
            f"{row[0]} - {row[1]}": row[0]
            for row in changes
        }

        selected = st.selectbox(
            "Select Change Request",
            list(change_options.keys())
        )

        change_id = change_options[selected]

        change = get_change_by_id(change_id)

        st.subheader(
            f"Readiness Check - {change[1]}"
        )

        st.write(
            "Complete the following checks before "
            "considering the change ready for release."
        )

        testing_completed = st.checkbox(
            "Testing Completed",
            value=bool(change[13])
        )

        approval_obtained = st.checkbox(
            "Approval Obtained",
            value=bool(change[14])
        )

        documentation_ready = st.checkbox(
            "Documentation Ready",
            value=bool(change[15])
        )

        implementation_plan = change[11]
        rollback_plan = change[12]

        st.write(
            "**Implementation Plan:**"
        )

        st.write(
            implementation_plan
            if implementation_plan
            else "Not provided."
        )

        st.write(
            "**Rollback Plan:**"
        )

        st.write(
            rollback_plan
            if rollback_plan
            else "Not provided."
        )

        if st.button("Save Readiness Check"):

            update_readiness(
                change_id,
                int(testing_completed),
                int(approval_obtained),
                int(documentation_ready)
            )

            ready, checks = check_readiness(
                testing_completed,
                approval_obtained,
                implementation_plan,
                rollback_plan,
                documentation_ready
            )

            if ready:

                st.success(
                    "Change is READY for release."
                )

            else:

                st.warning(
                    "Change is NOT ready for release. "
                    "Complete all required checks."
                )

                for check, result in checks.items():

                    if result:
                        st.write(
                            f"✅ {check}"
                        )

                    else:
                        st.write(
                            f"❌ {check}"
                        )


# ---------------------------------------------------------
# POST-RELEASE REVIEW
# ---------------------------------------------------------

elif page == "Post-Release Review":

    st.title("Post-Release Review")

    changes = get_all_changes()

    if not changes:

        st.info(
            "No change requests available."
        )

    else:

        change_options = {
            f"{row[0]} - {row[1]}": row[0]
            for row in changes
        }

        selected = st.selectbox(
            "Select Completed Change",
            list(change_options.keys())
        )

        change_id = change_options[selected]

        implementation_result = st.selectbox(
            "Implementation Result",
            [
                "Successful",
                "Successful with Minor Issues",
                "Failed"
            ]
        )

        issues = st.text_area(
            "Issues Encountered"
        )

        lessons_learned = st.text_area(
            "Lessons Learned"
        )

        if st.button("Submit Post-Release Review"):

            add_review(
                change_id,
                implementation_result,
                issues,
                lessons_learned
            )

            st.success(
                "Post-release review submitted successfully."
            )

    st.divider()

    st.subheader("Previous Reviews")

    reviews = get_reviews()

    if reviews:

        review_df = pd.DataFrame(
            reviews,
            columns=[
                "Review ID",
                "Change ID",
                "Change Title",
                "Implementation Result",
                "Issues",
                "Lessons Learned",
                "Review Date"
            ]
        )

        st.dataframe(
            review_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No post-release reviews available."
        )