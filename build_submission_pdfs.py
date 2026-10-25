from datetime import date
from pathlib import Path
import json
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
                                PageBreak, Table, TableStyle, KeepTogether)
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)
NAVY = colors.HexColor("#132438")
INK = colors.HexColor("#203047")
MUTED = colors.HexColor("#768596")
BLUE = colors.HexColor("#3B6DB6")
LINE = colors.HexColor("#E7EDF3")
PALE = colors.HexColor("#F5F8FB")
MINT = colors.HexColor("#4AA47D")
AMBER = colors.HexColor("#B88B43")
PURPLE = colors.HexColor("#8B75C4")
TODAY = "26 October 2026"
DETAILS_PATH = ROOT / ".submission-details.json"
details = json.loads(DETAILS_PATH.read_text(encoding="utf-8")) if DETAILS_PATH.exists() else {}
STUDENT = details.get("student", "[Student name]")
IDENTIFIERS = details.get("identifiers", "[Student identifiers]")
INSTITUTION = details.get("institution", "[Institution]")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="DocTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=30, textColor=INK, alignment=TA_LEFT, spaceAfter=9))
styles.add(ParagraphStyle(name="Subtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=16, textColor=MUTED, spaceAfter=14))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=INK, spaceBefore=12, spaceAfter=7, keepWithNext=True))
styles.add(ParagraphStyle(name="Subsection", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=BLUE, spaceBefore=7, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle(name="BodyTextCustom", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=14, textColor=colors.HexColor("#405164"), spaceAfter=6))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyTextCustom"], fontSize=8, leading=11, textColor=MUTED, spaceAfter=4))
styles.add(ParagraphStyle(name="BulletCustom", parent=styles["BodyTextCustom"], leftIndent=12, firstLineIndent=-8, bulletIndent=0, bulletFontName="Helvetica", spaceAfter=3))

def para(text, style="BodyTextCustom"):
    return Paragraph(text, styles[style])

def footer(canvas_obj, doc):
    canvas_obj.saveState()
    w, _ = A4
    canvas_obj.setStrokeColor(LINE)
    canvas_obj.setLineWidth(.6)
    canvas_obj.line(19*mm, 16*mm, w-19*mm, 16*mm)
    canvas_obj.setFillColor(MUTED)
    canvas_obj.setFont("Helvetica", 7.5)
    canvas_obj.drawString(19*mm, 10.5*mm, "LABDESK  |  STUDENT PROJECT DOCUMENTATION")
    canvas_obj.drawRightString(w-19*mm, 10.5*mm, f"{doc.page}")
    canvas_obj.restoreState()

def cover_block(title, subtitle, label):
    return [Spacer(1, 26*mm), para(label.upper(), "Small"), Spacer(1, 7*mm), para(title, "DocTitle"), para(subtitle, "Subtitle"), Spacer(1, 7*mm),
            Table([[para(f"<b>Student</b><br/>{STUDENT}", "BodyTextCustom"), para(f"<b>Institution</b><br/>{INSTITUTION}", "BodyTextCustom")],
                   [para(f"<b>Student identifiers</b><br/>{IDENTIFIERS}", "BodyTextCustom"), para(f"<b>Prepared</b><br/>{TODAY}", "BodyTextCustom")]],
                  colWidths=[82*mm, 82*mm], rowHeights=[23*mm, 23*mm], style=TableStyle([
                      ("BACKGROUND", (0,0), (-1,-1), PALE), ("BOX", (0,0), (-1,-1), .7, LINE), ("INNERGRID", (0,0), (-1,-1), .5, LINE),
                      ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 11), ("RIGHTPADDING", (0,0), (-1,-1), 11)
                  ])), Spacer(1, 15*mm), para("Project note", "Subsection"),
            para("LabDesk is a learning prototype prepared with AI coding assistance. The student should review and understand the implementation, confirm all details, and disclose assistance as required by course policy. Its features and results are described as implemented in the delivered prototype; no internship placement or external testing is claimed.", "BodyTextCustom"), PageBreak()]

def make_doc(path, story, title):
    doc = BaseDocTemplate(str(path), pagesize=A4, rightMargin=19*mm, leftMargin=19*mm, topMargin=18*mm, bottomMargin=22*mm, title=title, author=STUDENT)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=footer))
    doc.build(story)

def make_report():
    story = cover_block("LabDesk Project Report", "Laboratory equipment checkout and return prototype", "Summer internship report | Full Stack Application Development with ReactJS")
    story += [para("Executive Summary", "Section"),
        para("LabDesk is a browser-based laboratory equipment checkout prototype. It gives students a searchable view of equipment and a short loan request form, while a coordinator can review requests and record returns. The delivered build uses React and Vite for the client, Express and Node.js for the API, and Mongoose models for optional MongoDB persistence. Without a MongoDB connection string, the API runs in demonstration mode with in-memory sample records.", "BodyTextCustom"),
        para("Introduction", "Section"),
        para("Laboratories share instruments across classes, practical sessions, and student projects. Paper registers and informal messages can make availability and due dates difficult to track. LabDesk explores a simple digital workflow for one teaching laboratory: show an equipment register, record a loan request, review its status, and check an item back in.", "BodyTextCustom"),
        para("The application theme and broad checkout workflow were informed by LabFlow, an MIT-licensed project by Milan K B. LabDesk is a separate implementation with its own name, interface, and code. The upstream reference is listed in the README.", "BodyTextCustom"),
        para("Objectives", "Section"),
        para("The prototype aims to make equipment availability visible, collect the purpose and return date for a loan request, and give staff a compact queue for approvals and check-ins. It also serves as a practical example of a React client communicating with a Node and Express API, with Mongoose schemas prepared for MongoDB-backed storage.", "BodyTextCustom"),
        para("Scope and Deliverables", "Section"),
        para("The submitted application includes a dashboard, equipment catalogue, request queue, expected returns view, equipment request form, and Express API endpoints for health, equipment, request creation, and request status updates. The project includes a README, environment variable example, and this report, requirements specification, and interface preview PDF.", "BodyTextCustom"),
        para("Authentication, server-enforced roles, audit history, and production database provisioning are outside the current prototype scope. Demonstration records are illustrative and should not be replaced with real student information.", "BodyTextCustom"),
        para("Methodology", "Section"),
        para("The work follows a small iterative build: define the laboratory checkout workflow, model equipment and loan request fields, create the React views, add API routes and validation, and verify the client against the local API. The interface uses sample records so its principal states can be reviewed without a configured database. MongoDB persistence activates when MONGODB_URI is set in the server environment.", "BodyTextCustom"),
        para("Technology stack", "Subsection"),
        *bullet_list(["React 19 and Vite for the single-page client.", "Node.js and Express for the JSON API.", "MongoDB and Mongoose schemas for optional persistent storage.", "Lucide icons and responsive CSS for interface components." ]),
        para("Project Activities", "Section"),
        *bullet_list(["Defined the equipment fields: name, category, asset tag, status, and location.", "Created the overview dashboard with inventory counts, recent requests, and activity summary.", "Added equipment filters and search, a request form, and request status actions.", "Implemented API input checks for equipment and loan requests, status allow-list validation, health reporting, and safe error responses.", "Configured a demo-memory fallback and documented how to enable MongoDB persistence through an environment variable.", "Prepared project documentation and interface previews for review." ]),
        para("Results and Findings", "Section"),
        para("The local build produces a responsive dashboard and separate catalogue, request, and return views. The API reports whether MongoDB is connected or whether it is running in demo-memory mode. The current sample flow demonstrates the interface and core request lifecycle, but it is not a production-ready multi-user service: the demo mode resets when restarted, and the prototype does not include authentication or authorization.", "BodyTextCustom"),
        para("Conclusion", "Section"),
        para("LabDesk demonstrates a focused equipment checkout flow using a MERN-style architecture. It makes the catalogue, request queue, and return step visible in one interface. The next work should add sign-in and role checks, test each API path against a managed MongoDB deployment, protect secrets, and verify the complete workflow on the deployed URL before the project is used with real people or data.", "BodyTextCustom"),
        para("Appendix: Reference and use limits", "Section"),
        para("Reference project: LabFlow by Milan K B, https://github.com/milan-kb/LabFlow (MIT license). LabDesk is an independent implementation informed by the problem area and general workflow. This report does not claim an internship placement, user study, or production deployment. Interface preview pages contain illustrative sample records.", "Small")]
    make_doc(OUT / "LabDesk_Project_Report.pdf", story, "LabDesk Project Report")

def bullet_list(lines):
    return [para("-  " + item, "BulletCustom") for item in lines]

def grid_table(headers, rows, widths):
    data = [[para(f"<b>{h}</b>", "Small") for h in headers]] + [[para(v, "Small") for v in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), PALE), ("TEXTCOLOR", (0,0), (-1,0), INK), ("GRID", (0,0), (-1,-1), .45, LINE), ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 7), ("RIGHTPADDING", (0,0), (-1,-1), 7), ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
    return t

def make_srs():
    story = cover_block("LabDesk Software Requirements Specification", "Prototype requirements, workflows, and acceptance criteria", "Software requirements specification")
    story += [para("1. Purpose", "Section"), para("This specification defines the current LabDesk learning prototype and the behavior expected from its student-facing equipment request flow and staff-facing review flow. It is a basis for implementation review and future work, not a claim that deferred production controls are already present.", "BodyTextCustom"),
        para("2. Product Scope", "Section"), para("LabDesk supports a single teaching laboratory. Students browse equipment, submit a loan request with a purpose and due date, and review its status. A lab coordinator reviews requests and records returns. The current prototype uses sample records and has optional MongoDB persistence when configured.", "BodyTextCustom"),
        para("3. Users and Roles", "Section"), grid_table(["User", "Primary needs", "Current prototype"], [["Student", "Find available equipment and request a loan with a return date.", "Request form and equipment catalogue; no login."], ["Lab coordinator", "Review requests and record check-ins.", "Dashboard, request queue, and return view; not protected by server authorization."]], [31*mm, 66*mm, 67*mm]),
        para("4. Functional Requirements", "Section"), grid_table(["ID", "Requirement", "Acceptance criteria"], [
            ["FR-01", "Browse the equipment register.", "Show item name, category, tag, location, and status; filter by availability and search text."],
            ["FR-02", "Create a loan request.", "Require student name, equipment, purpose, and due date; return a validation message when any field is missing; new request appears in the queue."],
            ["FR-03", "Review a request.", "Staff can change a pending request to Approved; the status is visible on the request row."],
            ["FR-04", "Record a return.", "An approved request can be marked Returned and is reflected in the interface."],
            ["FR-05", "Report API readiness.", "GET /api/health returns ok and database state (connected or demo-memory)."],
            ["FR-06", "Persist data when configured.", "With MONGODB_URI set and the database reachable, equipment and requests use Mongoose models; otherwise demonstration data is held in memory."]
        ], [16*mm, 48*mm, 100*mm]),
        para("5. User Stories", "Section"),
        para("As a student, I want to find an available instrument so that I can plan a practical session. As a student, I want to submit the reason and due date so that the lab coordinator can review my request. As a coordinator, I want to approve and check in equipment so that the catalogue can reflect the loan lifecycle.", "BodyTextCustom"),
        para("6. Data Requirements", "Section"), grid_table(["Entity", "Fields"], [["Equipment", "name (required), category (required), tag (required and unique in MongoDB), status (Available, On loan, Maintenance), location, timestamps."], ["Loan request", "student, equipment, purpose, dueDate (required), status (Pending, Approved, Returned, Rejected), timestamps."]], [39*mm, 125*mm]),
        para("7. API Contract", "Section"), grid_table(["Method and path", "Purpose", "Response / errors"], [["GET /api/health", "Read service readiness.", "200 JSON with ok and database state."], ["GET /api/equipment", "List equipment.", "200 JSON array; server error uses a safe message."], ["POST /api/equipment", "Add an asset.", "201 created record; 400 if name, category, or tag is missing."], ["GET /api/requests", "List loan requests.", "200 JSON array."], ["POST /api/requests", "Create request.", "201 created record; 400 if a required field is missing."], ["PATCH /api/requests/:id/status", "Update request status.", "200 updated row; 400 for unsupported status; 404 for unknown id."]], [46*mm, 47*mm, 71*mm]),
        para("8. Quality Requirements", "Section"), *bullet_list(["Responsive layout should remain usable on mobile and desktop widths.", "Form controls must have visible labels; navigation and actions use semantic buttons.", "The API limits JSON bodies to 32 KB and validates required fields and allowed status values.", "Secrets belong in environment variables; no actual secret values should be committed.", "The current demo mode is non-persistent and must be labeled as such." ]),
        para("9. Assumptions and Limitations", "Section"), para("The prototype uses fictional names and equipment records. It has no authentication, role enforcement, ownership checks, real-time concurrency controls, audit log, email notification, or production database configuration. The browser app remains a demo until a MongoDB connection and deployment variables are configured and the live workflow is verified.", "BodyTextCustom"),
        para("10. Future Requirements", "Section"), para("Add student and coordinator sign-in, role-protected API routes, ownership rules, pagination, audit events, maintenance reporting, and integration checks against a managed MongoDB database. Reassess privacy, security, and hosting costs before production use.", "BodyTextCustom")]
    make_doc(OUT / "LabDesk_SRS.pdf", story, "LabDesk Software Requirements Specification")

# Draw a clean, full-viewport application preview that follows the built interface's
# current visual system and shows the actual demo labels and records.
def round_box(c, x, y, w, h, fill, stroke=LINE, radius=6):
    c.setFillColor(fill); c.setStrokeColor(stroke); c.roundRect(x, y, w, h, radius, fill=1, stroke=1)

def screen_header(c, width, height, active, page_title, subtitle):
    c.setFillColor(colors.HexColor("#F6F8FB")); c.rect(0, 0, width, height, fill=1, stroke=0)
    sidebar_w = 190
    c.setFillColor(NAVY); c.rect(0, 0, sidebar_w, height, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#9DBDF2")); c.roundRect(17, height-46, 25, 25, 7, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#284B76")); c.setFont("Helvetica-Bold", 12); c.drawCentredString(29.5, height-38, "L")
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 16); c.drawString(50, height-39, "labdesk")
    c.setFillColor(colors.HexColor("#1A2A3D")); c.roundRect(12, height-105, sidebar_w-24, 39, 7, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#D9E7F8")); c.roundRect(20, height-96, 22, 22, 5, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#284B76")); c.setFont("Helvetica-Bold", 9); c.drawCentredString(31, height-88, "N")
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 8); c.drawString(49, height-84, "Northstar Institute")
    c.setFillColor(colors.HexColor("#92A1B3")); c.setFont("Helvetica", 7); c.drawString(49, height-95, "Science department")
    c.setFillColor(colors.HexColor("#75859A")); c.setFont("Helvetica-Bold", 7); c.drawString(21, height-133, "W O R K S P A C E")
    labels=[("Overview","O"),("Equipment","E"),("Requests","R"),("Returns","V")]
    y=height-160
    for label,icon in labels:
        if label==active:
            c.setFillColor(colors.HexColor("#203952")); c.roundRect(11,y-4,sidebar_w-22,26,6,fill=1,stroke=0)
            c.setFillColor(colors.HexColor("#7FB0F1")); c.rect(11,y-4,2,26,fill=1,stroke=0)
        c.setFillColor(colors.HexColor("#EAF1FB") if label==active else colors.HexColor("#A8B3C1")); c.setFont("Helvetica",10); c.drawString(23,y+5,icon); c.setFont("Helvetica-Bold" if label==active else "Helvetica",8); c.drawString(44,y+5,label)
        y-=31
    c.setFillColor(colors.HexColor("#28394B")); c.line(15,42,sidebar_w-15,42)
    c.setFillColor(colors.HexColor("#D9E5F3")); c.circle(29,26,10,fill=1,stroke=0)
    c.setFillColor(colors.HexColor("#506985")); c.setFont("Helvetica-Bold",7); c.drawCentredString(29,23,"AM")
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold",8); c.drawString(46,28,"Alex Morgan")
    c.setFillColor(colors.HexColor("#92A1B3")); c.setFont("Helvetica",7); c.drawString(46,17,"Lab coordinator")
    c.setFillColor(colors.white); c.rect(sidebar_w,height-42,width-sidebar_w,42,fill=1,stroke=0)
    c.setStrokeColor(LINE); c.line(sidebar_w,height-42,width,height-42)
    c.setFillColor(MUTED); c.setFont("Helvetica",8); c.drawString(sidebar_w+25,height-25,"Workspace   /   ")
    c.setFillColor(INK); c.setFont("Helvetica-Bold",8); c.drawString(sidebar_w+85,height-25,active)
    c.setFillColor(colors.HexColor("#8C98A5")); c.setFont("Helvetica",7); c.drawRightString(width-27,height-25,"O  DEMO MODE     O")
    c.setFillColor(colors.HexColor("#8294A9")); c.setFont("Helvetica-Bold",7); c.drawString(sidebar_w+26,height-76,"MONDAY, OCTOBER 26, 2026")
    c.setFillColor(INK); c.setFont("Helvetica-Bold",20); c.drawString(sidebar_w+26,height-104,page_title)
    c.setFillColor(MUTED); c.setFont("Helvetica",9); c.drawString(sidebar_w+26,height-122,subtitle)
    return sidebar_w

def tag_status(c,x,y,label):
    scheme={"Available":(colors.HexColor("#EAF6EF"),colors.HexColor("#458C68")),"On loan":(colors.HexColor("#EDF3FC"),colors.HexColor("#537AB4")),"Maintenance":(colors.HexColor("#FBF2E3"),colors.HexColor("#A67D37")),"Pending":(colors.HexColor("#FBF2E3"),colors.HexColor("#A67D37")),"Approved":(colors.HexColor("#EDF3FC"),colors.HexColor("#537AB4")),"Returned":(colors.HexColor("#EAF6EF"),colors.HexColor("#458C68"))}
    bg,fg=scheme[label]; w=max(48,c.stringWidth(label,"Helvetica-Bold",7)+16)
    c.setFillColor(bg); c.roundRect(x,y-3,w,15,4,fill=1,stroke=0); c.setFillColor(fg); c.setFont("Helvetica-Bold",7); c.drawCentredString(x+w/2,y+2,label)

def title_panel(c,x,y,w,title,caption):
    round_box(c,x,y,w,44,colors.white)
    c.setFillColor(MUTED); c.setFont("Helvetica-Bold",6.5); c.drawString(x+13,y+29,caption.upper())
    c.setFillColor(INK); c.setFont("Helvetica-Bold",12); c.drawString(x+13,y+12,title)

def make_screens():
    path=OUT/"LabDesk_Interface_Previews.pdf"
    width,height=landscape(A4)
    c=canvas.Canvas(str(path), pagesize=(width,height), pageCompression=1)
    screens=["Overview","Equipment","Requests","Returns"]
    for page in screens:
        sidebar=screen_header(c,width,height,page,{"Overview":"Good morning, Alex","Equipment":"All equipment","Requests":"Request queue","Returns":"Expected returns"}[page],{"Overview":"Here's what's happening in your lab today.","Equipment":"Keep track of every instrument and asset in your lab.","Requests":"Review student requests and keep projects moving.","Returns":"Check in returned equipment and keep records up to date."}[page])
        x=sidebar+24; right=width-24; usable=right-x
        if page=="Overview":
            gap=9; cardw=(usable-3*gap)/4; y=height-225
            cards=[("TOTAL EQUIPMENT","6","Across 3 categories",BLUE),("AVAILABLE NOW","4","67% of inventory",MINT),("ON LOAN","1","1 due back this week",AMBER),("PENDING REQUESTS","1","Needs your attention",PURPLE)]
            for i,(label,val,note,col) in enumerate(cards):
                cx=x+i*(cardw+gap); round_box(c,cx,y,cardw,74,colors.white)
                c.setFillColor(col); c.circle(cx+18,y+56,7,fill=1,stroke=0); c.setFillColor(MUTED); c.setFont("Helvetica-Bold",6); c.drawString(cx+31,y+54,label)
                c.setFillColor(INK); c.setFont("Helvetica-Bold",18); c.drawString(cx+14,y+30,val); c.setFillColor(MUTED); c.setFont("Helvetica",7); c.drawString(cx+14,y+13,note)
            panel_y=height-456; panel_h=207; leftw=usable*.63-5; rightx=x+leftw+10; rightw=usable-leftw-10
            round_box(c,x,panel_y,leftw,panel_h,colors.white); c.setFillColor(MUTED); c.setFont("Helvetica-Bold",6); c.drawString(x+13,panel_y+panel_h-18,"INVENTORY")
            c.setFillColor(INK); c.setFont("Helvetica-Bold",12); c.drawString(x+13,panel_y+panel_h-35,"Equipment overview")
            c.setFillColor(BLUE); c.setFont("Helvetica-Bold",7); c.drawRightString(x+leftw-13,panel_y+panel_h-27,"View all  ->")
            c.setStrokeColor(LINE); c.line(x+12,panel_y+panel_h-48,x+leftw-12,panel_y+panel_h-48)
            headers=[("ITEM",x+13),("ASSET TAG",x+leftw*.55),("LOCATION",x+leftw*.72),("STATUS",x+leftw*.87)]
            for label,xx in headers: c.setFillColor(MUTED); c.setFont("Helvetica-Bold",5.5); c.drawString(xx,panel_y+panel_h-62,label)
            rows=[("Digital Oscilloscope","EL-204","Bench 04","Available"),("Arduino Starter Kit","PR-118","Cabinet B","On loan"),("Digital Multimeter","EL-087","Bench 02","Available"),("Soldering Station","PR-032","Service desk","Maintenance")]
            yy=panel_y+panel_h-83
            for name,tag,loc,status in rows:
                c.setStrokeColor(LINE); c.line(x+12,yy-8,x+leftw-12,yy-8)
                c.setFillColor(INK); c.setFont("Helvetica-Bold",7); c.drawString(x+13,yy,name)
                c.setFillColor(MUTED); c.setFont("Helvetica",6.5); c.drawString(x+leftw*.55,yy,tag); c.drawString(x+leftw*.72,yy,loc)
                tag_status(c,x+leftw*.87,yy-2,status); yy-=30
            round_box(c,rightx,panel_y,rightw,panel_h,colors.white); c.setFillColor(MUTED); c.setFont("Helvetica-Bold",6); c.drawString(rightx+13,panel_y+panel_h-18,"NEEDS REVIEW")
            c.setFillColor(INK); c.setFont("Helvetica-Bold",12); c.drawString(rightx+13,panel_y+panel_h-35,"Recent requests")
            requests=[("Ananya Menon","Arduino Starter Kit","Oct 29","Pending"),("Rohan Das","Digital Multimeter","Oct 28","Approved"),("Meera Nair","Digital Oscilloscope","Oct 26","Returned")]
            yy=panel_y+panel_h-67
            for name,item,due,status in requests:
                c.setFillColor(colors.HexColor("#E8F1FB")); c.circle(rightx+22,yy+4,9,fill=1,stroke=0); c.setFillColor(BLUE); c.setFont("Helvetica-Bold",5.5); c.drawCentredString(rightx+22,yy+2,name[0]+"M")
                c.setFillColor(INK); c.setFont("Helvetica-Bold",7); c.drawString(rightx+38,yy+7,name); c.setFillColor(MUTED); c.setFont("Helvetica",6); c.drawString(rightx+38,yy-4,item+" | Due "+due)
                tag_status(c,rightx+rightw-65,yy-2,status); yy-=45
            low_y=25; low_h=height-480
            round_box(c,x,low_y,leftw,low_h,colors.white); c.setFillColor(MUTED); c.setFont("Helvetica-Bold",6); c.drawString(x+13,low_y+low_h-17,"AT A GLANCE")
            c.setFillColor(INK); c.setFont("Helvetica-Bold",11); c.drawString(x+13,low_y+low_h-34,"Lab activity")
            for j in range(4):
                gy=low_y+low_h-52-j*19; c.setStrokeColor(LINE); c.line(x+42,gy,x+leftw-15,gy)
            for i,day in enumerate("MTWTFSS"):
                bx=x+70+i*(leftw-95)/6; c.setFillColor(colors.HexColor("#82A0D8")); c.roundRect(bx,low_y+18,7,15+((i*7)%25),3,fill=1,stroke=0); c.setFillColor(colors.HexColor("#80C5A6")); c.roundRect(bx+9,low_y+18,7,10+((i*11)%31),3,fill=1,stroke=0); c.setFillColor(MUTED); c.setFont("Helvetica",6); c.drawCentredString(bx+8,low_y+7,day)
            round_box(c,rightx,low_y,rightw,low_h,colors.HexColor("#F9FBFD")); c.setFillColor(BLUE); c.setFont("Helvetica-Bold",6); c.drawString(rightx+13,low_y+low_h-20,"*  LAB TIP")
            c.setFillColor(INK); c.setFont("Helvetica-Bold",11); c.drawString(rightx+13,low_y+low_h-42,"Ready for the next class?")
            c.setFillColor(MUTED); c.setFont("Helvetica",7); c.drawString(rightx+13,low_y+low_h-57,"Check upcoming bookings and ensure high-demand")
            c.drawString(rightx+13,low_y+low_h-68,"equipment is back on the shelf.")
            c.setFillColor(BLUE); c.setFont("Helvetica-Bold",7); c.drawString(rightx+13,low_y+16,"Review availability  ->")
        else:
            py=height-230; ph=py-28
            round_box(c,x,28,usable,ph,colors.white)
            if page=="Equipment":
                c.setFillColor(MUTED); c.setFont("Helvetica-Bold",6); c.drawString(x+14,py-20,"ASSET REGISTER")
                c.setFillColor(INK); c.setFont("Helvetica-Bold",12); c.drawString(x+14,py-38,"All equipment")
                c.setFillColor(BLUE); c.roundRect(right-115,py-45,99,24,5,fill=1,stroke=0); c.setFillColor(colors.white); c.setFont("Helvetica-Bold",7); c.drawCentredString(right-65.5,py-36,"+  Add equipment")
                c.setStrokeColor(LINE); c.line(x+13,py-57,right-13,py-57)
                columns=[("ITEM",x+14),("ASSET TAG",x+usable*.51),("LOCATION",x+usable*.69),("STATUS",x+usable*.85)]
                for label,xx in columns: c.setFillColor(MUTED); c.setFont("Helvetica-Bold",6); c.drawString(xx,py-73,label)
                rows=[("Digital Oscilloscope","Electronics","EL-204","Bench 04","Available"),("Arduino Starter Kit","Prototyping","PR-118","Cabinet B","On loan"),("Digital Multimeter","Electronics","EL-087","Bench 02","Available"),("Soldering Station","Prototyping","PR-032","Service desk","Maintenance"),("Bench Power Supply","Electronics","EL-143","Bench 07","Available"),("Raspberry Pi 5 Kit","Computing","CO-061","Cabinet A","Available")]
                yy=py-99
                for name,cat,tag,loc,status in rows:
                    c.setStrokeColor(LINE); c.line(x+13,yy-10,right-13,yy-10)
                    c.setFillColor(INK); c.setFont("Helvetica-Bold",8); c.drawString(x+14,yy,name); c.setFillColor(MUTED); c.setFont("Helvetica",6.5); c.drawString(x+14,yy-11,cat)
                    c.drawString(x+usable*.51,yy,tag); c.drawString(x+usable*.69,yy,loc); tag_status(c,x+usable*.85,yy-3,status); yy-=41
            elif page=="Requests":
                c.setFillColor(MUTED); c.setFont("Helvetica-Bold",6); c.drawString(x+14,py-20,"LOAN WORKFLOW")
                c.setFillColor(INK); c.setFont("Helvetica-Bold",12); c.drawString(x+14,py-38,"Request queue")
                c.setStrokeColor(LINE); c.line(x+13,py-57,right-13,py-57)
                headers=[("STUDENT",x+14),("EQUIPMENT",x+usable*.24),("PURPOSE",x+usable*.46),("DUE DATE",x+usable*.72),("STATUS",x+usable*.84),("ACTION",x+usable*.94)]
                c.setFillColor(MUTED); c.setFont("Helvetica-Bold",5.5)
                for label,xx in headers:c.drawString(xx,py-75,label)
                rows=[("Ananya Menon","Arduino Starter Kit","Sensor calibration lab","Oct 29","Pending","Approve"),("Rohan Das","Digital Multimeter","Circuit analysis assignment","Oct 28","Approved","More"),("Meera Nair","Digital Oscilloscope","Signal measurement practical","Oct 26","Returned","More")]
                yy=py-102
                for name,item,purpose,due,status,action in rows:
                    c.setStrokeColor(LINE); c.line(x+13,yy-9,right-13,yy-9)
                    c.setFillColor(colors.HexColor("#E8F1FB")); c.circle(x+22,yy+2,8,fill=1,stroke=0); c.setFillColor(BLUE); c.setFont("Helvetica-Bold",5); c.drawCentredString(x+22,yy,name[0]+"M")
                    c.setFillColor(INK); c.setFont("Helvetica-Bold",6.5); c.drawString(x+35,yy,name)
                    c.setFillColor(MUTED); c.setFont("Helvetica",6.2); c.drawString(x+usable*.24,yy,item); c.drawString(x+usable*.46,yy,purpose); c.drawString(x+usable*.72,yy,due)
                    tag_status(c,x+usable*.84,yy-3,status); c.setFillColor(BLUE); c.setFont("Helvetica-Bold",6); c.drawString(x+usable*.94,yy,action); yy-=43
            else:
                c.setFillColor(MUTED); c.setFont("Helvetica-Bold",6); c.drawString(x+14,py-20,"CHECK IN")
                c.setFillColor(INK); c.setFont("Helvetica-Bold",12); c.drawString(x+14,py-38,"Expected returns")
                c.setStrokeColor(LINE); c.line(x+13,py-57,right-13,py-57)
                c.setFillColor(colors.HexColor("#EDF7F2")); c.roundRect(x+18,py-112,36,36,8,fill=1,stroke=0)
                c.setFillColor(MINT); c.setFont("Helvetica-Bold",10); c.drawCentredString(x+36,py-99,"OK")
                c.setFillColor(INK); c.setFont("Helvetica-Bold",9); c.drawString(x+68,py-91,"Digital Multimeter")
                c.setFillColor(MUTED); c.setFont("Helvetica",7); c.drawString(x+68,py-105,"Checked out to Rohan Das  |  Due Oct 28")
                c.setFillColor(BLUE); c.roundRect(right-124,py-107,106,24,5,fill=1,stroke=0); c.setFillColor(colors.white); c.setFont("Helvetica-Bold",7); c.drawCentredString(right-71,py-98,"OK  Mark returned")
                c.setFillColor(colors.HexColor("#F6F8FB")); c.roundRect(x+18,py-175,usable-36,44,6,fill=1,stroke=0); c.setFillColor(MUTED); c.setFont("Helvetica",8); c.drawCentredString(x+usable/2,py-157,"One approved loan is currently expected back.")
        c.setFillColor(MUTED); c.setFont("Helvetica",6); c.drawString(x,13,"(c) 2026 LabDesk | Northstar Institute")
        c.setFont("Helvetica",6); c.drawRightString(right,13,"Learning demo | Illustrative sample records")
        c.showPage()
    c.save()

if __name__ == "__main__":
    make_report()
    make_srs()
    make_screens()
    print("Created 3 PDFs in output/pdf")
