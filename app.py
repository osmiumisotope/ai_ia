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
    get_client_by_id
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
    
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Personal Info", "👨‍👩‍👧 Dependents", "📄 Documents", "🏥 Disability Analysis"])
    
    with tab1:
        render_personal_info_tab(client_id, client_data)
    
    with tab2:
        render_dependents_tab(client_id)
    
    with tab3:
        render_documents_tab(client_id)
        
    with tab4:
        render_disability_analysis_tab(client_id, client_data)


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
            
            # Check if document already exists
            existing_doc = get_document_by_hash(file_hash, client_id)
            
            if existing_doc:
                st.warning(f"⚠️ This file has already been uploaded on {existing_doc.get('upload_time', 'unknown date')}")
            else:
                if st.button("📤 Upload Document", use_container_width=True):
                    try:
                        # Create client-specific directory
                        client_dir = UPLOADS_DIR / client_id
                        client_dir.mkdir(exist_ok=True)
                        
                        # Generate unique filename
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        safe_filename = f"{timestamp}_{uploaded_file.name}"
                        file_path = client_dir / safe_filename
                        
                        # Save file
                        with open(file_path, 'wb') as f:
                            f.write(file_content)
                        
                        # Add document record to database
                        doc_data = {
                            'document_type': doc_type,
                            'file_name': uploaded_file.name,
                            'file_hash': file_hash,
                            'storage_path': str(file_path),
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
                    
                    # Download button
                    storage_path = doc.get('storage_path')
                    if storage_path and Path(storage_path).exists():
                        with open(storage_path, 'rb') as f:
                            file_data = f.read()
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
        storage_path = selected_doc.get('storage_path')
        if not storage_path or not Path(storage_path).exists():
            st.error("Document file not found on disk.")
            return
            
        if st.button("Analyze Document", type="primary"):
            with st.spinner("Extracting policy details using Gemini..."):
                try:
                    from logic.llm_extractor import extract_disability_policy
                    policy = extract_disability_policy(storage_path)
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
