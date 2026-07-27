\# AI Misinformation Analysis System

\# API Contract v1.0





\## Endpoint



POST /api/analyze/





\## Pipeline



OCR

↓

Platform Detection

↓

NLP Analysis

↓

Fact Verification

↓

Engagement Extraction

↓

Spread Prediction

↓

Graph Generation

↓

Influence Detection

↓

React Flow Visualization





\---



\# Response Structure





{

&#x20; "status": "success",



&#x20; "analysis": {



&#x20;   "detection": {},



&#x20;   "fact\_verification": {},



&#x20;   "engagement": {},



&#x20;   "spread\_prediction": {},



&#x20;   "metadata": {}



&#x20; }

}





\---



\# NLP Detection





prediction labels:



\- Likely Reliable

\- Needs Verification

\- Potential Misinformation





Fields:



prediction

confidence

claim

content\_type

claim\_type

language

temporal\_context

risk\_level

entities

keywords

manipulation\_signals

similar\_claim





Entities format:



\[

&#x20; {

&#x20;   "name": "NASA",

&#x20;   "type": "Organization"

&#x20; }

]





\---



\# Fact Verification





verification\_status labels:



\- Verified Information

\- False Information

\- Misleading Information

\- Insufficient Evidence





Fields:



claim

verdict

reason

confidence

sources





\---



\# Engagement





Numeric fields must never be null.





Default values:



Numbers → 0



Arrays → \[]



Strings → "Unknown"





Fields:



likes

shares

comments

views

bookmarks

followers

platform\_metrics

detected\_signals





\---



\# Spread Prediction





Fields:



predicted\_reach

risk\_level

virality\_score





\---



\# Metadata





Example:



{

&#x20;"analysis\_id": "",

&#x20;"timestamp": "",

&#x20;"processing\_status": "completed"

}





\---



\# Integration Rules





1\. Do not rename fields without team discussion.



2\. Do not change JSON hierarchy.



3\. Maintain data types.



4\. Use default values instead of null.



5\. Graph Generation and React Flow modules consume this API directly.





Version:



API Contract v1.0

