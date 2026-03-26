"""
Financial Advisor Dashboard - Main Application
A comprehensive financial health dashboard built with Streamlit.

This dashboard is designed with a clean separation between:
- Logic layer (logic/) - Pure Python calculations, framework-agnostic
- Components layer (components/) - UI rendering components  
- Data layer (data/) - Sample data and data access

This separation makes it easy to port to React or any other frontend.
"""

import streamlit as st
import sys
import os
import hashlib
import tempfile
from typing import Dict
from datetime import datetime
from pathlib import Path
from dateutil.relativedelta import relativedelta

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import logic calculators
from logic import (
    FinancialFoundation,
    CashFlowBehavior,
    PortfolioHealth,
    FuturePlanning,
    EstateReadiness,
    HealthStatus
)

# Import UI components
from components import (
    get_custom_css,
    render_header,
    render_net_worth_summary,
    render_section_header,
    render_metric_card,
    render_metric_grid,
    render_allocation_chart,
    render_goal_progress,
    render_expense_breakdown,
    render_retirement_projection_chart,
    render_asset_breakdown_chart,
    render_health_score_gauge
)

# Import sample data
from data import get_all_sample_clients, get_historical_expenses

# Import database functions for profile management
from database.db import (
    update_client_profile,
    get_client_dependents,
    add_dependent,
    update_dependent,
    delete_dependent,
    get_client_documents,
    add_document,
    delete_document,
    get_document_by_hash,
    get_document_by_id,
    get_client_by_id,
    get_document_content,
    save_risk_willingness_survey,
    get_latest_risk_willingness_survey,
    save_risk_tolerance_assessment,
    get_latest_risk_tolerance_assessment,
    save_risk_assessment_result,
    get_latest_risk_assessment_result,
)

# Uploads directory
UPLOADS_DIR = Path(project_root) / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA-256 hash of file content."""
    return hashlib.sha256(file_content).hexdigest()


def render_profile_section(client_id: str, client_data):
    """Render the Profile section with tabs in the main panel."""
    # Section header
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="font-size: 1.5rem; font-weight: 600; color: #1E293B; margin: 0;">Profile Management</h2>
        <p style="font-size: 0.875rem; color: #475569; margin-top: 0.25rem;">Manage personal information, dependents, and documents</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 Personal Info", "👨‍👩‍👧 Dependents", "📄 Documents", "🏥 Disability Analysis", "📊 Risk Assessment"])
    
    with tab1:
        render_personal_info_tab(client_id, client_data)
    
    with tab2:
        render_dependents_tab(client_id)
    
    with tab3:
        render_documents_tab(client_id)
        
    with tab4:
        render_disability_analysis_tab(client_id, client_data)
    
    with tab5:
        render_risk_assessment_tab(client_id, client_data)


def render_personal_info_tab(client_id: str, client_data):
    """Render the Personal Info tab."""
    # Get current client data from database
    client_row = get_client_by_id(client_id)
    
    if not client_row:
        st.error("Client not found")
        return
    
    st.markdown("""
    <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 1rem;">
        <h3 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0 0 0.5rem 0;">Edit Personal Information</h3>
        <p style="font-size: 0.8rem; color: #64748B; margin: 0;">Update your profile details below</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form(key="personal_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Date of birth (for age calculation)
            current_dob = client_row.get('date_of_birth', '')
            if current_dob:
                try:
                    dob_date = datetime.strptime(current_dob, '%Y-%m-%d').date()
                except:
                    dob_date = datetime.now().date()
            else:
                dob_date = datetime.now().date()
            
            date_of_birth = st.date_input(
                "Date of Birth",
                value=dob_date,
                help="Used to calculate age"
            )
            
            # Gender
            gender_options = ['male', 'female']
            current_gender = client_row.get('gender_at_birth', 'male')
            gender_index = gender_options.index(current_gender) if current_gender in gender_options else 0
            
            gender = st.selectbox(
                "Gender",
                options=gender_options,
                index=gender_index,
                format_func=lambda x: x.capitalize()
            )
            
            # Retirement Age
            retirement_age = st.number_input(
                "Retirement Age",
                min_value=50,
                max_value=80,
                value=client_row.get('retirement_age', 65) or 65
            )
        
        with col2:
            # Risk Tolerance
            risk_options = ['low', 'moderate', 'high', 'critical']
            current_risk = client_row.get('risk_tolerance', 'moderate')
            risk_index = risk_options.index(current_risk) if current_risk in risk_options else 1
            
            risk_tolerance = st.selectbox(
                "Risk Tolerance",
                options=risk_options,
                index=risk_index,
                format_func=lambda x: x.capitalize()
            )
            
            # Marital Status
            marital_options = ['single', 'married', 'divorced', 'widowed', 'domestic_partnership']
            current_marital = client_row.get('marital_status', 'single')
            marital_index = marital_options.index(current_marital) if current_marital in marital_options else 0
            
            marital_status = st.selectbox(
                "Marital Status",
                options=marital_options,
                index=marital_index,
                format_func=lambda x: x.replace('_', ' ').capitalize()
            )
            
            # Employment Type
            employment_type_options = [
                'government_tenured', 'salaried_full_time', 'self_employed_stable',
                'commission_variable', 'contract_gig', 'retired'
            ]
            employment_type_labels = {
                'government_tenured': 'Government / Tenured',
                'salaried_full_time': 'Salaried Full-Time',
                'self_employed_stable': 'Self-Employed / Stable Business',
                'commission_variable': 'Commission / Variable Income',
                'contract_gig': 'Contract / Gig Worker',
                'retired': 'Retired',
            }
            current_employment = client_row.get('employment_type', 'salaried_full_time') or 'salaried_full_time'
            employment_index = employment_type_options.index(current_employment) if current_employment in employment_type_options else 1
            
            employment_type = st.selectbox(
                "Employment Type",
                options=employment_type_options,
                index=employment_index,
                format_func=lambda x: employment_type_labels.get(x, x.replace('_', ' ').title())
            )
            
            # State
            us_states = [
                'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
            ]
            current_state = client_row.get('state', 'CA')
            state_index = us_states.index(current_state) if current_state in us_states else us_states.index('CA')
            
            state = st.selectbox(
                "State",
                options=us_states,
                index=state_index
            )
        
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
        
        if submitted:
            try:
                update_data = {
                    'date_of_birth': date_of_birth.strftime('%Y-%m-%d'),
                    'gender_at_birth': gender,
                    'retirement_age': retirement_age,
                    'risk_tolerance': risk_tolerance,
                    'marital_status': marital_status,
                    'employment_type': employment_type,
                    'state': state
                }
                update_client_profile(client_id, update_data)
                st.success("✅ Profile updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating profile: {e}")


def render_dependents_tab(client_id: str):
    """Render the Dependents tab."""
    # Get existing dependents
    dependents = get_client_dependents(client_id)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Add new dependent section
        st.markdown("""
        <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 1rem;">
            <h3 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0 0 0.5rem 0;">Add New Dependent</h3>
            <p style="font-size: 0.8rem; color: #64748B; margin: 0;">Enter dependent details below</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form(key="add_dependent_form", clear_on_submit=True):
            dep_name = st.text_input("Name", placeholder="Enter dependent's name")
            
            relationship = st.selectbox(
                "Relationship",
                options=['child', 'spouse', 'parent', 'sibling', 'other'],
                format_func=lambda x: x.capitalize()
            )
            
            dep_dob = st.date_input("Date of Birth", value=None)
            
            fcol1, fcol2 = st.columns(2)
            with fcol1:
                is_financially_dependent = st.checkbox("Financially Dependent", value=True)
            with fcol2:
                special_needs = st.checkbox("Special Needs", value=False)
            
            dep_notes = st.text_area("Notes", placeholder="Optional notes...", height=80)
            
            add_submitted = st.form_submit_button("➕ Add Dependent", use_container_width=True)
            
            if add_submitted and dep_name:
                try:
                    dep_data = {
                        'name': dep_name,
                        'relationship': relationship,
                        'date_of_birth': dep_dob.strftime('%Y-%m-%d') if dep_dob else None,
                        'is_financially_dependent': is_financially_dependent,
                        'special_needs': special_needs,
                        'notes': dep_notes if dep_notes else None
                    }
                    add_dependent(client_id, dep_data)
                    st.success(f"✅ Added {dep_name} as dependent!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding dependent: {e}")
    
    with col2:
        # Display existing dependents
        st.markdown("""
        <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 1rem;">
            <h3 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0 0 0.5rem 0;">Current Dependents</h3>
            <p style="font-size: 0.8rem; color: #64748B; margin: 0;">Manage existing dependents</p>
        </div>
        """, unsafe_allow_html=True)
        
        if dependents:
            for dep in dependents:
                dep_id = dep['id']
                with st.expander(f"**{dep['name']}** ({dep['relationship'].capitalize()})", expanded=False):
                    # Calculate age if DOB available
                    age_str = ""
                    if dep.get('date_of_birth'):
                        try:
                            dob = datetime.strptime(dep['date_of_birth'], '%Y-%m-%d').date()
                            today = datetime.now().date()
                            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                            age_str = f" (Age: {age})"
                        except:
                            pass
                    
                    st.markdown(f"""
                    <div style="font-size: 0.85rem; color: #475569;">
                        <div style="margin-bottom: 0.5rem;"><strong>Relationship:</strong> {dep['relationship'].capitalize()}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Date of Birth:</strong> {dep.get('date_of_birth', 'Not specified')}{age_str}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Financially Dependent:</strong> {'Yes' if dep.get('is_financially_dependent') else 'No'}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Special Needs:</strong> {'Yes' if dep.get('special_needs') else 'No'}</div>
                        {f"<div style='margin-bottom: 0.5rem;'><strong>Notes:</strong> {dep.get('notes')}</div>" if dep.get('notes') else ""}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"🗑️ Delete Dependent", key=f"del_dep_{dep_id}", use_container_width=True):
                        try:
                            delete_dependent(dep_id)
                            st.success(f"Deleted {dep['name']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting dependent: {e}")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #94A3B8;">
                <p style="font-size: 0.9rem;">No dependents added yet</p>
                <p style="font-size: 0.8rem;">Use the form on the left to add dependents</p>
            </div>
            """, unsafe_allow_html=True)


def render_documents_tab(client_id: str):
    """Render the Documents tab."""
    # Document type options (matching the database schema)
    doc_type_options = {
        'will': 'Will',
        'trust': 'Trust Document',
        'poa': 'Power of Attorney',
        'statement': 'Financial Statement',
        'tax_return': 'Tax Return',
        'insurance_policy': 'Insurance Policy',
        'disability_insurance': 'Disability Insurance',
        'other': 'Other Document'
    }
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 1rem;">
            <h3 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0 0 0.5rem 0;">Upload New Document</h3>
            <p style="font-size: 0.8rem; color: #64748B; margin: 0;">Supported: PDF, DOC, DOCX, JPG, PNG, TXT</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Document type selector
        doc_type = st.selectbox(
            "Document Type",
            options=list(doc_type_options.keys()),
            format_func=lambda x: doc_type_options[x]
        )
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'],
            help="Select a document to upload"
        )
        
        if uploaded_file is not None:
            # Calculate file hash
            file_content = uploaded_file.read()
            file_hash = calculate_file_hash(file_content)
            uploaded_file.seek(0)  # Reset file pointer
            
            if st.button("📤 Upload Document", use_container_width=True):
                try:
                    # Remove any existing document with the same hash for this client
                    existing_doc = get_document_by_hash(file_hash, client_id)
                    if existing_doc:
                        old_path = existing_doc.get('storage_path')
                        if old_path and Path(old_path).exists():
                            Path(old_path).unlink()
                        delete_document(existing_doc['id'])
                    
                    # Create client-specific directory
                    client_dir = UPLOADS_DIR / client_id
                    client_dir.mkdir(exist_ok=True)
                    
                    # Generate unique filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    safe_filename = f"{timestamp}_{uploaded_file.name}"
                    file_path = client_dir / safe_filename
                    
                    # Save file to disk (best-effort for local usage)
                    try:
                        with open(file_path, 'wb') as f:
                            f.write(file_content)
                        disk_path = str(file_path)
                    except OSError:
                        disk_path = None
                    
                    # Add document record to database (with file bytes)
                    doc_data = {
                        'document_type': doc_type,
                        'file_name': uploaded_file.name,
                        'file_hash': file_hash,
                        'storage_path': disk_path,
                        'file_content': file_content,
                        'uploaded_by': 'user'
                    }
                    add_document(client_id, doc_data)
                    
                    st.success(f"✅ Document '{uploaded_file.name}' uploaded successfully!")
                    st.rerun()
                except Exception as e:
                        st.error(f"Error uploading document: {e}")
    
    with col2:
        # Display existing documents
        documents = get_client_documents(client_id)
        
        st.markdown("""
        <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 1rem;">
            <h3 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0 0 0.5rem 0;">Uploaded Documents</h3>
            <p style="font-size: 0.8rem; color: #64748B; margin: 0;">View and manage your documents</p>
        </div>
        """, unsafe_allow_html=True)
        
        if documents:
            for doc in documents:
                doc_id = doc['id']
                doc_type_label = doc_type_options.get(doc['document_type'], 'Document')
                upload_time = doc.get('upload_time', 'Unknown')
                
                # Format upload time
                try:
                    if isinstance(upload_time, str):
                        upload_dt = datetime.fromisoformat(upload_time)
                        upload_time_formatted = upload_dt.strftime('%b %d, %Y %I:%M %p')
                    else:
                        upload_time_formatted = str(upload_time)
                except:
                    upload_time_formatted = str(upload_time)
                
                with st.expander(f"📄 {doc['file_name']}", expanded=False):
                    st.markdown(f"""
                    <div style="font-size: 0.85rem; color: #475569; margin-bottom: 0.75rem;">
                        <div style="margin-bottom: 0.4rem;"><strong>Type:</strong> {doc_type_label}</div>
                        <div style="margin-bottom: 0.4rem;"><strong>Uploaded:</strong> {upload_time_formatted}</div>
                        <div><strong>File Hash:</strong> <code style="font-size: 0.7rem; background: #F1F5F9; padding: 0.1rem 0.3rem; border-radius: 4px;">{doc.get('file_hash', 'N/A')[:20]}...</code></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    bcol1, bcol2 = st.columns(2)
                    
                    # Download button — try disk first, fall back to DB content
                    storage_path = doc.get('storage_path')
                    file_data = None
                    if storage_path and Path(storage_path).exists():
                        with open(storage_path, 'rb') as f:
                            file_data = f.read()
                    else:
                        file_data = get_document_content(doc_id)

                    if file_data:
                        with bcol1:
                            st.download_button(
                                label="⬇️ Download",
                                data=file_data,
                                file_name=doc['file_name'],
                                key=f"download_{doc_id}",
                                use_container_width=True
                            )
                    
                    # Delete button
                    with bcol2:
                        if st.button("🗑️ Delete", key=f"del_doc_{doc_id}", use_container_width=True):
                            try:
                                # Delete file from disk
                                if storage_path and Path(storage_path).exists():
                                    Path(storage_path).unlink()
                                
                                # Delete record from database
                                delete_document(doc_id)
                                st.success("Document deleted")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting document: {e}")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #94A3B8;">
                <p style="font-size: 0.9rem;">No documents uploaded yet</p>
                <p style="font-size: 0.8rem;">Use the form on the left to upload documents</p>
            </div>
            """, unsafe_allow_html=True)

def render_disability_analysis_tab(client_id: str, client_data):
    """Render the Disability Analysis tab."""
    st.markdown("""
    <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 1rem;">
        <h3 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0 0 0.5rem 0;">Disability Insurance Analysis</h3>
        <p style="font-size: 0.8rem; color: #64748B; margin: 0;">Analyze uploaded disability insurance policies and project cash flows.</p>
    </div>
    """, unsafe_allow_html=True)
    
    documents = get_client_documents(client_id)
    disability_docs = [doc for doc in documents if doc.get('document_type') == 'disability_insurance']
    
    if not disability_docs:
        st.info("No Disability Insurance documents found. Please upload one in the Documents tab.")
        return
        
    selected_doc = st.selectbox(
        "Select Disability Insurance Document",
        options=disability_docs,
        format_func=lambda x: x['file_name']
    )
    
    if selected_doc:
        doc_id = selected_doc['id']
        
        # Retrieve file content: try disk first, then fall back to database
        storage_path = selected_doc.get('storage_path')
        file_bytes = None
        if storage_path and Path(storage_path).exists():
            with open(storage_path, 'rb') as f:
                file_bytes = f.read()
        else:
            file_bytes = get_document_content(doc_id)
        
        if not file_bytes:
            st.error("Document content not available. Please re-upload the document in the Documents tab.")
            return
            
        if st.button("Analyze Document", type="primary"):
            with st.spinner("Extracting policy details using Gemini..."):
                try:
                    from logic.llm_extractor import extract_disability_policy
                    policy = extract_disability_policy(file_bytes, selected_doc.get('file_name', 'document.pdf'))
                    st.session_state[f'disability_policy_{client_id}'] = policy
                    st.success("Policy details extracted successfully!")
                except Exception as e:
                    st.error(f"Error extracting policy details: {e}")
                    return
                    
        policy = st.session_state.get(f'disability_policy_{client_id}')
        if policy:
            st.markdown("### Extracted Policy Details")
            st.json(policy.model_dump())
            
            st.markdown("### Cash Flow Projection")
            with st.form("disability_inputs"):
                col1, col2 = st.columns(2)
                with col1:
                    annual_base_salary = st.number_input("Annual Base Salary", value=float(client_data.income.total_annual_income))
                    annual_bonus = st.number_input("Annual Bonus", value=0.0)
                    aime = st.number_input("AIME (Average Indexed Monthly Earnings)", value=5000.0)
                with col2:
                    date_of_disability = st.date_input("Date of Disability", value=datetime.now().date())
                    monthly_workers_comp = st.number_input("Monthly Workers Comp", value=0.0)
                    
                submit_calc = st.form_submit_button("Calculate Cash Flow")
                
            if submit_calc:
                try:
                    from logic.disability import DisabilityCashFlowModel
                    
                    # Parse DOB
                    client_row = get_client_by_id(client_id)
                    dob_str = client_row.get('date_of_birth') if client_row else None
                    try:
                        if dob_str:
                            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                        else:
                            dob = datetime.now().date() - relativedelta(years=client_data.profile.age)
                    except:
                        dob = datetime.now().date() - relativedelta(years=client_data.profile.age)
                        
                    user_inputs = {
                        'annual_base_salary': annual_base_salary,
                        'annual_bonus': annual_bonus,
                        'aime': aime,
                        'date_of_disability': date_of_disability,
                        'monthly_workers_comp': monthly_workers_comp,
                        'date_of_birth': dob
                    }
                    
                    model = DisabilityCashFlowModel(policy, user_inputs)
                    df = model.generate_timeline()
                    
                    st.dataframe(df, use_container_width=True)
                    
                    # Plot
                    st.line_chart(df[['Gross_Benefit', 'Total_Offsets', 'Net_Payout']])
                except Exception as e:
                    st.error(f"Error calculating cash flow: {e}")


def render_risk_assessment_tab(client_id: str, client_data):
    """Render the unified Risk Assessment tab combining willingness and tolerance."""
    from logic.risk_willingness import get_questions, get_categories, score_survey, CATEGORIES
    from logic.risk_tolerance import (
        EMPLOYMENT_TYPES,
        calculate_risk_tolerance,
        derive_values_from_client_data,
    )
    from logic.risk_assessment import (
        compute_unified_score,
        ASSET_CLASS_LABELS,
        PROFILE_LABELS,
        PROFILE_ORDER,
        ASSET_ALLOCATIONS,
        TOTAL_EQUITY,
    )

    st.markdown("""
    <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 1rem;">
        <h3 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0 0 0.5rem 0;">Risk Assessment</h3>
        <p style="font-size: 0.8rem; color: #64748B; margin: 0;">
            Combined evaluation of psychological risk <strong>willingness</strong> and objective risk-taking <strong>ability</strong> (tolerance).
            Complete both sections below, then view your unified risk profile and recommended asset allocation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ───────────────────────────────────────────────
    # Section 1: Risk Willingness Survey
    # ───────────────────────────────────────────────
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(5,150,105,0.10) 0%, rgba(2,132,199,0.10) 100%);
                padding: 1.25rem; border-radius: 12px; margin-bottom: 1rem;
                border-left: 4px solid #059669;">
        <h3 style="font-size: 1.05rem; font-weight: 600; color: #1E293B; margin: 0;">Part 1 — Risk Willingness</h3>
        <p style="font-size: 0.8rem; color: #64748B; margin: 0.25rem 0 0 0;">Psychological and emotional comfort with investment risk (10-question survey).</p>
    </div>
    """, unsafe_allow_html=True)

    _render_risk_willingness_section(client_id)

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # ───────────────────────────────────────────────
    # Section 2: Risk Tolerance
    # ───────────────────────────────────────────────
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(2,132,199,0.10) 0%, rgba(124,58,237,0.10) 100%);
                padding: 1.25rem; border-radius: 12px; margin-bottom: 1rem;
                border-left: 4px solid #0284C7;">
        <h3 style="font-size: 1.05rem; font-weight: 600; color: #1E293B; margin: 0;">Part 2 — Risk Tolerance (Ability)</h3>
        <p style="font-size: 0.8rem; color: #64748B; margin: 0.25rem 0 0 0;">Objective risk-taking ability based on measurable financial factors.</p>
    </div>
    """, unsafe_allow_html=True)

    _render_risk_tolerance_section(client_id, client_data)

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # ───────────────────────────────────────────────
    # Section 3: Combined Score & Allocation
    # ───────────────────────────────────────────────
    latest_willingness = get_latest_risk_willingness_survey(client_id)
    latest_tolerance = get_latest_risk_tolerance_assessment(client_id)

    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(124,58,237,0.10) 0%, rgba(219,39,119,0.10) 100%);
                padding: 1.25rem; border-radius: 12px; margin-bottom: 1rem;
                border-left: 4px solid #7C3AED;">
        <h3 style="font-size: 1.05rem; font-weight: 600; color: #1E293B; margin: 0;">Part 3 — Unified Risk Profile & Asset Allocation</h3>
        <p style="font-size: 0.8rem; color: #64748B; margin: 0.25rem 0 0 0;">
            Combined score = <code>lower_score × 0.80 + higher_score × 0.20</code>.
            The more conservative dimension dominates.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not latest_willingness or not latest_tolerance:
        missing = []
        if not latest_willingness:
            missing.append("Risk Willingness survey")
        if not latest_tolerance:
            missing.append("Risk Tolerance assessment")
        st.warning(f"Please complete the following before the unified profile can be calculated: **{', '.join(missing)}**")
        return

    willingness_score = latest_willingness.get("normalized_score", 0)
    tolerance_score = latest_tolerance.get("normalized_score", 0)

    combined = compute_unified_score(willingness_score, tolerance_score)

    # Auto-save combined result
    save_risk_assessment_result(client_id, combined)

    _render_unified_results(combined, willingness_score, tolerance_score)


# ───────────────────────────────────────────────
# Sub-renderers for the Risk Assessment tab
# ───────────────────────────────────────────────

def _render_risk_willingness_section(client_id: str):
    """Render the Risk Willingness survey section inside the combined tab."""
    from logic.risk_willingness import get_questions, get_categories, score_survey

    existing_survey = get_latest_risk_willingness_survey(client_id)

    previous_answers: Dict[str, str] = {}
    if existing_survey:
        saved_answers = existing_survey.get("answers", {})
        for q_id, ans_detail in saved_answers.items():
            if isinstance(ans_detail, dict):
                previous_answers[q_id] = ans_detail.get("selected", "")
            else:
                previous_answers[q_id] = str(ans_detail)

    questions = get_questions()
    categories = get_categories()

    with st.form(key="risk_willingness_form"):
        survey_answers = {}

        for cat_key, cat_info in categories.items():
            cat_label = cat_info["label"]
            cat_desc = cat_info["description"]

            st.markdown(f"""
            <div style="background: rgba(5,150,105,0.06); padding: 0.75rem 1rem; border-radius: 8px; margin: 1rem 0 0.75rem 0;
                        border-left: 3px solid #059669;">
                <h4 style="font-size: 0.9rem; font-weight: 600; color: #1E293B; margin: 0;">{cat_label}</h4>
                <p style="font-size: 0.7rem; color: #64748B; margin: 0.2rem 0 0 0;">{cat_desc}</p>
            </div>
            """, unsafe_allow_html=True)

            for q_id in cat_info["questions"]:
                q = questions[q_id]
                q_number = q_id.replace("Q", "")

                st.markdown(f"""
                <div style="font-size: 0.85rem; font-weight: 500; color: #1E293B; margin: 0.75rem 0 0.3rem 0;">
                    <span style="color: #059669; font-weight: 600;">Q{q_number}.</span> {q['prompt']}
                </div>
                """, unsafe_allow_html=True)

                options = ["— Select an answer —"] + [c["text"] for c in q["choices"]]

                default_index = 0
                prev_key = previous_answers.get(q_id)
                if prev_key:
                    for idx, choice in enumerate(q["choices"]):
                        if choice["key"] == prev_key:
                            default_index = idx + 1
                            break

                selected_idx = st.selectbox(
                    f"Q{q_number}", options=options, index=default_index,
                    key=f"rw_{q_id}", label_visibility="collapsed",
                )

                if selected_idx != "— Select an answer —":
                    for choice in q["choices"]:
                        if choice["text"] == selected_idx:
                            survey_answers[q_id] = choice["key"]
                            break

        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("📊 Calculate Risk Willingness Score", use_container_width=True)

    if submitted:
        missing = [q_id for q_id in questions if q_id not in survey_answers]
        if missing:
            missing_nums = ", ".join(q.replace("Q", "") for q in sorted(missing))
            st.error(f"Please answer all questions. Missing: Q{missing_nums}")
            return

        try:
            result = score_survey(survey_answers)
            save_risk_willingness_survey(client_id, result)
            st.success("✅ Risk willingness survey completed and saved!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    latest_survey = get_latest_risk_willingness_survey(client_id)
    if latest_survey:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        _render_survey_results(latest_survey)


def _render_risk_tolerance_section(client_id: str, client_data):
    """Render the Risk Tolerance form section inside the combined tab."""
    from logic.risk_tolerance import (
        EMPLOYMENT_TYPES,
        calculate_risk_tolerance,
        derive_values_from_client_data,
    )

    calc = derive_values_from_client_data(client_data, client_id)
    existing = get_latest_risk_tolerance_assessment(client_id)

    def _default(saved_key, calc_key, cast=float):
        if existing:
            val = existing.get(saved_key)
            if val is not None:
                return cast(val)
        return cast(calc.get(calc_key, 0))

    emp_keys = [e["key"] for e in EMPLOYMENT_TYPES]
    emp_labels = {e["key"]: e["label"] for e in EMPLOYMENT_TYPES}

    col_form, col_calc = st.columns([3, 2])

    with col_calc:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(2,132,199,0.06) 0%, rgba(5,150,105,0.06) 100%);
                    padding: 1.25rem; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 1rem;">
            <h4 style="font-size: 0.95rem; font-weight: 600; color: #1E293B; margin: 0 0 0.75rem 0;">📊 Calculated Values</h4>
            <p style="font-size: 0.75rem; color: #64748B; margin: 0 0 1rem 0;">Derived from existing client data. Use as reference.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1rem; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 0.75rem;">
            <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Time Horizon</div>
            <div style="font-size: 0.85rem; color: #1E293B;">Current Age: <strong>{calc['current_age']}</strong> · Planning Age: <strong>{calc['planning_age']}</strong> · Years: <strong>{max(0, calc['planning_age'] - calc['current_age'])}</strong></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1rem; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 0.75rem;">
            <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Liquidity</div>
            <div style="font-size: 0.85rem; color: #1E293B;">Liquid: <strong>${calc['liquid_savings']:,.0f}</strong> · Expenses: <strong>${calc['monthly_expenses']:,.0f}</strong>/mo · Emergency: <strong>{calc['emergency_months']:.1f}</strong> months</div>
        </div>
        """, unsafe_allow_html=True)

        dti_calc = (calc['monthly_debt'] / calc['gross_monthly_income'] * 100) if calc['gross_monthly_income'] > 0 else 0
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1rem; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 0.75rem;">
            <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Debt Burden</div>
            <div style="font-size: 0.85rem; color: #1E293B;">Debt: <strong>${calc['monthly_debt']:,.0f}</strong>/mo · Income: <strong>${calc['gross_monthly_income']:,.0f}</strong>/mo · DTI: <strong>{dti_calc:.1f}%</strong></div>
        </div>
        """, unsafe_allow_html=True)

        savings_rate_calc = ((calc['monthly_income'] - calc['monthly_expenses'] - calc['monthly_debt']) / calc['monthly_income'] * 100) if calc['monthly_income'] > 0 else 0
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1rem; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 0.75rem;">
            <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Income & Savings</div>
            <div style="font-size: 0.85rem; color: #1E293B;">Type: <strong>{emp_labels.get(calc['employment_type'], calc['employment_type'])}</strong> · Savings Rate: <strong>{savings_rate_calc:.1f}%</strong></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1rem; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 0.75rem;">
            <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Dependents</div>
            <div style="font-size: 0.85rem; color: #1E293B;">Count: <strong>{calc['num_dependents']}</strong> · Dual Income: <strong>{'Yes' if calc['dual_income'] else 'No'}</strong></div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📋 Use All Calculated Values", key="rt_copy_all", use_container_width=True):
            st.session_state['rt_use_calculated'] = True
            st.rerun()

    use_calc = st.session_state.pop('rt_use_calculated', False)

    with col_form:
        with st.form(key="risk_tolerance_form"):
            st.markdown("""
            <div style="background: rgba(5,150,105,0.06); padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 0.75rem; border-left: 3px solid #059669;">
                <h4 style="font-size: 0.9rem; font-weight: 600; color: #1E293B; margin: 0;">1. Time Horizon <span style="font-weight:400; color:#64748B;">(25 pts)</span></h4>
            </div>
            """, unsafe_allow_html=True)

            planning_age = st.number_input(
                "Planning Age", min_value=int(calc['current_age']) + 1, max_value=120,
                value=int(calc['planning_age']) if use_calc else int(_default('planning_age', 'planning_age', int)),
                step=1, key="rt_planning_age",
            )

            st.markdown("""
            <div style="background: rgba(2,132,199,0.06); padding: 0.75rem 1rem; border-radius: 8px; margin: 1rem 0 0.75rem 0; border-left: 3px solid #0284C7;">
                <h4 style="font-size: 0.9rem; font-weight: 600; color: #1E293B; margin: 0;">2. Liquidity <span style="font-weight:400; color:#64748B;">(20 pts)</span></h4>
            </div>
            """, unsafe_allow_html=True)

            emergency_months = st.number_input(
                "Emergency Months", min_value=0.0, max_value=120.0,
                value=float(calc['emergency_months']) if use_calc else float(_default('emergency_months', 'emergency_months')),
                step=0.5, format="%.1f", key="rt_emergency_months",
            )

            st.markdown("""
            <div style="background: rgba(217,119,6,0.06); padding: 0.75rem 1rem; border-radius: 8px; margin: 1rem 0 0.75rem 0; border-left: 3px solid #D97706;">
                <h4 style="font-size: 0.9rem; font-weight: 600; color: #1E293B; margin: 0;">3. Debt Burden — DTI <span style="font-weight:400; color:#64748B;">(15 pts)</span></h4>
            </div>
            """, unsafe_allow_html=True)

            rt_col1, rt_col2 = st.columns(2)
            with rt_col1:
                monthly_debt = st.number_input(
                    "Monthly Debt ($)", min_value=0.0,
                    value=float(calc['monthly_debt']) if use_calc else float(_default('monthly_debt', 'monthly_debt')),
                    step=100.0, format="%.0f", key="rt_monthly_debt",
                )
            with rt_col2:
                gross_monthly_income = st.number_input(
                    "Gross Monthly Income ($)", min_value=0.0,
                    value=float(calc['gross_monthly_income']) if use_calc else float(_default('gross_monthly_income', 'gross_monthly_income')),
                    step=100.0, format="%.0f", key="rt_gross_monthly_income",
                )

            st.markdown("""
            <div style="background: rgba(124,58,237,0.06); padding: 0.75rem 1rem; border-radius: 8px; margin: 1rem 0 0.75rem 0; border-left: 3px solid #7C3AED;">
                <h4 style="font-size: 0.9rem; font-weight: 600; color: #1E293B; margin: 0;">4. Income Stability & Savings <span style="font-weight:400; color:#64748B;">(15 pts)</span></h4>
            </div>
            """, unsafe_allow_html=True)

            default_emp = calc['employment_type'] if use_calc else (
                existing.get('employment_type', calc['employment_type']) if existing else calc['employment_type']
            )
            emp_index = emp_keys.index(default_emp) if default_emp in emp_keys else 1

            employment_type_input = st.selectbox(
                "Employment Type", options=emp_keys, index=emp_index,
                format_func=lambda x: emp_labels.get(x, x), key="rt_employment_type",
            )

            rt_col3, rt_col4 = st.columns(2)
            with rt_col3:
                monthly_income_input = st.number_input(
                    "Monthly Income ($)", min_value=0.0,
                    value=float(calc['monthly_income']) if use_calc else float(_default('monthly_income', 'monthly_income')),
                    step=100.0, format="%.0f", key="rt_monthly_income",
                )
            with rt_col4:
                monthly_expenses_input = st.number_input(
                    "Monthly Expenses ($)", min_value=0.0,
                    value=float(calc['monthly_expenses']) if use_calc else float(_default('monthly_expenses', 'monthly_expenses')),
                    step=100.0, format="%.0f", key="rt_monthly_expenses",
                )

            st.markdown("""
            <div style="background: rgba(219,39,119,0.06); padding: 0.75rem 1rem; border-radius: 8px; margin: 1rem 0 0.75rem 0; border-left: 3px solid #DB2777;">
                <h4 style="font-size: 0.9rem; font-weight: 600; color: #1E293B; margin: 0;">5. Dependents <span style="font-weight:400; color:#64748B;">(15 pts)</span></h4>
            </div>
            """, unsafe_allow_html=True)

            rt_col5, rt_col6 = st.columns(2)
            with rt_col5:
                num_dependents = st.number_input(
                    "Financial Dependents", min_value=0, max_value=20,
                    value=int(calc['num_dependents']) if use_calc else int(_default('num_dependents', 'num_dependents', int)),
                    step=1, key="rt_num_dependents",
                )
            with rt_col6:
                default_dual = calc['dual_income'] if use_calc else (
                    bool(existing.get('dual_income', calc['dual_income'])) if existing else calc['dual_income']
                )
                dual_income = st.selectbox(
                    "Dual Income?", options=[True, False],
                    index=0 if default_dual else 1,
                    format_func=lambda x: "Yes" if x else "No", key="rt_dual_income",
                )

            st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("📊 Calculate Risk Tolerance Score", use_container_width=True)

        if submitted:
            try:
                result = calculate_risk_tolerance(
                    current_age=calc['current_age'],
                    planning_age=int(planning_age),
                    emergency_months=float(emergency_months),
                    monthly_debt=float(monthly_debt),
                    gross_monthly_income=float(gross_monthly_income),
                    employment_type=employment_type_input,
                    monthly_income=float(monthly_income_input),
                    monthly_expenses=float(monthly_expenses_input),
                    num_dependents=int(num_dependents),
                    dual_income=bool(dual_income),
                )
                save_risk_tolerance_assessment(client_id, result)
                st.success("✅ Risk tolerance assessment completed and saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    latest = get_latest_risk_tolerance_assessment(client_id)
    if latest:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        _render_risk_tolerance_results(latest)


def _render_unified_results(combined: dict, willingness_score: float, tolerance_score: float):
    """Render the unified risk profile, scores comparison, and allocation table."""
    from logic.risk_assessment import ASSET_CLASS_LABELS, PROFILE_LABELS, PROFILE_ORDER, ASSET_ALLOCATIONS, TOTAL_EQUITY

    unified = combined["unified_score"]
    profile_label = combined["profile_label"]
    profile_key = combined["profile_key"]
    allocation = combined["allocation"]
    total_eq = combined["total_equity"]
    lower_dim = combined["lower_dimension"]

    # Color for unified score
    if unified >= 67:
        u_color = "#DC2626"
    elif unified >= 45:
        u_color = "#059669"
    elif unified >= 23:
        u_color = "#D97706"
    else:
        u_color = "#0284C7"

    # ── Score cards ──
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1.25rem; border-radius: 12px; border: 1px solid #E2E8F0; text-align: center;">
            <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Willingness Score</div>
            <div style="font-size: 2rem; font-weight: 700; color: #059669; margin: 0.4rem 0;">{willingness_score:.0f}</div>
            <div style="font-size: 0.65rem; color: #94A3B8;">out of 100</div>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1.25rem; border-radius: 12px; border: 1px solid #E2E8F0; text-align: center;">
            <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Tolerance Score</div>
            <div style="font-size: 2rem; font-weight: 700; color: #0284C7; margin: 0.4rem 0;">{tolerance_score:.0f}</div>
            <div style="font-size: 0.65rem; color: #94A3B8;">out of 100</div>
        </div>
        """, unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1.25rem; border-radius: 12px; border: 2px solid {u_color}; text-align: center;">
            <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Unified Score</div>
            <div style="font-size: 2rem; font-weight: 700; color: {u_color}; margin: 0.4rem 0;">{unified:.0f}</div>
            <div style="font-size: 0.65rem; color: #94A3B8;">lower × 0.80 + higher × 0.20</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # ── Constraint note ──
    dim_label = "Willingness" if lower_dim == "willingness" else "Tolerance"
    st.markdown(f"""
    <div style="padding: 0.75rem 1rem; background: rgba(217,119,6,0.06); border-radius: 8px; border-left: 3px solid #D97706; margin-bottom: 1rem;">
        <span style="font-size: 0.825rem; color: #334155;">
            ⚠️ The <strong>binding constraint</strong> is <strong>{dim_label}</strong> (score {combined['lower_score']:.0f}).
            This dimension receives 80% weight in the combined score.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Profile badge ──
    st.markdown(f"""
    <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; text-align: center; margin-bottom: 1.5rem;">
        <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Recommended Portfolio Profile</div>
        <div style="font-size: 1.75rem; font-weight: 700; color: {u_color}; margin: 0.5rem 0;">{profile_label}</div>
        <div style="font-size: 0.8rem; color: #64748B;">{total_eq:.0f}% Total Equity · {100 - total_eq:.0f}% Defensive</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Allocation table ──
    st.markdown("""
    <div style="margin-bottom: 0.75rem;">
        <h4 style="font-size: 0.95rem; font-weight: 600; color: #1E293B; margin: 0;">Recommended Asset Allocation</h4>
    </div>
    """, unsafe_allow_html=True)

    # Equity sleeve
    st.markdown("""
    <div style="font-size: 0.8rem; font-weight: 600; color: #1E293B; margin: 0.75rem 0 0.5rem 0; text-transform: uppercase; letter-spacing: 0.03em;">Equity Sleeve</div>
    """, unsafe_allow_html=True)
    eq_cols = st.columns(2)
    eq_items = [("global_equity", "#3B82F6"), ("home_country", "#10B981")]
    for i, (key, bar_color) in enumerate(eq_items):
        with eq_cols[i]:
            pct = allocation[key]
            st.markdown(f"""
            <div style="background: #FFFFFF; padding: 1rem; border-radius: 10px; border: 1px solid #E2E8F0;">
                <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 0.3rem;">{ASSET_CLASS_LABELS[key]}</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {bar_color};">{pct}%</div>
                <div style="height: 6px; background: #E2E8F0; border-radius: 3px; overflow: hidden; margin-top: 0.5rem;">
                    <div style="height: 100%; width: {pct}%; background: {bar_color}; border-radius: 3px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Defensive sleeve
    st.markdown("""
    <div style="font-size: 0.8rem; font-weight: 600; color: #1E293B; margin: 1rem 0 0.5rem 0; text-transform: uppercase; letter-spacing: 0.03em;">Defensive Sleeve</div>
    """, unsafe_allow_html=True)
    def_cols = st.columns(3)
    def_items = [("fixed_income", "#F59E0B"), ("cash", "#EF4444"), ("alternatives", "#6B7280")]
    for i, (key, bar_color) in enumerate(def_items):
        with def_cols[i]:
            pct = allocation[key]
            st.markdown(f"""
            <div style="background: #FFFFFF; padding: 1rem; border-radius: 10px; border: 1px solid #E2E8F0;">
                <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 0.3rem;">{ASSET_CLASS_LABELS[key]}</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {bar_color};">{pct}%</div>
                <div style="height: 6px; background: #E2E8F0; border-radius: 3px; overflow: hidden; margin-top: 0.5rem;">
                    <div style="height: 100%; width: {min(100, pct)}%; background: {bar_color}; border-radius: 3px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # ── Full profile comparison table ──
    with st.expander("📋 View All Portfolio Profiles", expanded=False):
        header = "| Asset Class | " + " | ".join(PROFILE_LABELS[p] for p in PROFILE_ORDER) + " |"
        separator = "|---|" + "|".join(["---:" for _ in PROFILE_ORDER]) + "|"
        rows = []
        for ac_key, ac_label in ASSET_CLASS_LABELS.items():
            row = f"| {ac_label} | " + " | ".join(
                f"{ASSET_ALLOCATIONS[p][ac_key]}%" for p in PROFILE_ORDER
            ) + " |"
            rows.append(row)
        total_row = "| **Total Equity** | " + " | ".join(
            f"**{TOTAL_EQUITY[p]:.0f}%**" for p in PROFILE_ORDER
        ) + " |"
        rows.append(total_row)

        table_md = "\n".join([header, separator] + rows)
        st.markdown(table_md)



def _render_survey_results(result: dict):
    """Render the scored survey results."""
    normalized = result.get("normalized_score", 0)
    level = result.get("willingness_level", "moderate")
    label = result.get("willingness_label", "Balanced")
    
    # Color mapping
    level_colors = {
        "low": "#0284C7",
        "moderate": "#D97706",
        "moderately_high": "#059669",
        "high": "#DC2626",
    }
    color = level_colors.get(level, "#64748B")
    
    # Main score display
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; text-align: center;">
            <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Willingness Score</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: {color}; line-height: 1.2; margin: 0.5rem 0;">{normalized:.0f}</div>
            <div style="font-size: 0.7rem; color: #94A3B8;">out of 100</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; text-align: center;">
            <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Risk Profile</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: {color}; margin: 0.5rem 0;">{label}</div>
            <div style="font-size: 0.7rem; color: #94A3B8;">{level.replace('_', ' ').title()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Category breakdown
    st.markdown("""
    <div style="margin-bottom: 0.75rem;">
        <h4 style="font-size: 0.95rem; font-weight: 600; color: #1E293B; margin: 0;">Category Breakdown</h4>
    </div>
    """, unsafe_allow_html=True)
    
    cat_scores = result.get("category_scores", {})
    cat_cols = st.columns(3)
    
    cat_labels = {
        "loss_aversion": ("Loss Aversion", "🛡️"),
        "self_assessment": ("Self-Assessment", "🪞"),
        "experience_gambles": ("Experience & Gambles", "🎲"),
    }
    
    for i, (cat_key, (cat_name, cat_icon)) in enumerate(cat_labels.items()):
        with cat_cols[i]:
            cat = cat_scores.get(cat_key, {})
            cat_norm = cat.get("normalized", 0)
            cat_raw = cat.get("raw", 0)
            cat_max = cat.get("max", 0)
            
            if cat_norm >= 75:
                bar_color = "#DC2626"
            elif cat_norm >= 50:
                bar_color = "#059669"
            elif cat_norm >= 25:
                bar_color = "#D97706"
            else:
                bar_color = "#0284C7"
            
            st.markdown(f"""
            <div style="background: #FFFFFF; padding: 1.25rem; border-radius: 12px; border: 1px solid #E2E8F0;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.25rem;">{cat_icon}</span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: #1E293B;">{cat_name}</span>
                </div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {bar_color};">{cat_norm:.0f}<span style="font-size: 0.8rem; color: #94A3B8;">/100</span></div>
                <div style="font-size: 0.7rem; color: #94A3B8; margin-bottom: 0.5rem;">Raw: {cat_raw} / {cat_max}</div>
                <div style="height: 6px; background: #E2E8F0; border-radius: 3px; overflow: hidden;">
                    <div style="height: 100%; width: {min(100, cat_norm)}%; background: {bar_color}; border-radius: 3px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Consistency flags
    flags = result.get("flags", [])
    if flags:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="margin-bottom: 0.5rem;">
            <h4 style="font-size: 0.95rem; font-weight: 600; color: #D97706; margin: 0;">⚠️ Advisor Alerts</h4>
        </div>
        """, unsafe_allow_html=True)
        
        for flag_text in flags:
            st.markdown(f"""
            <div style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.875rem 1rem; 
                        background: rgba(217, 119, 6, 0.06); border-radius: 8px; margin-bottom: 0.5rem;
                        border-left: 3px solid #D97706; border: 1px solid rgba(217, 119, 6, 0.2);
                        border-left: 3px solid #D97706;">
                <span style="font-size: 0.825rem; color: #334155; line-height: 1.5;">{flag_text}</span>
            </div>
            """, unsafe_allow_html=True)



def _render_risk_tolerance_results(result: dict):
    """Render scored risk tolerance results."""
    total = result.get("total_score", 0)
    max_score = result.get("max_score", 90)
    normalized = result.get("normalized_score", 0)
    level = result.get("tolerance_level", "moderate")
    label = result.get("tolerance_label", "Moderate")
    components = result.get("components", {})

    level_colors = {
        "low": "#0284C7",
        "low_moderate": "#D97706",
        "moderate": "#059669",
        "high": "#DC2626",
    }
    color = level_colors.get(level, "#64748B")

    # Main score display
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; text-align: center;">
            <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Total Score</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: {color}; line-height: 1.2; margin: 0.5rem 0;">{total}</div>
            <div style="font-size: 0.7rem; color: #94A3B8;">out of {max_score}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; text-align: center;">
            <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Risk Tolerance Profile</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: {color}; margin: 0.5rem 0;">{label}</div>
            <div style="font-size: 0.7rem; color: #94A3B8;">{normalized:.0f} / 100 normalized</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Component breakdown
    st.markdown("""
    <div style="margin-bottom: 0.75rem;">
        <h4 style="font-size: 0.95rem; font-weight: 600; color: #1E293B; margin: 0;">Component Breakdown</h4>
    </div>
    """, unsafe_allow_html=True)

    component_meta = [
        ("time_horizon", "Time Horizon", "⏳", 25),
        ("liquidity", "Liquidity", "💧", 20),
        ("debt_burden", "Debt Burden", "💳", 15),
        ("income_stability_savings", "Income & Savings", "💼", 15),
        ("dependents", "Dependents", "👨‍👩‍👧‍👦", 15),
    ]

    comp_cols = st.columns(5)
    for i, (key, name, icon, max_pts) in enumerate(component_meta):
        with comp_cols[i]:
            comp = components.get(key, {})
            score = comp.get("score", 0)
            pct = (score / max_pts * 100) if max_pts > 0 else 0

            if pct >= 75:
                bar_color = "#059669"
            elif pct >= 50:
                bar_color = "#0284C7"
            elif pct >= 25:
                bar_color = "#D97706"
            else:
                bar_color = "#DC2626"

            # Build detail text based on component
            detail = ""
            if key == "time_horizon":
                detail = f"Planning age: {comp.get('planning_age', '—')}"
            elif key == "liquidity":
                detail = f"{comp.get('emergency_months', 0):.1f} months"
            elif key == "debt_burden":
                detail = f"DTI: {comp.get('dti_pct', 0):.1f}%"
            elif key == "income_stability_savings":
                stab = comp.get("stability", {})
                sav = comp.get("savings", {})
                detail = f"Stability: {stab.get('score', 0)}/8 | Savings: {sav.get('score', 0)}/7"
            elif key == "dependents":
                detail = f"{comp.get('num_dependents', 0)} dep, {'dual' if comp.get('dual_income') else 'single'}"

            st.markdown(f"""
            <div style="background: #FFFFFF; padding: 1.25rem; border-radius: 12px; border: 1px solid #E2E8F0;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.25rem;">{icon}</span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: #1E293B;">{name}</span>
                </div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {bar_color};">{score}<span style="font-size: 0.8rem; color: #94A3B8;">/{max_pts}</span></div>
                <div style="font-size: 0.7rem; color: #94A3B8; margin-bottom: 0.5rem;">{detail}</div>
                <div style="height: 6px; background: #E2E8F0; border-radius: 3px; overflow: hidden;">
                    <div style="height: 100%; width: {min(100, pct)}%; background: {bar_color}; border-radius: 3px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# Page configuration
st.set_page_config(
    page_title="Financial Health Dashboard",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


def main():
    """Main application entry point."""
    
    # Sidebar for client selection and navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem; border-bottom: 1px solid #E2E8F0;">
            <h2 style="color: #059669; margin: 0; font-size: 1.25rem;">WealthView</h2>
            <p style="color: #64748B; font-size: 0.75rem; margin-top: 0.25rem;">Financial Advisory Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Client selector
        st.markdown("<p style='font-size: 0.875rem; color: #475569; margin-bottom: 0.5rem;'>Select Client</p>", unsafe_allow_html=True)
        clients = get_all_sample_clients()
        client_options = {
            f"{data.profile.name} ({cid})": cid 
            for cid, data in clients.items()
        }
        
        selected_display = st.selectbox(
            "Client",
            options=list(client_options.keys()),
            label_visibility="collapsed"
        )
        selected_client_id = client_options[selected_display]
        client_data = clients[selected_client_id]
        
        # Display client quick info - clean design without icons
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1rem; border-radius: 8px; margin-top: 1rem; border: 1px solid #E2E8F0;">
            <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">Client Profile</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; font-size: 0.8rem;">
                <div>
                    <div style="color: #64748B; font-size: 0.7rem;">Age</div>
                    <div style="color: #1E293B; font-weight: 500;">{client_data.profile.age}</div>
                </div>
                <div>
                    <div style="color: #64748B; font-size: 0.7rem;">Retirement</div>
                    <div style="color: #1E293B; font-weight: 500;">{client_data.profile.retirement_age}</div>
                </div>
                <div>
                    <div style="color: #64748B; font-size: 0.7rem;">Dependents</div>
                    <div style="color: #1E293B; font-weight: 500;">{client_data.profile.dependents}</div>
                </div>
                <div>
                    <div style="color: #64748B; font-size: 0.7rem;">State</div>
                    <div style="color: #1E293B; font-weight: 500;">{client_data.profile.state}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        # Navigation with clickable cards
        st.markdown("<p style='font-size: 0.7rem; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;'>Navigation</p>", unsafe_allow_html=True)
        
        # Initialize session state for selected section
        if 'selected_section' not in st.session_state:
            st.session_state.selected_section = "Overview"
        
        nav_items = [
            ("Overview", "Financial summary and health scores"),
            ("Financial Foundation", "Safety net and debt analysis"),
            ("Cash Flow & Spending", "Income, expenses, and savings"),
            ("Portfolio Health", "Investment allocation and risk"),
            ("Future Planning", "Retirement and goal tracking"),
            ("Estate Readiness", "Legacy and estate documents"),
            ("Profile", "Personal info, dependents & documents")
        ]
        
        for nav_name, nav_desc in nav_items:
            is_active = st.session_state.selected_section == nav_name
            if st.button(
                nav_name,
                key=f"nav_{nav_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.selected_section = nav_name
                st.rerun()
        
        selected_section = st.session_state.selected_section
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 0.7rem; color: #475569; text-align: center;">
            Dashboard v1.0
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    render_header(client_data.profile.name, selected_client_id)
    
    # Initialize calculators with client data
    foundation_calc = FinancialFoundation(client_data)
    cashflow_calc = CashFlowBehavior(client_data, get_historical_expenses(selected_client_id))
    portfolio_calc = PortfolioHealth(client_data)
    planning_calc = FuturePlanning(client_data)
    estate_calc = EstateReadiness(client_data)
    
    # Get all section summaries
    foundation_summary = foundation_calc.get_section_summary()
    cashflow_summary = cashflow_calc.get_section_summary()
    portfolio_summary = portfolio_calc.get_section_summary()
    planning_summary = planning_calc.get_section_summary()
    estate_summary = estate_calc.get_section_summary()
    
    # Calculate overall health score
    all_scores = [
        foundation_summary['overall_score'],
        cashflow_summary['overall_score'],
        portfolio_summary['overall_score'],
        planning_summary['overall_score'],
        estate_summary['overall_score']
    ]
    overall_health_score = sum(all_scores) / len(all_scores)
    
    # Display based on selected section
    if selected_section == "Overview":
        render_overview(
            client_data, 
            overall_health_score,
            foundation_summary,
            cashflow_summary,
            portfolio_summary,
            planning_summary,
            estate_summary
        )
    elif selected_section == "Financial Foundation":
        render_foundation_section(foundation_summary, client_data)
    elif selected_section == "Cash Flow & Spending":
        render_cashflow_section(cashflow_summary, client_data)
    elif selected_section == "Portfolio Health":
        render_portfolio_section(portfolio_summary, client_data)
    elif selected_section == "Future Planning":
        render_planning_section(planning_summary, planning_calc, client_data)
    elif selected_section == "Estate Readiness":
        render_estate_section(estate_summary, client_data)
    elif selected_section == "Profile":
        render_profile_section(selected_client_id, client_data)


def render_overview(client_data, overall_score, foundation, cashflow, portfolio, planning, estate):
    """Render the overview dashboard section."""
    
    # Net worth and overall health
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_net_worth_summary(client_data)
    
    with col2:
        render_health_score_gauge(overall_score, "Overall Financial Health")
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Section score cards
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h3 style="font-size: 1.125rem; font-weight: 600; color: #1E293B; margin: 0; letter-spacing: -0.01em;">Section Health Scores</h3>
        <p style="font-size: 0.8rem; color: #64748B; margin-top: 0.25rem;">Performance breakdown across key financial areas</p>
    </div>
    """, unsafe_allow_html=True)
    
    sections = [
        ("Foundation", "Safety & Debt", foundation),
        ("Cash Flow", "Income & Spending", cashflow),
        ("Portfolio", "Investments", portfolio),
        ("Planning", "Goals & Future", planning),
        ("Estate", "Legacy", estate)
    ]
    
    cols = st.columns(5)
    for i, (title, subtitle, summary) in enumerate(sections):
        with cols[i]:
            score = summary['overall_score']
            status = summary['overall_status']
            color = {
                HealthStatus.EXCELLENT: '#059669',
                HealthStatus.GOOD: '#0284C7',
                HealthStatus.FAIR: '#D97706',
                HealthStatus.POOR: '#EA580C',
                HealthStatus.CRITICAL: '#DC2626'
            }.get(status, '#64748B')
            
            # Calculate progress for visual bar
            progress_pct = min(100, score)
            
            st.markdown(f"""
            <div style="background: #FFFFFF; padding: 1.25rem; border-radius: 12px; border: 1px solid #E2E8F0; 
                        box-shadow: 0 1px 3px rgba(0,0,0,0.05); position: relative; overflow: hidden;">
                <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 3px; background: #F1F5F9;">
                    <div style="height: 100%; width: {progress_pct}%; background: {color}; transition: width 0.3s ease;"></div>
                </div>
                <div style="font-size: 0.8rem; font-weight: 600; color: #1E293B; margin-bottom: 0.125rem;">{title}</div>
                <div style="font-size: 0.65rem; color: #94A3B8; margin-bottom: 0.75rem;">{subtitle}</div>
                <div style="display: flex; align-items: baseline; gap: 0.375rem;">
                    <span style="font-size: 1.75rem; font-weight: 700; color: {color}; line-height: 1;">{score:.0f}</span>
                    <span style="font-size: 0.65rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.03em;">{status.value}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Quick insights row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="margin-bottom: 0.75rem;">
            <h3 style="font-size: 1.125rem; font-weight: 600; color: #1E293B; margin: 0; letter-spacing: -0.01em;">Asset Allocation</h3>
            <p style="font-size: 0.8rem; color: #64748B; margin-top: 0.25rem;">Current portfolio distribution</p>
        </div>
        """, unsafe_allow_html=True)
        allocation_data = {
            'US Stocks': client_data.portfolio_allocation.us_stocks,
            'Int\'l Stocks': client_data.portfolio_allocation.international_stocks,
            'Bonds': client_data.portfolio_allocation.bonds,
            'Real Estate': client_data.portfolio_allocation.real_estate,
            'Cash': client_data.portfolio_allocation.cash,
            'Other': client_data.portfolio_allocation.commodities + 
                    client_data.portfolio_allocation.alternatives +
                    client_data.portfolio_allocation.crypto
        }
        # Filter out zeros
        allocation_data = {k: v for k, v in allocation_data.items() if v > 0}
        render_allocation_chart(allocation_data)
    
    with col2:
        st.markdown("""
        <div style="margin-bottom: 0.75rem;">
            <h3 style="font-size: 1.125rem; font-weight: 600; color: #1E293B; margin: 0; letter-spacing: -0.01em;">Goal Progress</h3>
            <p style="font-size: 0.8rem; color: #64748B; margin-top: 0.25rem;">Tracking towards financial milestones</p>
        </div>
        """, unsafe_allow_html=True)
        goals_data = [
            {
                'name': goal.name,
                'current': goal.current_amount,
                'target': goal.target_amount,
                'priority': goal.priority,
                'status': planning['metrics'].get(f'goal_{goal.goal_id}', 
                         planning['metrics'].get(list(planning['metrics'].keys())[0])).status.value
            }
            for goal in client_data.goals
        ]
        render_goal_progress(goals_data)
    
    # Key recommendations
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h3 style="font-size: 1.125rem; font-weight: 600; color: #1E293B; margin: 0; letter-spacing: -0.01em;">Priority Recommendations</h3>
        <p style="font-size: 0.8rem; color: #64748B; margin-top: 0.25rem;">Action items requiring attention</p>
    </div>
    """, unsafe_allow_html=True)
    
    all_recommendations = []
    for summary in [foundation, cashflow, portfolio, planning, estate]:
        for metric_name, metric in summary['metrics'].items():
            if metric.status in [HealthStatus.POOR, HealthStatus.CRITICAL]:
                for rec in metric.recommendations[:1]:  # Top recommendation per poor metric
                    all_recommendations.append({
                        'text': rec,
                        'severity': 'critical' if metric.status == HealthStatus.CRITICAL else 'poor'
                    })
    
    if all_recommendations:
        for rec in all_recommendations[:5]:  # Show top 5
            color = '#DC2626' if rec['severity'] == 'critical' else '#EA580C'
            st.markdown(f"""
            <div style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.875rem 1rem; 
                        background: #FFFFFF; 
                        border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid {color};
                        border: 1px solid #E2E8F0; border-left: 3px solid {color};">
                <span style="font-size: 0.875rem; color: #334155; line-height: 1.5;">{rec['text']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding: 1rem; background: rgba(5, 150, 105, 0.08); border-radius: 8px; 
                    border: 1px solid rgba(5, 150, 105, 0.2); text-align: center;">
            <span style="font-size: 0.875rem; color: #059669; font-weight: 500;">No critical recommendations — financial health looks good!</span>
        </div>
        """, unsafe_allow_html=True)


def render_foundation_section(summary, client_data):
    """Render Financial Foundation section."""
    render_section_header(
        summary['section_title'],
        summary['section_question'],
        summary['overall_score'],
        summary['overall_status']
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Metrics grid
    render_metric_grid(summary['metrics'], columns=3)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Additional visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Asset Distribution")
        asset_data = {
            'Liquid Cash': client_data.assets.liquid_assets,
            'Investments': client_data.assets.investment_assets,
            'Company Stock': client_data.assets.company_stock_total,
            'Real Estate': client_data.assets.real_estate_primary + client_data.assets.real_estate_investment,
            'Other': client_data.assets.business_equity + client_data.assets.crypto + 
                    client_data.assets.collectibles + client_data.assets.other_assets
        }
        asset_data = {k: v for k, v in asset_data.items() if v > 0}
        render_asset_breakdown_chart(asset_data, "Asset Distribution")
    
    with col2:
        st.markdown("### Liability Breakdown")
        liability_data = {
            'Primary Mortgage': client_data.liabilities.mortgage_primary,
            'Investment Property': client_data.liabilities.mortgage_investment,
            'Auto Loans': client_data.liabilities.auto_loans,
            'Student Loans': client_data.liabilities.student_loans,
            'Credit Cards': client_data.liabilities.credit_cards,
            'Other Debt': client_data.liabilities.personal_loans + 
                         client_data.liabilities.heloc + client_data.liabilities.other_debt
        }
        liability_data = {k: v for k, v in liability_data.items() if v > 0}
        if liability_data:
            render_asset_breakdown_chart(liability_data, "Liability Breakdown")
        else:
            st.info("No liabilities!")


def render_cashflow_section(summary, client_data):
    """Render Cash Flow & Spending section."""
    render_section_header(
        summary['section_title'],
        summary['section_question'],
        summary['overall_score'],
        summary['overall_status']
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Key metrics
    render_metric_grid(summary['metrics'], columns=3)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Expense breakdown
    col1, col2 = st.columns([3, 2])
    
    with col1:
        expense_categories = {
            'Housing': client_data.expenses.housing,
            'Childcare': client_data.expenses.childcare,
            'Transportation': client_data.expenses.transportation,
            'Groceries': client_data.expenses.groceries,
            'Healthcare': client_data.expenses.healthcare,
            'Insurance': client_data.expenses.insurance_premiums,
            'Debt Payments': client_data.expenses.debt_payments,
            'Entertainment': client_data.expenses.entertainment,
            'Dining Out': client_data.expenses.dining_out,
            'Travel': client_data.expenses.travel,
            'Shopping': client_data.expenses.shopping,
            'Subscriptions': client_data.expenses.subscriptions,
            'Other': client_data.expenses.other + client_data.expenses.utilities
        }
        expense_categories = {k: v for k, v in expense_categories.items() if v > 0}
        render_expense_breakdown(expense_categories, client_data.income.monthly_income)
    
    with col2:
        st.markdown("""
        <div style="margin-bottom: 0.75rem;">
            <h4 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0;">Income vs Expenses</h4>
        </div>
        """, unsafe_allow_html=True)
        monthly_income = client_data.income.monthly_income
        monthly_expenses = client_data.expenses.total_monthly_expenses
        monthly_savings = monthly_income - monthly_expenses
        
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="margin-bottom: 1.5rem;">
                <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase;">Monthly Income</div>
                <div style="font-size: 1.75rem; font-weight: 700; color: #059669;">${monthly_income:,.0f}</div>
            </div>
            <div style="margin-bottom: 1.5rem;">
                <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase;">Monthly Expenses</div>
                <div style="font-size: 1.75rem; font-weight: 700; color: #EA580C;">${monthly_expenses:,.0f}</div>
            </div>
            <div style="padding-top: 1rem; border-top: 1px solid #E2E8F0;">
                <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase;">Monthly Savings</div>
                <div style="font-size: 1.75rem; font-weight: 700; color: {'#059669' if monthly_savings > 0 else '#DC2626'};">
                    ${monthly_savings:,.0f}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Expense breakdown by type
        fixed = client_data.expenses.fixed_expenses
        discretionary = client_data.expenses.discretionary_expenses
        
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; margin-top: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="font-size: 0.875rem; color: #1E293B; margin-bottom: 1rem; font-weight: 600;">Expense Split</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                <span style="color: #475569;">Fixed/Essential</span>
                <span style="color: #0284C7; font-weight: 600;">${fixed:,.0f}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #475569;">Discretionary</span>
                <span style="color: #D97706; font-weight: 600;">${discretionary:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_portfolio_section(summary, client_data):
    """Render Portfolio Health section."""
    render_section_header(
        summary['section_title'],
        summary['section_question'],
        summary['overall_score'],
        summary['overall_status']
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Metrics grid
    render_metric_grid(summary['metrics'], columns=3)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="margin-bottom: 0.75rem;">
            <h4 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0;">Current Allocation</h4>
        </div>
        """, unsafe_allow_html=True)
        allocation = {
            'US Stocks': client_data.portfolio_allocation.us_stocks,
            'Int\'l Stocks': client_data.portfolio_allocation.international_stocks,
            'Bonds': client_data.portfolio_allocation.bonds,
            'Real Estate': client_data.portfolio_allocation.real_estate,
            'Commodities': client_data.portfolio_allocation.commodities,
            'Cash': client_data.portfolio_allocation.cash,
            'Alternatives': client_data.portfolio_allocation.alternatives,
            'Crypto': client_data.portfolio_allocation.crypto
        }
        allocation = {k: v for k, v in allocation.items() if v > 0}
        render_allocation_chart(allocation)
    
    with col2:
        st.markdown("""
        <div style="margin-bottom: 0.75rem;">
            <h4 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0;">Portfolio Metrics</h4>
        </div>
        """, unsafe_allow_html=True)
        metrics = client_data.portfolio_metrics
        
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #E2E8F0;">
                <div>
                    <div style="font-size: 0.75rem; color: #64748B;">Expense Ratio</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: {'#059669' if metrics.weighted_expense_ratio < 0.3 else '#D97706'};">
                        {metrics.weighted_expense_ratio:.2f}%
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #64748B;">Annual Turnover</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: {'#059669' if metrics.annual_turnover < 30 else '#D97706'};">
                        {metrics.annual_turnover:.0f}%
                    </div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #E2E8F0;">
                <div>
                    <div style="font-size: 0.75rem; color: #64748B;">Tax Efficiency</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: {'#059669' if metrics.tax_efficiency_score > 70 else '#D97706'};">
                        {metrics.tax_efficiency_score}/100
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #64748B;">Diversification</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: {'#059669' if metrics.concentration_score > 70 else '#D97706'};">
                        {metrics.concentration_score}/100
                    </div>
                </div>
            </div>
            <div>
                <div style="font-size: 0.75rem; color: #64748B;">Trades (12 months)</div>
                <div style="font-size: 1.25rem; font-weight: 600; color: {'#059669' if metrics.trades_last_12_months < 24 else '#D97706'};">
                    {metrics.trades_last_12_months}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Company stock exposure
        if client_data.assets.company_stock_total > 0:
            total_inv = client_data.assets.investment_assets + client_data.assets.company_stock_total
            company_pct = (client_data.assets.company_stock_total / total_inv * 100) if total_inv > 0 else 0
            
            st.markdown(f"""
            <div style="background: {'rgba(220, 38, 38, 0.08)' if company_pct > 20 else 'rgba(217, 119, 6, 0.08)'}; 
                        padding: 1rem; border-radius: 8px; margin-top: 1rem; 
                        border-left: 3px solid {'#DC2626' if company_pct > 20 else '#D97706'};
                        border: 1px solid {'rgba(220, 38, 38, 0.2)' if company_pct > 20 else 'rgba(217, 119, 6, 0.2)'};
                        border-left: 3px solid {'#DC2626' if company_pct > 20 else '#D97706'};">
                <div style="font-size: 0.8rem; font-weight: 600; color: {'#DC2626' if company_pct > 20 else '#D97706'}; text-transform: uppercase; letter-spacing: 0.03em;">Company Stock Exposure</div>
                <div style="font-size: 0.875rem; color: #334155; margin-top: 0.375rem;">
                    ${client_data.assets.company_stock_total:,.0f} ({company_pct:.1f}% of portfolio)
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_planning_section(summary, planning_calc, client_data):
    """Render Future Planning section."""
    render_section_header(
        summary['section_title'],
        summary['section_question'],
        summary['overall_score'],
        summary['overall_status']
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Retirement metrics
    col1, col2 = st.columns(2)
    
    with col1:
        if 'retirement_projection' in summary['metrics']:
            render_metric_card("Retirement Readiness", summary['metrics']['retirement_projection'], show_recommendations=True)
    
    with col2:
        if 'stress_test' in summary['metrics']:
            render_metric_card("Stress Test", summary['metrics']['stress_test'], show_recommendations=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Retirement projection chart
    retirement_assets = (
        client_data.assets.retirement_401k +
        client_data.assets.ira_traditional +
        client_data.assets.ira_roth +
        client_data.assets.brokerage_taxable * 0.8
    )
    
    # Calculate projected savings (simplified)
    years_to_ret = client_data.profile.retirement_age - client_data.profile.age
    annual_savings = client_data.income.total_annual_income * 0.15
    projected = retirement_assets * (1.06 ** years_to_ret) + annual_savings * ((1.06 ** years_to_ret - 1) / 0.06)
    
    target = client_data.expenses.total_monthly_expenses * 12 * 0.75 / 0.04  # 4% rule
    
    render_retirement_projection_chart(
        client_data.profile.age,
        client_data.profile.retirement_age,
        retirement_assets,
        projected,
        target
    )
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Goal progress
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h3 style="font-size: 1.125rem; font-weight: 600; color: #1E293B; margin: 0; letter-spacing: -0.01em;">Financial Goals</h3>
        <p style="font-size: 0.8rem; color: #64748B; margin-top: 0.25rem;">Progress toward your savings targets</p>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(len(client_data.goals)) if len(client_data.goals) <= 3 else st.columns(3)
    
    for i, goal in enumerate(client_data.goals):
        col_idx = i % 3
        with cols[col_idx]:
            goal_key = f'goal_{goal.goal_id}'
            metric = summary['metrics'].get(goal_key)
            if metric:
                render_metric_card(goal.name, metric, show_recommendations=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Scenario analysis
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h3 style="font-size: 1.125rem; font-weight: 600; color: #1E293B; margin: 0; letter-spacing: -0.01em;">What-If Scenarios</h3>
        <p style="font-size: 0.8rem; color: #64748B; margin-top: 0.25rem;">Explore how changes affect your retirement</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Adjust Parameters")
        
        income_change = st.slider(
            "Income Change (%)",
            min_value=-30,
            max_value=50,
            value=0,
            step=5
        )
        
        expense_change = st.slider(
            "Expense Change (%)",
            min_value=-30,
            max_value=30,
            value=0,
            step=5
        )
        
        retirement_age_change = st.slider(
            "Retirement Age Change (years)",
            min_value=-5,
            max_value=10,
            value=0,
            step=1
        )
    
    with col2:
        st.markdown("#### Scenario Result")
        scenario = planning_calc.scenario_analysis(
            income_change_pct=income_change,
            expense_change_pct=expense_change,
            retirement_age_change=retirement_age_change
        )
        
        render_metric_card("Projected Outcome", scenario, show_recommendations=True)
        
        if scenario.trend:
            change_color = '#059669' if scenario.trend > 0 else '#DC2626'
            bg_r = 5 if scenario.trend > 0 else 220
            bg_g = 150 if scenario.trend > 0 else 38
            bg_b = 105 if scenario.trend > 0 else 38
            st.markdown(f"""
            <div style="text-align: center; margin-top: 1rem; padding: 1rem; background: rgba({bg_r}, {bg_g}, {bg_b}, 0.08); 
                        border-radius: 8px; border: 1px solid rgba({bg_r}, {bg_g}, {bg_b}, 0.2);">
                <span style="font-size: 1.5rem; color: {change_color};">
                    {'+' if scenario.trend > 0 else ''}{scenario.trend:.1f}%
                </span>
                <div style="font-size: 0.75rem; color: #475569;">vs Base Case</div>
            </div>
            """, unsafe_allow_html=True)


def render_estate_section(summary, client_data):
    """Render Estate Readiness section."""
    render_section_header(
        summary['section_title'],
        summary['section_question'],
        summary['overall_score'],
        summary['overall_status']
    )
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Metrics grid
    render_metric_grid(summary['metrics'], columns=2)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Estate planning checklist
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="margin-bottom: 0.75rem;">
            <h4 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0;">Document Checklist</h4>
            <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.125rem;">Essential estate documents</p>
        </div>
        """, unsafe_allow_html=True)
        
        estate = client_data.estate
        documents = [
            ("Will", estate.has_will, "Essential for asset distribution"),
            ("Trust", estate.has_trust, "Recommended for estates > $1M"),
            ("Financial POA", estate.has_poa_financial, "Manages finances if incapacitated"),
            ("Healthcare POA", estate.has_poa_healthcare, "Makes medical decisions if unable"),
            ("Healthcare Directive", estate.has_healthcare_directive, "Specifies end-of-life wishes"),
            ("Digital Estate Plan", estate.digital_estate_documented, "Passwords, crypto, digital assets")
        ]
        
        for doc_name, has_doc, description in documents:
            color = "#059669" if has_doc else "#DC2626"
            bg_color = "rgba(5, 150, 105, 0.06)" if has_doc else "rgba(220, 38, 38, 0.06)"
            border_color = "#059669" if has_doc else "#DC2626"
            
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; 
                        background: {bg_color}; border-radius: 8px; margin-bottom: 0.5rem;
                        border-left: 3px solid {border_color};">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: {color}; flex-shrink: 0;"></div>
                <div>
                    <div style="font-size: 0.8rem; color: #1E293B; font-weight: 600;">{doc_name}</div>
                    <div style="font-size: 0.7rem; color: #64748B;">{description}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="margin-bottom: 0.75rem;">
            <h4 style="font-size: 1rem; font-weight: 600; color: #1E293B; margin: 0;">Beneficiary Status</h4>
            <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.125rem;">Account designations</p>
        </div>
        """, unsafe_allow_html=True)
        
        if estate.beneficiaries_updated:
            status_text = "Up to date"
            status_color = "#059669"
            indicator_bg = "rgba(5, 150, 105, 0.1)"
        else:
            status_text = "Review needed"
            status_color = "#D97706"
            indicator_bg = "rgba(217, 119, 6, 0.1)"
        
        last_review = estate.beneficiaries_last_reviewed
        review_text = last_review.strftime("%B %d, %Y") if last_review else "Never"
        
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                <div style="width: 10px; height: 10px; border-radius: 50%; background: {status_color};"></div>
                <div>
                    <div style="font-size: 0.9rem; color: {status_color}; font-weight: 600;">{status_text}</div>
                    <div style="font-size: 0.75rem; color: #64748B;">Last reviewed: {review_text}</div>
                </div>
            </div>
            <div style="padding-top: 1rem; border-top: 1px solid #E2E8F0;">
                <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 0.5rem;">Accounts to Review:</div>
                <div style="font-size: 0.8rem; color: #1E293B;">
        """, unsafe_allow_html=True)
        
        accounts = []
        if client_data.assets.retirement_401k > 0:
            accounts.append(f"• 401(k): ${client_data.assets.retirement_401k:,.0f}")
        if client_data.assets.ira_traditional > 0:
            accounts.append(f"• Traditional IRA: ${client_data.assets.ira_traditional:,.0f}")
        if client_data.assets.ira_roth > 0:
            accounts.append(f"• Roth IRA: ${client_data.assets.ira_roth:,.0f}")
        if client_data.insurance.life_insurance_coverage > 0:
            accounts.append(f"• Life Insurance: ${client_data.insurance.life_insurance_coverage:,.0f}")
        
        for acc in accounts:
            st.markdown(f"<div>{acc}</div>", unsafe_allow_html=True)
        
        st.markdown("</div></div></div>", unsafe_allow_html=True)
        
        # Will status
        if estate.has_will and estate.will_last_updated:
            years_old = (client_data.estate.will_last_updated.today() - estate.will_last_updated).days / 365
            
            if years_old > 5:
                will_status = "Will may need review"
                will_color = "#D97706"
                border_color = "#D97706"
            elif years_old > 3:
                will_status = "Consider reviewing will"
                will_color = "#0284C7"
                border_color = "#0284C7"
            else:
                will_status = "Will recently updated"
                will_color = "#059669"
                border_color = "#059669"
            
            bg_r = 217 if years_old > 3 else 5
            bg_g = 119 if years_old > 3 else 150
            bg_b = 6 if years_old > 3 else 105
            st.markdown(f"""
            <div style="background: rgba({bg_r}, {bg_g}, {bg_b}, 0.08); 
                        padding: 1rem; border-radius: 8px; margin-top: 1rem; 
                        border: 1px solid rgba({bg_r}, {bg_g}, {bg_b}, 0.2);
                        border-left: 3px solid {border_color};">
                <div style="font-size: 0.8rem; font-weight: 600; color: {will_color};">{will_status}</div>
                <div style="font-size: 0.75rem; color: #475569; margin-top: 0.25rem;">
                    Last updated: {estate.will_last_updated.strftime("%B %Y")} ({years_old:.1f} years ago)
                </div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
