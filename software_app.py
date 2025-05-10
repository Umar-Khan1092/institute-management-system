import os
import streamlit as st
from datetime import date
from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, Float,
    create_engine, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import pandas as pd

# --- Database setup ---
DB_URL = "sqlite:///institutes.db"
engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# --- Model definitions ---
class Institute(Base):
    __tablename__ = 'institutes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String)
    focal_person = Column(String)
    contact = Column(String)
    agreement_date = Column(Date)
    rate_per_student = Column(Integer)
    agreement_path = Column(String)
    assignments = relationship('Assignment', back_populates='institute')

class ClassModel(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    agency = Column(String)
    sections = relationship('Section', back_populates='class_model')
    assignments = relationship('Assignment', back_populates='class_model')

class Section(Base):
    __tablename__ = 'sections'
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    name = Column(String, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    duration_months = Column(Integer)
    class_model = relationship('ClassModel', back_populates='sections')
    assignments = relationship('Assignment', back_populates='section')

class Assignment(Base):
    __tablename__ = 'assignments'
    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'), nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    section_id = Column(Integer, ForeignKey('sections.id'), nullable=False)
    total_students = Column(Integer)
    institute = relationship('Institute', back_populates='assignments')
    class_model = relationship('ClassModel', back_populates='assignments')
    section = relationship('Section', back_populates='assignments')

class LetterDispatch(Base):
    __tablename__ = 'letters_dispatch'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    reference = Column(String)
    recipient = Column(String)

class LetterReceive(Base):
    __tablename__ = 'letters_receive'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    reference = Column(String)
    sender = Column(String)

class IncomeRegister(Base):
    __tablename__ = 'income_register'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    amount = Column(Float)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    class_id = Column(Integer, ForeignKey('classes.id'))
    section_id = Column(Integer, ForeignKey('sections.id'))
    institute = relationship('Institute')
    class_model = relationship('ClassModel')
    section = relationship('Section')

class ExpenseRegister(Base):
    __tablename__ = 'expense_register'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    amount = Column(Float)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    class_id = Column(Integer, ForeignKey('classes.id'))
    section_id = Column(Integer, ForeignKey('sections.id'))
    institute = relationship('Institute')
    class_model = relationship('ClassModel')
    section = relationship('Section')

class InstituteShare(Base):
    __tablename__ = 'institute_share'
    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey('institutes.id'))
    class_id = Column(Integer, ForeignKey('classes.id'))
    section_id = Column(Integer, ForeignKey('sections.id'))
    total_students = Column(Integer)
    rate_per_student = Column(Integer)
    duration_months = Column(Integer)
    total_amount = Column(Float)
    paid_date = Column(Date)
    institute = relationship('Institute')
    class_model = relationship('ClassModel')
    section = relationship('Section')

class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    designation = Column(String)
    user_id = Column(String, unique=True)
    password = Column(String)
    institute_permission = Column(String)

Base.metadata.create_all(engine)

# --- Style function for dataframes ---
def style_dataframe(df):
    return df.style.set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#5c2f0d'), ('color', '#ffffff'), ('font-weight', 'bold'), ('padding', '10px'), ('font-family', 'Roboto, sans-serif')]},
        {'selector': 'td', 'props': [('border', '1px solid #e5e7eb'), ('padding', '10px'), ('background-color', '#f8fafc'), ('color', '#1f2937'), ('font-family', 'Roboto, sans-serif')]}
    ])

# --- App UI ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        body {
            background: linear-gradient(135deg, #f8fafc, #e5e7eb);
            font-family: 'Roboto', sans-serif;
        }
        .stApp {
            background: linear-gradient(120deg, #ffffff, #f8fafc);
            color: #1f2937;
            max-width: 100%;
            margin: 0 auto;
            padding: 0;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        .app-header {
            width: 100%;
            text-align: left;
            margin: 0;
            padding: 0;
        }
        h1, h2, h3 {
            color: #5c2f0d;
            background: #bfa3f3;
            padding: 10px 15px;
            border-radius: 10px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
            font-family: 'Roboto', sans-serif;
            font-weight: 500;
        }
        h1 {
            text-align: left !important;
            margin-left: 0;
            padding-left: 15px;
            font-size: 2rem;
            font-weight: 700;
        }
        .css-18e3th9 {
            padding: 2rem;
        }
        .stButton > button {
            background: #b91c1c;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            font-family: 'Roboto', sans-serif;
            transition: all 0.2s ease;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
        }
        .stButton > button:hover {
            background: #5c2f0d;
            transform: translateY(-1px);
            # box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        }
        .stButton > button:disabled {
            background: #d1d5db;
            color: #9ca3af;
            cursor: not-allowed;
            box-shadow: none;
        }
        .stTextInput > div > input, .stTextArea > div > textarea, .stSelectbox > div > select {
            background-color: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            padding: 8px;
            color: #1f2937;
            font-family: 'Roboto', sans-serif;
            transition: border-color 0.2s ease;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }
        .stTextInput > div > input:focus, .stTextArea > div > textarea:focus, .stSelectbox > div > select:focus {
            border-color: #b91c1c;
            box-shadow: 0 0 6px rgba(185, 28, 28, 0.3);
        }
        .stDateInput > div > input {
            background-color: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            padding: 8px;
            font-family: 'Roboto', sans-serif;
        }
        .stFileUploader > div {
            background-color: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            padding: 8px;
        }
        .stTabs > div > button {
            background-color: #bfa3f3;
            color: #ffffff;
            border-radius: 6px 6px 0 0;
            margin-right: 4px;
            padding: 8px 16px;
            font-weight: 500;
            font-family: 'Roboto', sans-serif;
            transition: background-color 0.2s ease;
        }
        .stTabs > div > button:hover {
            background-color: #8b4513;
        }
        .stTabs > div > button[aria-selected="true"] {
            background-color: #b91c1c;
            color: #ffffff;
        }
        .stExpander {
            background-color: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }
        .stMarkdown, .stText {
            color: #1f2937;
            font-family: 'Roboto', sans-serif;
        }
        .stAlert > div {
            border-radius: 6px;
            font-family: 'Roboto', sans-serif;
        }
            
        .st-emotion-cache-16tyu1 h2{
            padding: 1rem 12px;
            }
        .st-emotion-cache-16tyu1 h3{
            padding: 0.75rem 12px 1rem;
            margin-top: 10px
            }
        .st-emotion-cache-13lcgu3:hover{
             border-color: #513683;
            }
        .st-emotion-cache-10c9vv9 p:hover{
            color: #513683;
            }
        .st-emotion-cache-4uzi61{
            margin-top: 20px;
            }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
    <style>
        .sidebar-info {
            background: #ffffff;
            padding: 20px;
            border-radius: 6px;
            border-left: 6px solid #b91c1c;
            font-family: 'Roboto', sans-serif;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
            margin: 8px;
        }
        .sidebar-info h3 {
            color: #1f2937;
            font-size: 1.25rem;
            margin-bottom: 10px;
            font-weight: 500;
            padding-left: 20%;
        }
        .sidebar-info p {
            color: #1f2937;
            font-size: 0.875rem;
            line-height: 1.4;
        }
        .sidebar-info ul {
            padding-left: 20px;
            font-size: 0.875rem;
            color: #1f2937;
        }
        .sidebar-info ul li {
            margin-bottom: 6px;
        }
        .sidebar-info p em {
            color: #b91c1c;
            font-weight: 500;
        }
        # .st-emotion-cache-br351g.active{
        #             color: #513683;
        #             }
                    
        .st-bd{
                color: #513683;
                }
        .st-bn:hover{
                    color: #513683; 
                    }
    </style>

    <div class="sidebar-info">
        <h3>About This App</h3>
        <p>This is an <strong>Institute Management System</strong> where you can:</p>
        <ul>
            <li>Add, update, or delete institutes</li>
            <li>Manage class sections</li>
            <li>Update intitute records</li>
            <li>Mangement of accounts</li>
            <li>Visualize the updated reports</li>
            <li>Store and retrieve data securely</li>
        </ul>
        <p style="margin-top:8px;"><em>Tip:</em> Register all institutes first before assigning sections.</p>
    </div>
""", unsafe_allow_html=True)

# Updated title section with stronger left-alignment enforcement
st.markdown("""
    <style>
        .title-wrapper {
            display: block;
            width: 100%;
            text-align: left !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .title-wrapper h1 {
            display: inline-block;
            text-align: left !important;
            margin-left: 0 !important;
            padding-left: 15px !important;
            width: auto;
            text-shadow: none;
        }
        /* Override Streamlit's default container centering */
        div[data-testid="stAppViewContainer"] > div {
            text-align: left !important;
        }
    </style>
""", unsafe_allow_html=True)

# Use a container and wrap the title
with st.container():
    st.markdown('<div class="title-wrapper"><h1>Institute Management System</h1></div>', unsafe_allow_html=True)

tabs = st.tabs([
    "Registration", "Institute List", "Classes",
    "Registers", "Accounts", "Reports", "Admin Panel"
])

# --- Tab 1: Registration ---
with tabs[0]:
    st.header("Institute Registration")
    with st.form("reg_form"):
        name = st.text_input("Institute Name")
        address = st.text_area("Institute Address")
        focal = st.text_input("Focal Person Name")
        contact = st.text_input("Contact #")
        agree_date = st.date_input(
            "Agreement Signing Date",
            min_value=date(2000,1,1),
            max_value=date.today()
        )
        rate = st.number_input("Rate Per Student", min_value=0, step=1)
        pdf_file = st.file_uploader("Upload the Agreement (PDF)", type=["pdf"])
        if st.form_submit_button("Register Institute"):
            path = None
            if pdf_file:
                os.makedirs("agreements", exist_ok=True)
                path = os.path.join(
                    "agreements",
                    f"{name.replace(' ','_')}_{pdf_file.name}"
                )
                open(path, "wb").write(pdf_file.getbuffer())
            inst = Institute(
                name=name, address=address, focal_person=focal,
                contact=contact, agreement_date=agree_date,
                rate_per_student=rate, agreement_path=path
            )
            session.add(inst)
            session.commit()
            st.success(f"Registered '{name}' successfully!")

# --- Tab 2: Institute List ---
with tabs[1]:
    st.header("Registered Institutes")
    for inst in session.query(Institute).all():
        with st.expander(f"{inst.name} (ID: {inst.id})"):
            with st.form(f"upd_inst_{inst.id}"):
                nn = st.text_input("Institute Name", inst.name)
                aa = st.text_area("Institute Address", inst.address)
                fp = st.text_input("Focal Person Name", inst.focal_person)
                cc = st.text_input("Contact #", inst.contact)
                dd = st.date_input(
                    "Agreement Signing Date",
                    inst.agreement_date or date.today()
                )
                rr = st.number_input("Rate Per Student", inst.rate_per_student or 0)
                npdf = st.file_uploader("Replace Agreement PDF?", type=["pdf"])
                if st.form_submit_button("Update"):
                    if npdf:
                        os.makedirs("agreements", exist_ok=True)
                        p = os.path.join(
                            "agreements",
                            f"{nn.replace(' ','_')}_{npdf.name}"
                        )
                        open(p, "wb").write(npdf.getbuffer())
                        inst.agreement_path = p
                    inst.name, inst.address = nn, aa
                    inst.focal_person, inst.contact = fp, cc
                    inst.agreement_date, inst.rate_per_student = dd, rr
                    session.commit()
                    st.success("Updated!")

# --- Tab 3: Classes & Sections ---
with tabs[2]:
    st.header("Class & Section Management")
    st.subheader("1. Create Class")
    with st.form("class_form"):
        cname = st.text_input("Class Name")
        agency = st.text_input("Agency")
        if st.form_submit_button("Create Class"):
            session.add(ClassModel(name=cname, agency=agency))
            session.commit()
            st.success("Class created!")

    st.subheader("2. Create Section")
    classes = session.query(ClassModel).all()
    if classes:
        with st.form("sec_form"):
            sel = st.selectbox("Class", {c.id: f"{c.id}: {c.name}" for c in classes})
            sname = st.text_input("Section Name")
            sd = st.date_input("Start Date")
            ed = st.date_input("End Date", min_value=sd)
            dur = (ed.year - sd.year)*12 + (ed.month - sd.month)
            st.write(f"Duration: {dur} month(s)")
            if st.form_submit_button("Create Section"):
                session.add(Section(
                    class_id=sel, name=sname,
                    start_date=sd, end_date=ed,
                    duration_months=dur
                ))
                session.commit()
                st.success("Section created!")
    else:
        st.info("Create a class first to add sections.")

    st.subheader("3. Assign to Institute")
    insts = session.query(Institute).all()
    clss = session.query(ClassModel).all()
    if insts and clss:
        with st.form("assign_form"):
            iid = st.selectbox("Institute", {i.id: f"{i.id}: {i.name}" for i in insts})
            cid = st.selectbox("Class", {c.id: f"{c.id}: {c.name}" for c in clss})
            # Only show sections for the selected class
            secs = session.query(Section).filter(Section.class_id == cid).all()
            sid = st.selectbox(
                "Section",
                {s.id: f"{s.id}: {s.name}" for s in secs} if secs else {0: "No sections available"},
                disabled=not secs
            )
            ts = st.number_input("Total Students", min_value=0)
            if st.form_submit_button("Assign", disabled=not secs or sid == 0):
                session.add(Assignment(
                    institute_id=iid, class_id=cid,
                    section_id=sid, total_students=ts
                ))
                session.commit()
                st.success("Assigned!")
            elif not secs:
                st.warning("No sections available for the selected class. Create a section first.")
    else:
        st.info("Ensure at least one institute and class exist.")

# --- Tab 4: Registers ---
with tabs[3]:
    st.header("Letters Dispatch & Receive Registers")

    st.subheader("Dispatch Register")
    with st.form("disp_form"):
        dd = st.date_input("Date", key="disp_date")
        ref = st.text_input("Reference No.", key="disp_ref")
        rec = st.text_input("Recipient", key="disp_rec")
        if st.form_submit_button("Log Dispatch"):
            session.add(LetterDispatch(date=dd, reference=ref, recipient=rec))
            session.commit()
            st.success("Dispatch logged!")

    st.subheader("Receive Register")
    with st.form("recv_form"):
        rd = st.date_input("Date", key="recv_date")
        rref = st.text_input("Reference No.", key="recv_ref")
        snd = st.text_input("Sender", key="recv_snd")
        if st.form_submit_button("Log Receive"):
            session.add(LetterReceive(date=rd, reference=rref, sender=snd))
            session.commit()
            st.success("Receive logged!")

# --- Tab 5: Accounts ---
with tabs[4]:
    st.header("Accounts: Income & Expense & Institute Share")

    # Debugging: Display current database state with names
    with st.expander("Debug: Database State"):
        st.subheader("Institutes")
        institutes = session.query(Institute).all()
        st.write([(i.id, i.name) for i in institutes])
        
        st.subheader("Classes")
        classes = session.query(ClassModel).all()
        st.write([(c.id, c.name) for c in classes])
        
        st.subheader("Sections")
        sections = session.query(Section).all()
        section_data = []
        for s in sections:
            class_obj = session.query(ClassModel).filter_by(id=s.class_id).first()
            class_name = class_obj.name if class_obj else "Unknown"
            section_data.append((s.id, s.name, class_name))
        st.write(section_data)
        
        st.subheader("Assignments")
        assignments = session.query(Assignment).all()
        assignment_data = []
        for a in assignments:
            inst_obj = session.query(Institute).filter_by(id=a.institute_id).first()
            class_obj = session.query(ClassModel).filter_by(id=a.class_id).first()
            section_obj = session.query(Section).filter_by(id=a.section_id).first()
            inst_name = inst_obj.name if inst_obj else "Unknown"
            class_name = class_obj.name if class_obj else "Unknown"
            section_name = section_obj.name if section_obj else "Unknown"
            assignment_data.append((a.id, inst_name, class_name, section_name, a.total_students))
        st.write(assignment_data)

    # Get classes with at least one section
    valid_class_ids = [s.class_id for s in session.query(Section).distinct(Section.class_id).all()]
    valid_classes = session.query(ClassModel).filter(ClassModel.id.in_(valid_class_ids)).all()
    class_options = {c.id: f"{c.id}: {c.name}" for c in valid_classes} if valid_classes else {0: "No classes with sections"}

    st.subheader("Income Register")
    with st.form("inc_form"):
        idate = st.date_input("Date", key="inc_date")
        amt = st.number_input("Amount Received", min_value=0.0, step=0.01)
        iid = st.selectbox(
            "Institute", {i.id: f"{i.id}: {i.name}" for i in session.query(Institute)},
            key="inc_inst"
        )
        cid = st.selectbox(
            "Class", class_options,
            key="inc_cls"
        )
        # Refresh session to ensure latest data
        session.expire_all()
        sec_list = session.query(Section).filter(Section.class_id == cid).all() if cid != 0 else []
        sec_options = {s.id: f"{s.id}: {s.name}" for s in sec_list} if sec_list else {0: "No sections available"}
        sid = st.selectbox(
            "Section", sec_options,
            key="inc_sec"
        )
        submit_button = st.form_submit_button("Log Income", disabled=(not sec_list or sid == 0))
        if not valid_classes:
            st.warning("No classes have sections. Please create a section in the 'Classes' tab under 'Create Section'.")
        elif not sec_list:
            st.warning("No sections available for the selected class. Please create a section in the 'Classes' tab under 'Create Section'.")
        if submit_button and sec_list and sid != 0:
            session.add(IncomeRegister(
                date=idate, amount=amt,
                institute_id=iid, class_id=cid, section_id=sid
            ))
            session.commit()
            st.success("Income logged!")
        elif submit_button and (not sec_list or sid == 0):
            st.error("Please select a valid section to log income.")

    st.subheader("Expense Register")
    with st.form("exp_form"):
        edate = st.date_input("Date", key="exp_date")
        eamt = st.number_input("Amount Spent", min_value=0.0, step=0.01)
        eiid = st.selectbox(
            "Institute", {i.id: f"{i.id}: {i.name}" for i in session.query(Institute)},
            key="exp_inst"
        )
        ecid = st.selectbox(
            "Class", class_options,
            key="exp_cls"
        )
        # Refresh session to ensure latest data
        session.expire_all()
        sec_list = session.query(Section).filter(Section.class_id == ecid).all() if ecid != 0 else []
        sec_options = {s.id: f"{s.id}: {s.name}" for s in sec_list} if sec_list else {0: "No sections available"}
        esid = st.selectbox(
            "Section", sec_options,
            key="exp_sec"
        )
        submit_button = st.form_submit_button("Log Expense", disabled=(not sec_list or esid == 0))
        if not valid_classes:
            st.warning("No classes have sections. Please create a section in the 'Classes' tab under 'Create Section'.")
        elif not sec_list:
            st.warning("No sections available for the selected class. Please create a section in the 'Classes' tab under 'Create Section'.")
        if submit_button and sec_list and esid != 0:
            session.add(ExpenseRegister(
                date=edate, amount=eamt,
                institute_id=eiid, class_id=ecid, section_id=esid
            ))
            session.commit()
            st.success("Expense logged!")
        elif submit_button and (not sec_list or esid == 0):
            st.error("Please select a valid section to log expense.")

    st.subheader("Institute Share Calculation")
    with st.form("share_form"):
        st.info("Ensure the selected Institute, Class, and Section have a valid assignment created in the 'Classes' tab.")
        sid2 = st.selectbox(
            "Institute", {i.id: f"{i.id}: {i.name}" for i in session.query(Institute)},
            key="share_inst"
        )
        cid2 = st.selectbox(
            "Class", class_options,
            key="share_cls"
        )
        # Refresh session to ensure latest data
        session.expire_all()
        sec_list = session.query(Section).filter(Section.class_id == cid2).all() if cid2 != 0 else []
        sec_options = {s.id: f"{s.id}: {s.name}" for s in sec_list} if sec_list else {0: "No sections available"}
        sid3 = st.selectbox(
            "Section", sec_options,
            key="share_sec"
        )
        submit_button = st.form_submit_button("Save Share", disabled=(not sec_list or sid3 == 0))
        if not valid_classes:
            st.warning("No classes have sections. Please create a section in the 'Classes' tab under 'Create Section'.")
        elif not sec_list:
            st.warning("No sections available for the selected class. Please create a section in the 'Classes' tab under 'Create Section'.")
        elif sid3 == 0:
            st.error("Please select a valid section to calculate the institute share.")
        else:
            # Validate assignment
            assign = session.query(Assignment).filter_by(
                institute_id=sid2, class_id=cid2, section_id=sid3
            ).first()
            if not assign:
                st.warning("No valid assignment found for this Institute-Class-Section combination. Please create a correct assignment in the 'Classes' tab under 'Assign to Institute'.")
            else:
                # Verify section belongs to the class
                section = session.query(Section).filter_by(id=sid3, class_id=cid2).first()
                if not section:
                    st.error("Selected section does not belong to the chosen class. Please fix the assignment or create a new one.")
                else:
                    rate = session.query(Institute).get(sid2).rate_per_student
                    duration = section.duration_months
                    total = assign.total_students * rate * duration
                    st.write(f"Total Students: {assign.total_students}")
                    st.write(f"Rate per Student: {rate}")
                    st.write(f"Duration (months): {duration}")
                    st.write(f"Total Amount: {total}")
                    pdate = st.date_input("Paid Date", key="share_date")
                    if submit_button:
                        session.add(InstituteShare(
                            institute_id=sid2, class_id=cid2, section_id=sid3,
                            total_students=assign.total_students,
                            rate_per_student=rate, duration_months=duration,
                            total_amount=total, paid_date=pdate
                        ))
                        session.commit()
                        st.success("Institute share saved!")

# --- Tab 6: Reports ---
with tabs[5]:
    st.header("Report Section")

    st.subheader("1. Income Statement (Class Wise)")
    df_income = pd.read_sql(
        session.query(
            ClassModel.name.label('Class'),
            func.sum(IncomeRegister.amount).label('Total Income')
        )
        .join(IncomeRegister, IncomeRegister.class_id == ClassModel.id)
        .group_by(ClassModel.name)
        .statement,
        engine
    )
    st.dataframe(style_dataframe(df_income))

    st.subheader("2. Expense Statement (Class Wise)")
    df_expense = pd.read_sql(
        session.query(
            ClassModel.name.label('Class'),
            func.sum(ExpenseRegister.amount).label('Total Expense')
        )
        .join(ExpenseRegister, ExpenseRegister.class_id == ClassModel.id)
        .group_by(ClassModel.name)
        .statement,
        engine
    )
    st.dataframe(style_dataframe(df_expense))

    st.subheader("3. Dispatch Register")
    df_disp = pd.read_sql(session.query(LetterDispatch).statement, engine)
    st.dataframe(style_dataframe(df_disp))

    st.subheader("4. Receiving Register")
    df_recv = pd.read_sql(session.query(LetterReceive).statement, engine)
    st.dataframe(style_dataframe(df_recv))

    st.subheader("5. Profit/Loss Statement (Institute Wise)")
    df_inc_inst = pd.read_sql(
        session.query(
            Institute.name.label('Institute'),
            func.coalesce(func.sum(IncomeRegister.amount), 0).label('Income')
        )
        .outerjoin(IncomeRegister, IncomeRegister.institute_id == Institute.id)
        .group_by(Institute.name)
        .statement,
        engine
    )
    df_exp_inst = pd.read_sql(
        session.query(
            Institute.name.label('Institute'),
            func.coalesce(func.sum(ExpenseRegister.amount), 0).label('Expense')
        )
        .outerjoin(ExpenseRegister, ExpenseRegister.institute_id == Institute.id)
        .group_by(Institute.name)
        .statement,
        engine
    )
    df_pl = df_inc_inst.merge(df_exp_inst, on='Institute', how='outer').fillna(0)
    df_pl['Profit/Loss'] = df_pl['Income'] - df_pl['Expense']
    st.dataframe(style_dataframe(df_pl))

# --- Tab 7: Admin Panel ---
with tabs[6]:
    st.header("Admin Panel")
    st.subheader("Create New Admin")
    with st.form("admin_form"):
        aname = st.text_input("Admin Name")
        desig = st.text_input("Designation")
        uid = st.text_input("User ID")
        pwd = st.text_input("Password", type="password")
        perm = st.text_input("Permission (Institute IDs comma-separated)")
        if st.form_submit_button("Create Admin"):
            session.add(Admin(
                name=aname, designation=desig,
                user_id=uid, password=pwd,
                institute_permission=perm
            ))
            session.commit()
            st.success(f"Admin '{aname}' created!")

    st.subheader("Existing Admins")
    df_admins = pd.read_sql(
        session.query(Admin.id, Admin.name, Admin.designation, Admin.user_id).statement,
        engine
    )
    st.dataframe(style_dataframe(df_admins))
