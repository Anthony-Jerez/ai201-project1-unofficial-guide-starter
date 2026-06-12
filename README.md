# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

The Unofficial Guide centralizes raw student feedback, experiences, and workload expectations for Computer Science professors and courses at CUNY Queens College. While official university catalogs and websites give you basic course descriptions and instructor names, they completely miss out critical information, including exam difficulty, teaching quality, and student feedback. By making this data easily searchable, students will have access to knowledge that is difficult to find through official CUNY channels, which can help them better strategically pick their courses and professors.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
| --- | --- | --- | --- |
| 1 | RateMyProfessor | Condensed Review Data | documents/akinlar.txt |
| 2 | RateMyProfessor | Condensed Review Data | documents/chyn.txt |
| 3 | RateMyProfessor | Condensed Review Data | documents/gryak.txt |
| 4 | RateMyProfessor | Condensed Review Data | documents/kahrobaei.txt |
| 5 | RateMyProfessor | Condensed Review Data | documents/lord.txt |
| 6 | RateMyProfessor | Condensed Review Data | documents/obrenic.txt |
| 7 | RateMyProfessor | Condensed Review Data | documents/ryba.txt |
| 8 | RateMyProfessor | Condensed Review Data | documents/steinberg.txt |
| 9 | RateMyProfessor | Condensed Review Data | documents/telang.txt |
| 10 | RateMyProfessor | Condensed Review Data | documents/waxman.txt |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** Document-Structure-Based Chunks (variable size).

**Overlap:** No overlap.

**Why these choices fit your documents:**

Traditional fixed-size chunking techniques fail on our source documents because the text is not continuous. The data is highly structured and each student review is delimited by a `---` delimiter. Using arbitrary character limits could possibly split up a single review, seperating critical metadata such as ```Course``` or ```Review```. Also, we use no overlap because with overlap, it's possible that certain reviews can be mixed up where the end of one review is grabbed along with the start of another review.

Thus, it's best to use a document-structure-based chunking strategy, parsing each source document by the ```---``` delimiter so that one review equals one chunk. To ensure, no essential context is lost during the retrieval step, a preprocessing step is needed to extract the ```Professor Name``` from the top of each source document and prepend it to the text payload of each chunk. 

**Final chunk count:** 100

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2

**Production tradeoff reflection:**

While upgrading to a larger commerical embedding model (e.g. OpenAI's text-embedding-3-large model) would provide higher-dimensional vectors and thus capture more naunced sementic representations which would improve retrieval accuracy, this will also introduce network latency and token usage costs due to it requiring a external API call to access the model. The current embedding model runs locally, keeping retrieval latency near zero. Additionally, as mentioned before, each source document contains the latest 10 reviews in English for a certain professor, thus a larger context window and multilingual support would be unecessary at this current point.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

```bash
You are a helpful academic advisor assistant for Queens College students. 
Your ONLY job is to answer the user's question based STRICTLY on the context provided below.

RULES:
1. If the answer is not contained within the context above, you MUST explicitly say: "I don't have enough information on that based on the student reviews."
2. Do NOT use your general training knowledge to answer questions. 
3. Briefly cite the professor or source document in your answer when making claims.
```

**How system enforces grounding:**

The system prompt includes a set of guard rails that the LLM must adhere to ensure it strictly bases its answer only on the context provided. If it receives very low-relevance chunks, it's instructed to respond stating "I don't have enough information on that based on the student reviews." I also formatted the final context to include certain metadata (source) along with the retrieved context.

**How source attribution is surfaced in the response:**

Source attribution is handled in two layers. First, during the generation phase, the system prompt explicitly instructs the LLM to cite the source document inline. Second, during the retrieval phase, the application extracts the source filename from the metadata of the k=5 retrieved chunks, adds them to a unique Python set(), and displays them in a dedicated "Retrieved from" UI box in the Gradio interface.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Does Professor Jerry Waxman allow students to use electronics like phones or computers during his lectures?| No electronics allowed.| According to the reviews in waxman.txt, Professor Jerry Waxman does not allow students to use electronics like phones or computers during his lectures. One review states, "I was surprised we weren't allowed to use our computer or any electronics" (waxman.txt), and another review mentions that "if a phone was used, he would stop the lecture to address it" (waxman.txt).| Relevant| Accurate|
| 2 | What specific topics are covered on the exams for Bojana Obrenic's summer section of CSCI 320?| Exam 1: regex, Godel, DFA, NDFA, telescoping, CFG. Exam 2: Pumping Lemma, Turing Machines. Final: Cumulative.| According to the review from Aug 3rd, 2025, in the source document obrenic.txt, the specific topics covered on the exams for Bojana Obrenic's summer section of CSCI-320 are: Exam 1: regular expression, godel numbers, dfa, ndfa, telescoping, and cfg. Exam 2: Pump Lemma, Turing Machine, and exam 1 stuff. The final exam covers material from both exam 1 and 2. (Source: obrenic.txt, Aug 3rd, 2025 review)| Relevant| Accurate|
| 3 | How is the grade broken down in Delaram Kahrobaei's CSCI 220 class according to a student who took it in May 2026?| 40% midterm, 40% final, 10% hw.| According to a student review in kahrobaei.txt, the grade breakdown in Delaram Kahrobaei's CSCI 220 class is as follows: 40% midterm, 40% final, and 10% homework, as stated in the review dated May 29th, 2026. (Source: kahrobaei.txt)| Relevant| Accurate|
| 4 | What advice do students give to prepare for exams in Cuneyt Akinlar's introductory CSCI 111 course?| Attend the last lecture before the exam, do practice problems.| According to the reviews in akinlar.txt, students advise that to prepare for exams in Cuneyt Akinlar's introductory CSCI 111 course, one should "attend the lectures if you're new to CS--they're helpful!" and "just doing some of the practice problems will help you prepare for the exams." Additionally, it's recommended to "attend the last lecture before each exam--he tells you what specific topics are going to be tested." (Source: akinlar.txt)| Relevant| Accurate|
| 5 | What is a common student complaint regarding the formatting and presentation of Gaurish Telang's lecture slides?| Jams an impossible amount of information into one slide, highly disorganized.| According to the source document telang.txt, one student complaint is that Gaurish Telang "jams everything into one slide that is impossible to decipher if you miss a class" (Source: telang.txt, Review dated Apr 10th, 2025). This suggests that some students find his lecture slides to be overly dense and difficult to follow, particularly if they miss a class.| Relevant| Accurate|

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Can you list all the professors who teach CSCI 331?

**What the system returned:** Based on the context, there is only one professor mentioned who teaches CSCI 331: Cuneyt Akinlar (Source: akinlar.txt).

**Root cause (tied to a specific pipeline stage):**

This failure occurred during the Retrieval stage due to a strict Top-K cutoff limitation clashing with an aggregation query. Across our document sources, CSCI 331 is taught by at least five different professors (Akinlar, Chyn, Obrenic, Steinberg, and Telang). However, our ChromaDB retrieval function is hardcoded to return n_results=5. The vector store successfully found chunks mentioning "CSCI 331", but because it only returned 5 chunks total, it physically could not retrieve reviews for all five professors. The LLM was only fed a fragmented subset of the database, making it impossible to provide a comprehensive list.

**What you would change to fix it:**

To fix this, I would implement hybrid search logic. If the user's prompt triggers an aggregation keyword (like "List all" or "Who teaches"), the system would bypass standard semantic vector search and instead run a metadata filter search across the entire database, pulling the professor_name metadata from every chunk where the text contains the exact string "331", bypassing the k=5 limit.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

Defining a document-structure-based chunking strategy in the spec helped me develop a robust retrieval pipeline free from severe context fragmentation. Because I strictly defined splitting by the ```---``` markdown delimiter rather than using an arbitrary fixed character count, every single student review remained intact as a discrete chunk.

**One way your implementation diverged from the spec, and why:**

During Milestone 4, I realized that prepending the global statistics (e.g. "Avg Would take again: 47%") to the text payload of every single chunk used up additional redudant storage and contributed to heavily skewing the vector distances and causing inaccurate retrieval. I diverged from the spec by refactoring the ingestion script to extract those global statistics and inject them only into the ChromaDB metadata dictionary, keeping the text payload semantically focused on the student reviews themselves.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* I provided samples of my raw RateMyProfessor text files, which contained noisy info, and asked for a way to clean them during ingestion without leaving awkward double spaces or trailing spaces in the text.
- *What it produced:* It produced a regular expression ```re.compile(r"\\s*")```
- *What I changed or overrode:* While integrating the regex, I initially made the mistake of reducing the pattern to just r"\s*", which started deleting every single space and newline in my source documents. I had to debug the output and manually override it back to the AI's exact provided pattern.

**Instance 2**

- *What I gave the AI:* I provided my working ingest.py script containing one massive ingest_and_chunk function and asked for advice on whether ingestion and chunking should be separated instead of being all within a single function.
- *What it produced:* It recommended refactoring for the Single Responsibility Principle and produced a refined script with the original function I had created broken into load_and_clean_file, chunk_document, and process_all_docs functions.
- *What I changed or overrode:* I accepted the recommended structure but had to rewrite how my ```vector_store.py``` script interacted with the updated code in my ```ingest.py``` script. I overrode the old data pipeline by importing the new process_all_docs function and writing Python logic to inject chunk position tracking directly into the newly structured metadata dictionary.
