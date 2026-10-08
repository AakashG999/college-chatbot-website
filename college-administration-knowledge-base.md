# College Administration Knowledge Base

> **Purpose of this document**: This is a reference knowledge base about a
> college's administration, written to be used as a source document for a
> Retrieval-Augmented Generation (RAG) chatbot. It uses realistic **placeholder**
> content for a fictional "Greenfield College" — replace every fact, date, fee
> amount, and contact with your institution's real information before using it
> in production.
>
> **How to use this with a RAG pipeline**:
> - Split the document on `##` (top-level topic) headings — each becomes a
>   natural chunk or group of chunks. Sections are self-contained so a chunk
>   read in isolation still makes sense.
> - The `category:` line under each `##` heading can be lifted into that
>   chunk's metadata (for metadata filtering during retrieval, as this
>   project's own ingestion pipeline does).
> - Keep each `###` subsection together where possible (don't split a
>   subsection across two chunks) — a chunk size of 500–800 tokens with
>   50–100 token overlap works well for this content.
> - Re-run ingestion any time a section below changes, and keep a changelog
>   (see the bottom of this document) so stale chunks can be identified.

---

## Table of Contents

1. [Admissions](#admissions) — `category: admissions`
2. [Fees and Scholarships](#fees-and-scholarships) — `category: fees`
3. [Academic Calendar and Curriculum](#academic-calendar-and-curriculum) — `category: academics`
4. [Examinations](#examinations) — `category: exams`
5. [Hostel and Campus Facilities](#hostel-and-campus-facilities) — `category: hostel`
6. [Library Services](#library-services) — `category: library`
7. [IT Services and Student Portal](#it-services-and-student-portal) — `category: it`
8. [Student Code of Conduct and Anti-Ragging Policy](#student-code-of-conduct-and-anti-ragging-policy) — `category: conduct`
9. [Grievance Redressal](#grievance-redressal) — `category: grievance`
10. [Placements and Career Services](#placements-and-career-services) — `category: placements`
11. [Student Clubs, Activities, and Transportation](#student-clubs-activities-and-transportation) — `category: campus-life`
12. [International and Exchange Students](#international-and-exchange-students) — `category: international`
13. [Health and Wellness](#health-and-wellness) — `category: health`
14. [Convocation and Alumni Relations](#convocation-and-alumni-relations) — `category: alumni`
15. [Administration Contacts Directory](#administration-contacts-directory) — `category: contact`

---

## Admissions
category: admissions

### Eligibility
Candidates must have completed higher secondary education (10+2) with a
minimum of 60% aggregate marks in the relevant stream:
- **Science stream** (Physics, Chemistry, Mathematics/Biology) for B.Tech,
  B.Sc programs
- **Commerce stream** for B.Com, BBA programs
- **Any stream** for BA, BA (Hons) programs

A relaxation of 5% is granted to candidates from reserved categories (SC/ST/OBC/PwD) as per government norms.

### How to Apply
1. Fill out the online application form on the college admissions portal
   (admissions.greenfieldcollege.edu).
2. Upload scanned copies of marksheets, transfer certificate, migration
   certificate, and a recent passport-size photograph.
3. Pay the non-refundable application fee of INR 1,000 (INR 500 for
   reserved category applicants).
4. Appear for the entrance test (for B.Tech and MBA programs) or submit
   qualifying exam scores (e.g., JEE Main, CUET) for other programs.
5. Shortlisted candidates are called for document verification and
   counselling before seat allotment.

### Important Dates (Academic Year 2026–27)
| Milestone | Date |
|---|---|
| Application window opens | June 1 |
| Application window closes | July 15 |
| Entrance test (B.Tech / MBA) | July 22 |
| Merit list release | July 30 |
| Document verification and counselling | August 1–8 |
| Admission confirmation and fee payment deadline | August 10 |
| Classes begin | August 18 |

### Documents Required
- 10th and 12th grade marksheets and passing certificates
- Transfer certificate (TC) and migration certificate (if from another board/university)
- Category certificate (for reserved category applicants)
- Income certificate (for need-based scholarship applicants)
- Four passport-size photographs
- Government-issued photo ID (Aadhaar card, passport, or voter ID)
- Entrance test admit card and scorecard, where applicable

### Lateral Entry and Transfer Admissions
Diploma holders may apply for lateral entry into the second year of
relevant B.Tech programs, subject to seat availability (typically 10% of
sanctioned intake). Students seeking transfer from another recognized
institution must have a minimum CGPA of 7.0 and apply within the first two
weeks of the semester.

### Contact for Admissions Queries
Admissions Office, Ground Floor, Main Administrative Block.
Email: admissions@greenfieldcollege.edu | Phone: +91-11-2345-6789
(Office hours: 10 AM–5 PM, Monday–Saturday)

---

## Fees and Scholarships
category: fees

### Tuition Fee Structure (per annum, Academic Year 2026–27)
| Program | Annual Tuition Fee |
|---|---|
| B.Tech | INR 1,20,000 |
| B.Sc | INR 60,000 |
| B.Com | INR 55,000 |
| BA | INR 50,000 |
| BBA | INR 75,000 |
| MBA | INR 2,00,000 |

Fees are payable in two equal installments: at the start of each semester
(before August 10 for the odd semester, before January 10 for the even
semester).

### Other Recurring Charges
- Hostel fee (including mess): INR 90,000 per annum
- Library security deposit (refundable): INR 2,000, one-time
- Student activity and sports fee: INR 5,000 per annum
- Examination fee: INR 1,500 per semester

### Payment Methods
Fees can be paid online via the student portal (net banking, UPI, debit or
credit card) or offline via demand draft payable to "Greenfield College" at
the Accounts Office. A payment receipt is generated instantly on the portal
and should be retained for all future reference.

### Late Payment Policy
A late fee of INR 500 per week applies after the due date, up to a maximum
of 4 weeks. Students who have not cleared dues within this grace period may
be de-registered from courses for that semester and barred from appearing
in semester-end examinations.

### Fee Refund Policy
Students who withdraw admission within 7 days of the start of classes are
eligible for a full tuition refund minus a processing fee of INR 2,000, as
per UGC refund guidelines. No refund is applicable after the add/drop
period ends.

### Scholarships
- **Merit Scholarship**: 25–100% tuition waiver based on entrance test rank
  or qualifying exam percentile; renewed annually subject to maintaining a
  minimum 7.5 CGPA with no active disciplinary action.
- **Need-based Financial Aid**: Partial fee waiver (up to 50%) for students
  from economically weaker sections, subject to verified family income
  below INR 8,00,000 per annum.
- **Sports & Cultural Scholarships**: Partial tuition waiver for students
  representing the college at state or national level competitions,
  awarded by the Sports and Cultural Affairs Committee.
- **Alumni-funded Scholarships**: A small number of scholarships funded by
  the Alumni Association, awarded based on a combination of merit and need.

Scholarship applications open alongside admissions and must be submitted
through the Student Welfare Office along with supporting documents within
30 days of admission confirmation.

### Contact for Fee Queries
Accounts Office, 1st Floor, Main Administrative Block.
Email: accounts@greenfieldcollege.edu | Phone: +91-11-2345-6790

---

## Academic Calendar and Curriculum
category: academics

### Semester Structure
The academic year is divided into two semesters:
- **Odd Semester**: August – December
- **Even Semester**: January – May

A compulsory summer term (4 weeks, June) is offered for students who need
to clear backlog courses or wish to take up additional electives/internships.

### Key Academic Dates (Odd Semester, illustrative)
- Classes begin: August 18
- Mid-semester exams: October 10–17
- Mid-term break: last week of October
- Last date to withdraw from a course without academic penalty: October 25
- Semester-end exams: December 5–20
- Result declaration: January 10
- Winter break: December 21 – January 5

### Attendance Policy
Students must maintain a minimum of 75% attendance in each registered
course to be eligible to sit for the semester-end exam in that course.
Students with attendance between 65–75% may apply for condonation through
the Dean of Academics' office with valid supporting documents (medical
certificates, participation certificates for college-representing events,
etc.). Attendance below 65% results in automatic debarment from the
semester-end exam for that course, with no exceptions.

### Grading System
The college follows a 10-point Cumulative Grade Point Average (CGPA)
system:

| Grade | Grade Point | Marks Range |
|---|---|---|
| O (Outstanding) | 10 | 90–100% |
| A+ (Excellent) | 9 | 80–89% |
| A (Very Good) | 8 | 70–79% |
| B+ (Good) | 7 | 60–69% |
| B (Above Average) | 6 | 50–59% |
| C (Average) | 5 | 45–49% |
| P (Pass) | 4 | 40–44% |
| F (Fail) | 0 | Below 40% |

Grade cards are released within 15 days of the semester-end exams via the
student portal. Degree classification (First Class, First Class with
Distinction, etc.) is based on the final CGPA at graduation.

### Credit System and Electives
Each program follows a credit-based curriculum (typically 20–24 credits
per semester). Students can choose open electives from other departments,
subject to seat availability, to be registered during the course
registration window in the first week of each semester. A maximum of two
open electives may be taken per semester.

### Academic Probation and Dismissal
A student whose semester CGPA falls below 5.0 in two consecutive semesters
is placed on academic probation and must meet with an academic advisor.
Failure to improve CGPA above 5.0 in the following semester may result in
dismissal from the program, subject to review by the Academic Standards
Committee.

### Contact for Academic Queries
Office of the Dean of Academics, 2nd Floor, Main Administrative Block.
Email: academics@greenfieldcollege.edu | Phone: +91-11-2345-6791

---

## Examinations
category: exams

### Exam Types and Weightage
- Mid-semester exams: 20% weightage
- Semester-end exams: 50% weightage
- Internal assessments, assignments, and quizzes: 30% weightage

### Admit Cards
Admit cards are released on the student portal 7 days before the
semester-end exams begin. Students with pending fee dues or attendance
shortfalls will not be able to download their admit card until the issue
is resolved with the respective office.

### Re-evaluation / Revaluation
Students may apply for re-evaluation of a semester-end exam answer script
within 10 days of result declaration, by paying a re-evaluation fee of INR
500 per subject via the student portal. Revaluation results are typically
published within 3 weeks of application. If the revised grade is higher,
the fee is refunded.

### Supplementary / Backlog Exams
Students who fail a course can appear for the supplementary exam conducted
within 4 weeks of the regular result declaration. A maximum of 2
supplementary attempts are allowed per course; if a student still fails,
the course must be repeated in a subsequent regular semester offering.

### Malpractice and Code of Conduct During Exams
Any form of malpractice during exams (use of unauthorized material,
impersonation, communication devices, etc.) results in immediate
cancellation of that exam paper. Depending on severity, the Examination
Disciplinary Committee may impose further penalties ranging from a
one-semester suspension to expulsion, as per the Examination Code of
Conduct published on the student portal.

### Special Accommodations
Students with documented disabilities or temporary medical conditions
(e.g., a fractured writing hand) may request exam accommodations
(extended time, scribe, separate room) by applying to the Examination Cell
at least 2 weeks before the exam, along with medical documentation.

### Contact for Exam Queries
Examination Cell, 2nd Floor, Main Administrative Block.
Email: exams@greenfieldcollege.edu | Phone: +91-11-2345-6792

---

## Hostel and Campus Facilities
category: hostel

### Hostel Accommodation
Separate hostels are available for male and female students on campus,
allotted on a first-come-first-served basis to outstation students,
subject to availability. Hostel fee (including mess) is INR 90,000 per
annum, payable in two installments alongside tuition fees.

### Room Types
- Shared rooms (2–3 students): included in standard hostel fee
- Single occupancy rooms: additional INR 20,000 per annum, subject to
  availability, allotted by seniority

### Hostel Rules
- Entry curfew: 9:30 PM on weekdays, 11:00 PM on weekends and before
  holidays.
- Visitors are allowed only in designated common areas during visiting
  hours (4 PM–7 PM); overnight guests are not permitted.
- Ragging in any form is strictly prohibited and punishable under the
  college's anti-ragging policy (see the Student Code of Conduct section).
- Possession of prohibited substances or electrical appliances not on the
  approved list results in confiscation and disciplinary action.

### Mess Facility
The hostel mess offers both vegetarian and non-vegetarian meal plans.
Students can switch meal plans once per semester by applying at the
Hostel Office at least one week before the start of the semester.

### Campus Facilities
- **Central Library**: open 8 AM–10 PM on working days (see Library
  Services section for details)
- **Health Center**: on-campus doctor available 9 AM–5 PM on weekdays,
  with a tie-up with City General Hospital for emergencies (see Health
  and Wellness section)
- **Sports Complex**: basketball and volleyball courts, a football/cricket
  ground, an indoor badminton and table tennis hall, and a gymnasium
  (6 AM–9 PM daily)
- **Campus Wi-Fi**: available college-wide to all registered students
  using their college-issued credentials
- **Cafeteria and Food Court**: multiple outlets open 8 AM–9 PM, cashless
  payment via student ID card

### Contact for Hostel Queries
Hostel Office, Hostel Block A, Ground Floor.
Email: hostel@greenfieldcollege.edu | Phone: +91-11-2345-6793

---

## Library Services
category: library

### Collection and Access
The Central Library holds over 50,000 print titles, 10,000+ e-books, and
subscriptions to more than 40 academic journals and databases (including
IEEE Xplore and JSTOR), accessible both on-campus and remotely via VPN
with college credentials.

### Timings
Open 8 AM–10 PM on working days, and 10 AM–6 PM on Sundays and public
holidays during exam periods (extended hours are announced before each
exam season).

### Borrowing Policy
- Undergraduate students: up to 4 books for 14 days
- Postgraduate students: up to 6 books for 21 days
- Faculty: up to 10 books for 30 days

Overdue fines are INR 2 per book per day. Lost books must be replaced or
paid for at twice the book's listed price.

### Study Spaces
The library offers silent study zones, group discussion rooms (bookable
via the library portal, up to 2 hours per booking), and a 24-hour reading
room accessible during the two weeks preceding semester-end exams.

### Contact for Library Queries
Central Library, Academic Block, 1st Floor.
Email: library@greenfieldcollege.edu | Phone: +91-11-2345-6796

---

## IT Services and Student Portal
category: it

### Student Portal
All academic and administrative transactions (fee payment, course
registration, grade cards, hostel applications, admit card downloads) are
conducted through the student portal at portal.greenfieldcollege.edu,
accessible using the college-issued student ID and a password set during
onboarding.

### Email and Wi-Fi Credentials
Every admitted student receives a college email address
(firstname.lastname@greenfieldcollege.edu) and Wi-Fi login credentials
during orientation week. Passwords must be reset within 90 days as per
the IT security policy.

### Common Issues and Resets
Students who forget their portal or email password can use the
"Forgot Password" self-service option, which sends a reset link to their
registered personal email and phone number. If self-service fails,
students should visit the IT Helpdesk in person with their student ID.

### Acceptable Use Policy
College IT resources (Wi-Fi, email, portal) must not be used for
commercial activity, copyright infringement, or any activity violating
the Student Code of Conduct. Violations may result in suspension of IT
access pending disciplinary review.

### Contact for IT Queries
IT Helpdesk, Academic Block, Ground Floor.
Email: ithelp@greenfieldcollege.edu | Phone: +91-11-2345-6795

---

## Student Code of Conduct and Anti-Ragging Policy
category: conduct

### General Code of Conduct
Students are expected to maintain discipline, punctuality, and respectful
behavior towards faculty, staff, and fellow students, both on campus and
during college-organized off-campus activities. Violations are reviewed
by the Student Disciplinary Committee, which can impose penalties ranging
from a warning to expulsion depending on severity.

### Anti-Ragging Policy
Ragging in any form — physical, verbal, or psychological — is strictly
prohibited, in line with UGC anti-ragging regulations. This includes but
is not limited to:
- Forcing a junior student to perform any act causing physical or mental
  distress
- Any act that disrupts the academic or hostel routine of a student
- Teasing, abusing, or playing practical jokes that cause embarrassment

**Reporting**: Incidents can be reported anonymously via the Anti-Ragging
Helpline (1800-XXX-XXXX, toll-free, 24x7) or directly to the Anti-Ragging
Committee at antiragging@greenfieldcollege.edu. All reports are
investigated within 7 days, and interim protective measures are provided
to the complainant where needed.

**Penalties**: Range from suspension of hostel privileges to expulsion
and reporting to local police, as mandated by UGC regulations.

### Prevention of Sexual Harassment (POSH) / Internal Complaints Committee
The college maintains an Internal Complaints Committee (ICC) as mandated
by the POSH Act, 2013, to address complaints of sexual harassment from
students, faculty, or staff. Complaints can be filed confidentially with
the ICC via icc@greenfieldcollege.edu. The ICC guarantees confidentiality
and completes inquiries within 90 days as per statutory requirements.

### Contact for Code of Conduct Queries
Office of Student Affairs, Main Administrative Block, 2nd Floor.
Email: studentaffairs@greenfieldcollege.edu | Phone: +91-11-2345-6797

---

## Grievance Redressal
category: grievance

### Student Grievance Portal
Students can submit academic, administrative, or facility-related
grievances through the online Student Grievance Portal
(grievance.greenfieldcollege.edu) or in person at the Dean of Students'
office. Each grievance is assigned a tracking number and an expected
resolution timeline.

### Resolution Timeline
- Simple administrative grievances (e.g., fee receipt errors): 3 working
  days
- Academic grievances (e.g., grade disputes): 10 working days, following
  review by the relevant department
- Complex grievances requiring committee review: up to 30 working days,
  with interim status updates provided every 7 days

### Escalation
If a grievance is not resolved within the stated timeline, or the
student is unsatisfied with the resolution, it can be escalated to the
Grievance Redressal Committee, chaired by the Dean of Students, which
meets monthly.

### Contact for Grievances
Office of the Dean of Students, Main Administrative Block, 2nd Floor.
Email: grievance@greenfieldcollege.edu | Phone: +91-11-2345-6798

---

## Placements and Career Services
category: placements

### Placement Process
The Training and Placement Cell (TPC) coordinates on-campus recruitment
during the final year of each program. Eligibility requires a minimum
CGPA of 6.0 with no active backlogs at the time of the placement drive.

### Placement Season Timeline (illustrative)
- Pre-placement talks and registration: July–August
- Placement season (Tier-1 companies): August–October
- Placement season (Tier-2/3 companies): November–February
- Internship drives (for pre-final year students): January–March

### Career Services
- Resume building and mock interview workshops, conducted each semester
- Industry mentorship program connecting students with alumni in their
  field of interest
- Internship facilitation for academic credit (minimum 6 weeks, subject
  to department approval)

### Contact for Placement Queries
Training and Placement Cell, Academic Block, 3rd Floor.
Email: placements@greenfieldcollege.edu | Phone: +91-11-2345-6799

---

## Student Clubs, Activities, and Transportation
category: campus-life

### Student Clubs
Over 25 registered student clubs covering technical (robotics, coding),
cultural (dance, music, drama), literary, and social service domains.
Clubs are allotted an annual budget by the Student Council and must
register their events with the Dean of Student Affairs at least 2 weeks
in advance.

### Annual Fests
- **Technical fest** (February): project exhibitions, hackathons,
  technical paper presentations
- **Cultural fest** (March): inter-college cultural competitions, concerts

### Student Council
Elected annually by the student body, the Student Council represents
student interests in administrative committees and organizes campus-wide
events and welfare initiatives.

### Campus Transportation
College buses operate on 12 routes covering major parts of the city,
with a transport fee of INR 18,000 per annum, payable alongside tuition
fees. Bus passes are issued by the Transport Office and routes/timings
are published each semester on the student portal.

### Contact for Clubs/Transportation Queries
Office of Student Affairs (clubs) / Transport Office (bus passes),
Main Administrative Block, Ground Floor.
Email: studentaffairs@greenfieldcollege.edu (clubs) /
transport@greenfieldcollege.edu (buses)

---

## International and Exchange Students
category: international

### Admission Process for International Students
International applicants apply through a separate portal
(international.greenfieldcollege.edu) and are evaluated based on
equivalent qualifications certified by the Association of Indian
Universities (AIU). A separate, higher international tuition fee
structure applies.

### Visa and FRRO Registration
The International Students Office assists with student visa
documentation and mandatory FRRO (Foreigner Regional Registration
Office) registration within 14 days of arrival in India.

### Exchange Programs
The college maintains exchange agreements with 8 partner universities
across Europe and Southeast Asia, allowing students to spend one semester
abroad with credit transfer, subject to a minimum CGPA of 7.5 and
department approval.

### Contact for International Student Queries
International Students Office, Main Administrative Block, 1st Floor.
Email: international@greenfieldcollege.edu | Phone: +91-11-2345-6794

---

## Health and Wellness
category: health

### On-Campus Health Center
A qualified doctor is available on campus from 9 AM–5 PM on weekdays for
general consultations and minor treatment, free of charge for registered
students. The Health Center maintains a tie-up with City General Hospital
for emergencies and specialist referrals.

### Student Insurance
All students are covered under a group medical insurance policy
(hospitalization cover up to INR 1,00,000 per annum), included in the
annual fee. Claim forms are available at the Health Center.

### Counselling Services
The college provides confidential student counselling services (academic
stress, personal concerns, career guidance) through the Student
Counselling Center, available by appointment on weekdays. Walk-in slots
are available for urgent concerns.

### Contact for Health Queries
Health Center, near Hostel Block A.
Email: health@greenfieldcollege.edu | Phone: +91-11-2345-6800
Student Counselling Center: counselling@greenfieldcollege.edu

---

## Convocation and Alumni Relations
category: alumni

### Convocation
The annual convocation ceremony is held each September for students who
completed their program in the preceding academic year. Degree
certificates are issued on convocation day; provisional certificates are
available earlier via the student portal for students needing proof of
graduation sooner (e.g., for job offers).

### Alumni Association
All graduates automatically become members of the Greenfield College
Alumni Association, which organizes annual alumni meets, mentorship
programs for current students, and manages alumni-funded scholarships.

### Contact for Convocation/Alumni Queries
Office of the Registrar (convocation) / Alumni Relations Office.
Email: registrar@greenfieldcollege.edu (convocation) /
alumni@greenfieldcollege.edu (alumni association)

---

## Administration Contacts Directory
category: contact

| Office | Email | Phone |
|---|---|---|
| Admissions Office | admissions@greenfieldcollege.edu | +91-11-2345-6789 |
| Accounts Office | accounts@greenfieldcollege.edu | +91-11-2345-6790 |
| Dean of Academics | academics@greenfieldcollege.edu | +91-11-2345-6791 |
| Examination Cell | exams@greenfieldcollege.edu | +91-11-2345-6792 |
| Hostel Office | hostel@greenfieldcollege.edu | +91-11-2345-6793 |
| International Students Office | international@greenfieldcollege.edu | +91-11-2345-6794 |
| IT Helpdesk | ithelp@greenfieldcollege.edu | +91-11-2345-6795 |
| Central Library | library@greenfieldcollege.edu | +91-11-2345-6796 |
| Office of Student Affairs | studentaffairs@greenfieldcollege.edu | +91-11-2345-6797 |
| Dean of Students (Grievances) | grievance@greenfieldcollege.edu | +91-11-2345-6798 |
| Training and Placement Cell | placements@greenfieldcollege.edu | +91-11-2345-6799 |
| Health Center | health@greenfieldcollege.edu | +91-11-2345-6800 |
| Anti-Ragging Committee | antiragging@greenfieldcollege.edu | 1800-XXX-XXXX (toll-free) |
| Internal Complaints Committee (POSH) | icc@greenfieldcollege.edu | — |

### General Office Hours
Administrative offices are open Monday–Saturday, 10 AM–5 PM, except on
public holidays and during the mid-term break (last week of October).

### Campus Address
Greenfield College, 123 Education Avenue, New Delhi, 110001, India.

---

## Document Changelog

| Date | Section(s) Changed | Notes |
|---|---|---|
| 2026-10-01 | All sections | Initial version created |

*Replace this changelog entry, and every placeholder fact above, with your
institution's real and current information before deploying this as a
production RAG source.*
