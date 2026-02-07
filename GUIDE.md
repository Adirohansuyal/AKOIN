# COREP Reporting Assistant Guide

This document explains what the COREP Reporting Assistant application does, the problem it solves, and how it works internally.

## What the App is Doing

The COREP Reporting Assistant is a web-based application that helps automate the process of filling out COREP (Common Reporting) regulatory reports. Users can provide a scenario in plain English, and the application will extract the relevant financial data, validate it against some basic rules, and present it in a format that is ready to be used in a COREP template.

## The Problem it Solves

COREP reporting is a mandatory and complex process for financial institutions in the European Union. It involves interpreting dense regulatory texts to find the correct data and report it in a standardized format. This process is often manual, time-consuming, and prone to human error. This application aims to reduce the manual effort and improve the accuracy of COREP reporting by leveraging a Large Language Model (LLM).

## How it Works Internally

The application is built as a FastAPI web server and follows a multi-step process to generate the reports:

1.  **API and Input:** The application exposes a `/report` endpoint that accepts a user's query as a string. This query describes a financial scenario.

2.  **Retrieval-Augmented Generation (RAG):**
    *   The application first uses a RAG engine to find the most relevant sections of the regulatory text for the given query.
    *   It uses the `sentence-transformers` library to create numerical representations (embeddings) of chunks of the regulatory text stored in `data/regulatory_text.txt`.
    *   These embeddings are stored in a `faiss` index, which allows for very fast similarity searches.
    *   When a user query is received, it is also converted into an embedding, and the `faiss` index is used to find the most similar text chunks from the regulatory document.

3.  **LLM-Powered Structured Data Generation:**
    *   The retrieved text chunks (the context) and the original user query are then sent to a powerful Large Language Model (Groq API with Llama 3.1).
    *   The LLM is given a specific set of instructions (a "system prompt") to act as a regulatory reporting assistant and to return the answer *only* in a structured JSON format.

4.  **Parsing and Validation:**
    *   The JSON output from the LLM is carefully parsed.
    *   The application then runs a series of validation rules on the extracted data. For example, it checks if certain capital components (like CET1) are negative or if the total Tier 1 capital is zero, flagging any inconsistencies.

5.  **Template Mapping:**
    *   The validated data is then mapped into a pandas DataFrame that is structured to look like an extract from a COREP template.

6.  **Final Output:** The application returns a JSON response to the user that includes:
    *   The structured data extracted by the LLM.
    *   The COREP template extract.
    *   An audit log containing the exact chunks of the regulatory text that were used to generate the report, providing transparency and allowing for verification.
