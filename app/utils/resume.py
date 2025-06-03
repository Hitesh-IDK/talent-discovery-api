from app.schemas.resume import ParsedResume
from pypdf import PageObject
from typing import List
from datetime import datetime

def extract_links(page: PageObject, resume: ParsedResume) -> ParsedResume:
    if "/Annots" in page:
        for annotation in page["/Annots"]:
            obj = annotation.get_object()
            subtype = obj["/Subtype"]
            link = obj["/A"]["/URI"]
            oldLink = link
            if link:
                if "linkedin.com" in link:
                    startIndex = link.index("linkedin.com") 
                    link = link[startIndex:]
                    link_subsets = [subset for subset in link.split('/') if len(subset.strip()) != 0]
                    if len(link_subsets) == 3:
                        resume.linkedin = link
                elif "github.com" in link:
                    startIndex = link.index("github.com")
                    link = link[startIndex:]
                    link_subsets = [subset for subset in link.split('/') if len(subset.strip()) != 0]
                    if len(link_subsets) == 2:
                        resume.github = link

    return resume

def getParseMessage(resume_content: str) -> List[str]:
    dateRules = """
        and start and end dates must be formatted into - 'MONTH YEAR' i.e for example 'June 2025'. If both start and end are not 
        mentioned and just one date is mentioned it can be assumed that the end date was provided and not the start
    """

    messages = []
    systemMessage = {
        "role": "system",
        "content": """You are a Data Analyst, Tasked with the objective to parse a resume into it equivalent columns in the SQL table. 
            You will be given the parsed resume content, extract all the data from the resume with the highest accuracy and generate the
            values for each of the sql columns based on the resume content and return the response in the form of python object.

            WARNING: YOU MUST STRICTLY FOLLOW THE EXACT DATA STRUCTURE AS MENTIONED BELOW
            
            The columns available are phone number, email, name, address,
            summary or overview of the user to be returned as summary in the response.
            And then the composite columns which are listed below,
            
            1. Work experience or experience related info to be named as experiences and returned in the response in the format such that for each 
            experience the title, summary or description of the experience to be named as the summary variable, time span when they 
            worked on it that should be named as the start and end date {dateRules}, the company or organization in which they gained the experience 
            to be returned as organization. The work experience may have projects under it with their own title, summary, start and end dates and such.
            Convert each project into a line and add it to the summary of the work experience, if start and end dates for the work experience is not 
            provided, use the start and end dates of these projects to identify the total start and end time of the work experience. No need of the
            projects object nested within the work experience. 
            
            2. Projects that the user has worked on to be named as projects and returned in the response in the format such that for each project 
            the title, summary or description of the project to be named as the summary variable, time span when they worked on it that should be 
            named as the start and end date {dateRules}, technologies used in this project to be named 
            as the technologies variable which should not include the programming languages, programming languages used to build this 
            project to be named as programming_languages variable which should not include technologies or tools used. If programming_languages or
            technlogies are not mentioned seperately, extract them from the summary if possible.
            
            3. Education that the user has undertaken to be named as educations and returned in the response in the format such that for each education
            the degree or grade for the education that was added to be named as the title variable and in case if, the name of the organization 
            where the education was pursued returned as the organization variable, time span when they 
            pursued the education that should be named as the start and end date {dateRules}, grade or cgpa or gpa achieved to be named as the 
            grade variable which if not provided can be empty, percentage achieved at the end of the education to be named as the percentage
            variable which can be empty if not provided or unable to calculate

            4. Technical Skills to be named as technical_skills and returned with a list of string string of all the technical skills or tools that the 
            user has mentioned in their resume. This should not include the programming languages.

            5. Programming languages to be named as programming_languages and returned with a list of string of all the programming languages that the user 
            has mentioned in their resume. This should not include the technical skills.

            6. Soft Skills to be named as soft_skills and returned with a list of string of all the soft skills that the user 
            has mentioned in their resume.

            7. Languages to be named as languages and returned with a list of string of all the languages that the user 
            has mentioned in their resume.

            8. Certifications to be named as certifications and returned in the response in the format such that for each certification the title 
            of the certification to named as the title variable, organization under which the certification was issued to be named as the organization 
            variable, end date at which the certification was completed and the certificate as issued to be named as the end_date which should be formatted
            into 'MONTH YEAR' i.e for example 'June 2025'.

            9. Total experience in the work experience which should not include internships which will be calculated based on the start and end dates of
            all the work experiences excluding the internships, the variable should be named as total_experience and the variable should be a floating number that counts based on the years
        """.format(dateRules=dateRules)
    }

    messages.append(systemMessage)

    userMessage = {
        "role": "user",
        "content": "Resume Content - \n\n" + resume_content
    }

    messages.append(userMessage)
    return messages