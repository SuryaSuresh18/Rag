This project demonstrates how to build **Agentic Workflows** using:
- **RAG Agent** (Retrieval-Augmented Generation) with FAISS as a vector database
- **WebSearch Agent** powered by DuckDuckGo
- **Supervisor Agent** that orchestrates multiple tools
- **Summarizer Tool** to combine outputs
- **Email Tool**  to send results


The framework is reusable — you can swap in new documents, add new tools, or adapt to different domains.


## 📚 Use Case: Child Mental Health Query
We ingested a medical PDF:
- [Primary Care Principles for Child Mental Health (MU)](https://medicine.missouri.edu/sites/default/files/psychiatry/21-0151BH_PrimaryCarePrinciplesforChildMentalHealthBooklet_FINAL%20(1).pdf)


### Example Queries
1. *“Child of age 12 is making careless mistakes in schoolwork and struggling to maintain attention. What mental health issue is this?”*
2. *“What type of doctor should treat this child?”*
3. *“Find a specialist in Mumbai 400001.”*

The Supervisor Agent:
- Asks the RAG Agent (PDF knowledge base)
- Uses DuckDuckGo for real-time info
- Summarizes both
- Sends the summary via email
